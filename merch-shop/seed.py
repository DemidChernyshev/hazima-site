import sqlite3, os

DB = os.path.join('instance', 'shop.db')
os.makedirs('instance', exist_ok=True)

con = sqlite3.connect(DB)
con.execute("PRAGMA foreign_keys = ON")

# Создаем 4 пустые карточки (категории и картинки)
demo = [
    ("Название товара", "", 0, "1.jpg"),
    ("Название товара", "", 0, "2.jpg"),
    ("Название товара", "", 0, "3.jpg"),
    ("Название товара", "", 0, "4.jpg"),
]

for title, desc, price, img in demo:
    cur = con.execute("INSERT INTO products (title, description, price, image) VALUES (?, ?, ?, ?)", (title, desc, price, img))
    pid = cur.lastrowid
    for size in ['S', 'M', 'L', 'XL']:
        con.execute("INSERT INTO product_sizes (product_id, size, stock) VALUES (?, ?, 10)", (pid, size))

con.commit()
con.close()
print("✅ База создана, карточки добавлены")