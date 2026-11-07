import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
from datetime import datetime

class DatabaseManager:
    """Handles all SQLite database connections and table creation."""
    def __init__(self, db_name="inventory.db"):
        self.db_name = db_name
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              username TEXT UNIQUE NOT NULL,
                              password TEXT NOT NULL
                              )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              name TEXT NOT NULL,
                              category TEXT NOT NULL,
                              price REAL NOT NULL,
                              quantity INTEGER NOT NULL,
                              min_stock INTEGER NOT NULL
                              )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              product_id INTEGER,
                              type TEXT NOT NULL,
                              quantity INTEGER NOT NULL,
                              date TEXT NOT NULL,
                              FOREIGN KEY (product_id) REFERENCES products(id)
                              )''')
            # Add default admin user if not exists
            cursor.execute("SELECT * FROM users WHERE username='admin'")
            if not cursor.fetchone():
                hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed_pw))
            conn.commit()

class UserAuth:
    """Handles User Authentication."""
    def __init__(self, db_manager):
        self.db = db_manager

    def authenticate(self, username, password):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
            return cursor.fetchone() is not None

class InventoryManager:
    """Handles business logic for the Inventory System."""
    def __init__(self, db_manager):
        self.db = db_manager

    def add_product(self, name, category, price, quantity, min_stock):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, category, price, quantity, min_stock) VALUES (?, ?, ?, ?, ?)",
                           (name, category, price, quantity, min_stock))
            conn.commit()

    def update_product(self, product_id, name, category, price, quantity, min_stock):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET name=?, category=?, price=?, quantity=?, min_stock=? WHERE id=?",
                           (name, category, price, quantity, min_stock, product_id))
            conn.commit()

    def delete_product(self, product_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            cursor.execute("DELETE FROM transactions WHERE product_id=?", (product_id,))
            conn.commit()

    def get_all_products(self, search_term=""):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            if search_term:
                query = f"%{search_term}%"
                cursor.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ? OR id LIKE ?", (query, query, query))
            else:
                cursor.execute("SELECT * FROM products")
            return cursor.fetchall()

    def get_product_by_id(self, product_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
            return cursor.fetchone()

    def stock_transaction(self, product_id, trans_type, qty):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            product = self.get_product_by_id(product_id)
            if not product:
                return False, "Product not found."
            
            current_qty = product[4]
            if trans_type == "OUT" and current_qty < qty:
                return False, "Insufficient stock."
                
            new_qty = current_qty + qty if trans_type == "IN" else current_qty - qty
            
            cursor.execute("UPDATE products SET quantity=? WHERE id=?", (new_qty, product_id))
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO transactions (product_id, type, quantity, date) VALUES (?, ?, ?, ?)",
                           (product_id, trans_type, qty, date_str))
            conn.commit()
            return True, "Transaction successful."

    def get_low_stock_products(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE quantity <= min_stock")
            return cursor.fetchall()
            
    def get_summary(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(quantity) FROM products")
            total_stock = cursor.fetchone()[0] or 0
            
            low_stock = len(self.get_low_stock_products())
            return {"total_products": total_products, "total_stock": total_stock, "low_stock": low_stock}

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.db = DatabaseManager()
        self.user_auth = UserAuth(self.db)
        
        self.root.title("Login - Inventory System")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        
        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Username:").grid(row=0, column=0, pady=10, sticky="e")
        self.entry_user = ttk.Entry(frame, width=20)
        self.entry_user.grid(row=0, column=1, pady=10)
        self.entry_user.insert(0, "admin") # default for demo
        
        ttk.Label(frame, text="Password:").grid(row=1, column=0, pady=10, sticky="e")
        self.entry_pass = ttk.Entry(frame, show="*", width=20)
        self.entry_pass.grid(row=1, column=1, pady=10)
        self.entry_pass.insert(0, "admin123") # default for demo
        
        ttk.Button(frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=20)
        
    def login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        
        if self.user_auth.authenticate(user, pwd):
            self.root.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Invalid username or password")


class DashboardWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Digital Inventory Management System")
        self.root.geometry("900x650")
        
        self.db = DatabaseManager()
        self.manager = InventoryManager(self.db)
        
        self.create_widgets()
        self.refresh_data()
        
    def create_widgets(self):
        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Dashboard Tab
        self.tab_dash = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dash, text="Dashboard")
        self.setup_dashboard_tab()
        
        # Products Tab
        self.tab_prod = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_prod, text="Manage Products")
        self.setup_products_tab()
        
        # Transactions Tab
        self.tab_trans = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_trans, text="Stock In/Out")
        self.setup_transactions_tab()

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_data())
        
    def setup_dashboard_tab(self):
        frame_stats = ttk.LabelFrame(self.tab_dash, text="Overview", padding=20)
        frame_stats.pack(fill="x", padx=20, pady=20)

        self.lbl_total_prod = ttk.Label(frame_stats, text="Total Products: 0", font=("Helvetica", 14))
        self.lbl_total_prod.grid(row=0, column=0, padx=40, pady=10)
        
        self.lbl_total_stock = ttk.Label(frame_stats, text="Total Stock: 0", font=("Helvetica", 14))
        self.lbl_total_stock.grid(row=0, column=1, padx=40, pady=10)
        
        self.lbl_low_stock = ttk.Label(frame_stats, text="Low Stock Items: 0", font=("Helvetica", 14, "bold"), foreground="red")
        self.lbl_low_stock.grid(row=0, column=2, padx=40, pady=10)

        frame_low = ttk.LabelFrame(self.tab_dash, text="Low Stock Alerts", padding=10)
        frame_low.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ID", "Name", "Qty", "Min Stock")
        self.tree_low = ttk.Treeview(frame_low, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree_low.heading(col, text=col)
            self.tree_low.column(col, width=150, anchor="center")
        self.tree_low.pack(pady=5, fill="both", expand=True)
        
    def setup_products_tab(self):
        frame_top = ttk.Frame(self.tab_prod)
        frame_top.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame_top, text="Search:").pack(side="left")
        self.entry_search = ttk.Entry(frame_top, width=30)
        self.entry_search.pack(side="left", padx=5)
        ttk.Button(frame_top, text="Search", command=self.load_products).pack(side="left", padx=5)
        ttk.Button(frame_top, text="Clear", command=lambda: (self.entry_search.delete(0, tk.END), self.load_products())).pack(side="left")
        
        columns = ("ID", "Name", "Category", "Price", "Qty", "Min Stock")
        self.tree_prod = ttk.Treeview(self.tab_prod, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_prod.heading(col, text=col)
            self.tree_prod.column(col, width=120, anchor="center")
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=5)
        
        frame_btn = ttk.Frame(self.tab_prod)
        frame_btn.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(frame_btn, text="Add Product", command=self.open_add_window).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="Edit Product", command=self.open_edit_window).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="Delete Product", command=self.delete_product).pack(side="left", padx=5)
        
    def setup_transactions_tab(self):
        frame = ttk.LabelFrame(self.tab_trans, text="Process Transaction", padding=30)
        frame.pack(pady=40)
        
        ttk.Label(frame, text="Product ID:").grid(row=0, column=0, pady=10, sticky="e")
        self.trans_prod_id = ttk.Entry(frame, width=20)
        self.trans_prod_id.grid(row=0, column=1, pady=10)
        
        ttk.Label(frame, text="Quantity:").grid(row=1, column=0, pady=10, sticky="e")
        self.trans_qty = ttk.Entry(frame, width=20)
        self.trans_qty.grid(row=1, column=1, pady=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Stock In (+)", command=lambda: self.process_transaction("IN")).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Stock Out (-)", command=lambda: self.process_transaction("OUT")).pack(side="left", padx=10)
        
    def refresh_data(self):
        summary = self.manager.get_summary()
        self.lbl_total_prod.config(text=f"Total Products: {summary['total_products']}")
        self.lbl_total_stock.config(text=f"Total Stock: {summary['total_stock']}")
        self.lbl_low_stock.config(text=f"Low Stock Items: {summary['low_stock']}")
        
        # Reload low stock tree
        for item in self.tree_low.get_children():
            self.tree_low.delete(item)
        for p in self.manager.get_low_stock_products():
            self.tree_low.insert("", "end", values=(p[0], p[1], p[4], p[5]))
            
        self.load_products()
        
    def load_products(self):
        term = self.entry_search.get() if hasattr(self, 'entry_search') else ""
        for item in self.tree_prod.get_children():
            self.tree_prod.delete(item)
        for p in self.manager.get_all_products(term):
            self.tree_prod.insert("", "end", values=p)
            
    def process_transaction(self, trans_type):
        try:
            pid = int(self.trans_prod_id.get())
            qty = int(self.trans_qty.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid Product ID or Quantity")
            return
            
        success, msg = self.manager.stock_transaction(pid, trans_type, qty)
        if success:
            messagebox.showinfo("Success", msg)
            self.trans_prod_id.delete(0, tk.END)
            self.trans_qty.delete(0, tk.END)
            self.refresh_data()
        else:
            messagebox.showerror("Error", msg)
            
    def open_add_window(self):
        self.ProductWindow(self, "Add Product")
        
    def open_edit_window(self):
        selected = self.tree_prod.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to edit")
            return
        item = self.tree_prod.item(selected[0])['values']
        self.ProductWindow(self, "Edit Product", item)
        
    def delete_product(self):
        selected = self.tree_prod.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to delete")
            return
        item = self.tree_prod.item(selected[0])['values']
        if messagebox.askyesno("Confirm", f"Delete product '{item[1]}' (ID: {item[0]})?"):
            self.manager.delete_product(item[0])
            self.refresh_data()

    class ProductWindow:
        def __init__(self, parent, title, product_data=None):
            self.parent = parent
            self.product_data = product_data
            
            self.top = tk.Toplevel(parent.root)
            self.top.title(title)
            self.top.geometry("350x350")
            
            frame = ttk.Frame(self.top, padding=20)
            frame.pack(expand=True, fill="both")
            
            labels = ["Name:", "Category:", "Price:", "Quantity:", "Min Stock:"]
            self.entries = {}
            for i, label in enumerate(labels):
                ttk.Label(frame, text=label).grid(row=i, column=0, pady=10, sticky="e")
                ent = ttk.Entry(frame, width=25)
                ent.grid(row=i, column=1, pady=10)
                self.entries[label] = ent
                
            if product_data:
                self.entries["Name:"].insert(0, product_data[1])
                self.entries["Category:"].insert(0, product_data[2])
                self.entries["Price:"].insert(0, product_data[3])
                self.entries["Quantity:"].insert(0, product_data[4])
                self.entries["Min Stock:"].insert(0, product_data[5])
                
            ttk.Button(frame, text="Save", command=self.save).grid(row=len(labels), column=0, columnspan=2, pady=20)
            
        def save(self):
            try:
                name = self.entries["Name:"].get()
                cat = self.entries["Category:"].get()
                price = float(self.entries["Price:"].get())
                qty = int(self.entries["Quantity:"].get())
                min_s = int(self.entries["Min Stock:"].get())
                if not name or not cat:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid input data. Ensure numbers for price, qty, min stock.")
                return
                
            if self.product_data:
                self.parent.manager.update_product(self.product_data[0], name, cat, price, qty, min_s)
            else:
                self.parent.manager.add_product(name, cat, price, qty, min_s)
                
            self.parent.refresh_data()
            self.top.destroy()
            
    def run(self):
        self.root.mainloop()

def start_app():
    app = DashboardWindow()
    app.run()

if __name__ == "__main__":
    root = tk.Tk()
    login = LoginWindow(root, start_app)
    root.mainloop()
