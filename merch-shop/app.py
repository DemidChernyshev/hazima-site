import os
from flask import Flask, render_template, session, request, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from db import init_app as init_db_app, get_db, init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-hozha'
app.config['DATABASE'] = os.path.join(app.instance_path, 'shop.db')

os.makedirs(app.instance_path, exist_ok=True)
init_db_app(app)


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('✅ БД инициализирована')


# Декоратор для защиты админки
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Доступ только для администратора', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# ---------- КАТАЛОГ ----------
@app.route('/')
def index():
    db = get_db()
    products = db.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY id DESC").fetchall()
    return render_template('index.html', products=products)


# ---------- ТОВАР ----------
@app.route('/product/<int:pid>')
def product(pid):
    db = get_db()
    p = db.execute("SELECT * FROM products WHERE id = ? AND is_active = 1", (pid,)).fetchone()
    if not p: abort(404)
    sizes = db.execute("SELECT * FROM product_sizes WHERE product_id = ?", (pid,)).fetchall()
    return render_template('product.html', product=p, sizes=sizes)


# ---------- КОРЗИНА ----------
def get_cart():
    return session.setdefault('cart', [])


@app.route('/cart/add/<int:pid>', methods=['POST'])
def cart_add(pid):
    size = request.form.get('size', 'M')
    qty = int(request.form.get('qty', 1))
    cart = get_cart()
    for item in cart:
        if item['pid'] == pid and item['size'] == size:
            item['qty'] += qty
            break
    else:
        cart.append({'pid': pid, 'size': size, 'qty': qty})
    session['cart'] = cart
    session.modified = True
    flash('Товар добавлен в корзину', 'success')
    return redirect(url_for('cart_view'))


@app.route('/cart')
def cart_view():
    db = get_db()
    cart = get_cart()
    items, total = [], 0
    for it in cart:
        p = db.execute("SELECT * FROM products WHERE id = ?", (it['pid'],)).fetchone()
        if p:
            line = p['price'] * it['qty']
            total += line
            items.append({'product': p, 'size': it['size'], 'qty': it['qty'], 'line_total': line})
    return render_template('cart.html', items=items, total=total)


@app.route('/cart/remove/<int:idx>', methods=['POST'])
def cart_remove(idx):
    cart = get_cart()
    if 0 <= idx < len(cart):
        cart.pop(idx)
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('cart_view'))


# ---------- ОФОРМЛЕНИЕ ----------
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    db = get_db()
    cart = get_cart()
    if not cart: return redirect(url_for('index'))

    items, total = [], 0
    for it in cart:
        p = db.execute("SELECT * FROM products WHERE id = ?", (it['pid'],)).fetchone()
        if p:
            line = p['price'] * it['qty']
            total += line
            items.append({'product': p, 'size': it['size'], 'qty': it['qty'], 'price': p['price']})

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')

        cur = db.execute("INSERT INTO orders (user_id, customer_name, phone, address, total) VALUES (?, ?, ?, ?, ?)",
                         (session.get('user_id'), name, phone, address, total))
        order_id = cur.lastrowid
        for it in items:
            db.execute("INSERT INTO order_items (order_id, product_id, size, qty, price) VALUES (?, ?, ?, ?, ?)",
                       (order_id, it['product']['id'], it['size'], it['qty'], it['price']))
        db.commit()
        session['cart'] = []
        return render_template('checkout.html', success=True, order_id=order_id)

    return render_template('checkout.html', items=items, total=total)


# ---------- АВТОРИЗАЦИЯ ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        if db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
            flash('Логин занят', 'error')
        else:
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                       (username, generate_password_hash(password)))
            db.commit()
            flash('Аккаунт создан!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash('С возвращением!', 'success')
            return redirect(url_for('profile'))
        flash('Неверный логин или пароль', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли', 'success')
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    orders = db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (session['user_id'],)).fetchall()
    return render_template('profile.html', orders=orders)


# ---------- АДМИНКА ----------
@app.route('/admin')
@admin_required
def admin_panel():
    db = get_db()
    products = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    orders = db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    return render_template('admin.html', products=products, orders=orders)


@app.route('/admin/add_product', methods=['POST'])
@admin_required
def admin_add_product():
    title = request.form.get('title')
    price = int(request.form.get('price', 0))
    img = request.form.get('image', '1.jpg')
    desc = request.form.get('description', '')
    cat = request.form.get('category', 'tshirts')

    db = get_db()
    cur = db.execute("INSERT INTO products (title, description, price, image, category) VALUES (?, ?, ?, ?, ?)",
                     (title, desc, price, img, cat))
    pid = cur.lastrowid
    for size in ['S', 'M', 'L', 'XL']:
        db.execute("INSERT INTO product_sizes (product_id, size) VALUES (?, ?)", (pid, size))
    db.commit()
    flash('Товар добавлен!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/ping')
def ping(): return {'status': 'ok'}, 200


if __name__ == '__main__':
    app.run(debug=True)