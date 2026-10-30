import sqlite3, os

DB = os.path.join('instance', 'shop.db')
os.makedirs('instance', exist_ok=True)

con = sqlite3.connect(DB)

# 1. Принудительно создаем таблицы, если их нет
con.executescript("""
CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, price INTEGER, image TEXT, category TEXT, is_active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS product_sizes (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, size TEXT, stock INTEGER DEFAULT 10);
""")

# 2. Очищаем старые данные (чтобы не было дублей)
con.execute("DELETE FROM products")
con.execute("DELETE FROM product_sizes")

desc_tshirt = "Базовая футболка из мягкого хлопка с уникальным кастомным рисунком. Спокойный силуэт, не сковывает движения, а принт добавляет индивидуальности без кричащих деталей. Отлично смотрится и с джинсами, и с карго, и со спортивными штанами. Рисунок нанесён стойкой краской — сохраняет цвет после множества стирок."
desc_bag = "Шоппер с авторским кастомным рисунком — это не просто аксессуар, а маленькая история на ткани. Каждый элемент принта продуман и несёт свой смысл. Плотный материал и надёжные ручки выдерживают повседневную нагрузку."

# 3. Твои товары
demo = [
    ("Шоппер Classic", desc_bag, 700, "Bag/Bag-1.jpg", "accessories"),
    ("Шоппер Tatar", desc_bag, 700, "Bag/Bag-2.jpg", "accessories"),
    ("Шоппер Black", desc_bag, 700, "Bag/Bag-3.jpg", "accessories"),
    ("Шоппер Canvas", desc_bag, 700, "Bag/Bag-4.jpg", "accessories"),
    ("Шоппер Street", desc_bag, 700, "Bag/Bag-5.jpg", "accessories"),
    ("Футболка Oversize", desc_tshirt, 1700, "Tshirt/TShirt-1.jpg", "tshirts"),
    ("Футболка Tatar", desc_tshirt, 1700, "Tshirt/TShirt2-1.jpg", "tshirts"),
    ("Футболка Basic", desc_tshirt, 1700, "Tshirt/TShirt3-1.jpg", "tshirts"),
    ("Футболка Black", desc_tshirt, 1700, "Tshirt/TShirt4-1.jpg", "tshirts"),
]

for title, desc, price, img, cat in demo:
    cur = con.execute("INSERT INTO products (title, description, price, image, category) VALUES (?, ?, ?, ?, ?)", (title, desc, price, img, cat))
    pid = cur.lastrowid
    for size in ['S', 'M', 'L', 'XL']:
        con.execute("INSERT INTO product_sizes (product_id, size) VALUES (?, ?)", (pid, size))

con.commit()
con.close()
print("✅ БАЗА ЗАПОЛНЕНА! Все товары с ценами и описаниями на месте.")