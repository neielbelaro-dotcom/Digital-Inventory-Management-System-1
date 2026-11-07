import sqlite3
import random

def seed_critical_stocks():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    categories = ["Electronics", "Components", "Hardware", "Packaging", "Raw Materials"]
    
    for i in range(1, 105):
        name = f"Critical Item {i}"
        cat = random.choice(categories)
        price = round(random.uniform(1.0, 100.0), 2)
        # To be critical: quantity <= min_stock
        min_stock = random.randint(20, 50)
        qty = random.randint(0, min_stock) # less than or equal to min_stock
        
        cursor.execute("INSERT INTO products (name, category, price, quantity, min_stock) VALUES (?, ?, ?, ?, ?)",
                       (name, cat, price, qty, min_stock))

    conn.commit()
    conn.close()
    print("Successfully added 100+ critical stock products to the database.")

if __name__ == "__main__":
    seed_critical_stocks()
