import sqlite3
import random
from datetime import datetime, timedelta

def seed_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # Create dummy products if none or few exist
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    
    product_ids = []
    if count < 10:
        categories = ["Electronics", "Office Supplies", "Furniture", "Cleaning", "Hardware", "Peripherals"]
        for i in range(1, 51):
            name = f"Sample Product {i}"
            cat = random.choice(categories)
            price = round(random.uniform(5.0, 999.99), 2)
            qty = random.randint(20, 200)
            min_stock = random.randint(5, 30)
            
            cursor.execute("INSERT INTO products (name, category, price, quantity, min_stock) VALUES (?, ?, ?, ?, ?)",
                           (name, cat, price, qty, min_stock))
            product_ids.append(cursor.lastrowid)
    else:
        cursor.execute("SELECT id FROM products")
        product_ids = [row[0] for row in cursor.fetchall()]

    # Generate 450 random stock transactions (logs)
    start_date = datetime.now() - timedelta(days=180)
    
    for _ in range(450):
        pid = random.choice(product_ids)
        ttype = random.choice(["IN", "OUT", "OUT", "OUT"]) # slightly more OUTs to simulate sales
        qty = random.randint(1, 20)
        
        # Random date within the last 6 months
        random_days = random.randint(0, 180)
        random_seconds = random.randint(0, 86400)
        t_date = start_date + timedelta(days=random_days, seconds=random_seconds)
        date_str = t_date.strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("INSERT INTO transactions (product_id, type, quantity, date) VALUES (?, ?, ?, ?)",
                       (pid, ttype, qty, date_str))

    conn.commit()
    conn.close()
    print("Successfully added 450+ transaction logs and sample products to the database.")

if __name__ == "__main__":
    seed_db()
