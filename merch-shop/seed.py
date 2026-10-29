import sqlite3, os

DB = os.path.join('instance', 'shop.db')
os.makedirs('instance', exist_ok=True)

con = sqlite3.connect(DB)
con.execute("PRAGMA foreign_keys = ON")

demo = [
    ("Vibe Oversize", "Чёрная оверсайз-футболка с минималистичным принтом. 100% хлопок 240 г/м².", 2900, "1.jpg", [("S",5),("M",10),("L",8),("XL",4)]),
    ("No Logo Black", "Классика без принта. Идеальная база под всё.", 1900, "2.jpg", [("M",12),("L",9),("XL",3)]),
    ("Static Noise", "Принт с текстурой шума. Лимитированный дроп 50 штук.", 3200, "3.jpg", [("S",3),("M",6),("L",4)]),
    ("Mono White", "Белая футболка со строчным логотипом на груди.", 2200, "4.jpg", [("S",7),("M",11),("L",9),("XL",5)]),
]

for title, desc, price, img, sizes in demo:
    cur = con.execute(
        "INSERT INTO products (title, description, price, image) VALUES (?, ?, ?, ?)",
        (title, desc, price, img)
    )
    pid = cur.lastrowid
    for size, stock in sizes:
        con.execute(
            "INSERT INTO product_sizes (product_id, size, stock) VALUES (?, ?, ?)",
            (pid, size, stock)
        )

con.commit()
con.close()
print("✅ Демо-товары добавлены")