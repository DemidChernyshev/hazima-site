import os
from flask import Flask, render_template, session, request, redirect, url_for, flash
from db import init_app as init_db_app, get_db, init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['DATABASE'] = os.path.join(app.instance_path, 'shop.db')

os.makedirs(app.instance_path, exist_ok=True)
init_db_app(app)

@app.cli.command('initdb')
def initdb_command():
    """Flask initdb — создаёт таблицы."""
    init_db()
    print('✅ БД инициализирована')

# ---------- РОУТЫ ----------
@app.route('/')
def index():
    db = get_db()
    products = db.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY id DESC").fetchall()
    return render_template('index.html', products=products)

@app.route('/product/<int:pid>')
def product(pid):
    db = get_db()
    p = db.execute("SELECT * FROM products WHERE id = ? AND is_active = 1", (pid,)).fetchone()
    if not p:
        return "Товар не найден", 404
    sizes = db.execute("SELECT * FROM product_sizes WHERE product_id = ? AND stock > 0", (pid,)).fetchall()
    return render_template('product.html', product=p, sizes=sizes)

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

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    db = get_db()
    cart = get_cart()
    if not cart:
        return redirect(url_for('index'))

    items, total = [], 0
    for it in cart:
        p = db.execute("SELECT * FROM products WHERE id = ?", (it['pid'],)).fetchone()
        if p:
            line = p['price'] * it['qty']
            total += line
            items.append({'product': p, 'size': it['size'], 'qty': it['qty'], 'price': p['price']})

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        tg = request.form.get('telegram', '').strip()
        address = request.form.get('address', '').strip()

        if not (name and phone and address):
            flash('Заполни имя, телефон и адрес', 'error')
            return render_template('checkout.html', items=items, total=total)

        cur = db.execute(
            "INSERT INTO orders (customer_name, phone, telegram, address, total) VALUES (?, ?, ?, ?, ?)",
            (name, phone, tg, address, total)
        )
        order_id = cur.lastrowid
        for it in items:
            db.execute(
                "INSERT INTO order_items (order_id, product_id, size, qty, price) VALUES (?, ?, ?, ?, ?)",
                (order_id, it['product']['id'], it['size'], it['qty'], it['price'])
            )
        db.commit()

        session['cart'] = []
        session.modified = True
        return render_template('checkout.html', success=True, order_id=order_id)

    return render_template('checkout.html', items=items, total=total)

# ---------- ПИНГ ДЛЯ RENDER ----------
@app.route('/ping')
def ping():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(debug=True)