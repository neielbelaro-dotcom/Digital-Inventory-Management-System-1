import sqlite3
import hashlib
import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_dev_key")

# Database name from environment (fallback to inventory.db for dev)
DB_NAME = os.environ.get("DATABASE_NAME", "inventory.db")

# Database & Logic Classes
class DatabaseManager:
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
            cursor.execute("SELECT * FROM users WHERE username='admin'")
            if not cursor.fetchone():
                hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed_pw))
            conn.commit()

class UserAuth:
    def __init__(self, db_manager):
        self.db = db_manager

    def authenticate(self, username, password):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
            return cursor.fetchone() is not None

class InventoryManager:
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
                return False, f"Insufficient stock. Only {current_qty} left."
                
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
            
    def get_all_transactions(self, limit=50):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, p.name, t.type, t.quantity, t.date 
                FROM transactions t 
                JOIN products p ON t.product_id = p.id 
                ORDER BY t.date DESC LIMIT ?
            ''', (limit,))
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

db = DatabaseManager(DB_NAME)
user_auth = UserAuth(db)
inv_manager = InventoryManager(db)

# HTML Templates (embedded for simplicity in a single file)
BASE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Inventory System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='style.css') }}" rel="stylesheet">
</head>
<body>
    {% if session.get('logged_in') %}
    <div class="sidebar">
        <a class="navbar-brand" href="{{ url_for('dashboard') }}"><i class="fas fa-layer-group text-primary me-2"></i>Inventory <span style="font-weight: 300;">System</span></a>
        <a href="{{ url_for('dashboard') }}"><i class="fas fa-chart-pie me-3 w-20px"></i>Dashboard</a>
        <a href="{{ url_for('products') }}"><i class="fas fa-box-open me-3 w-20px"></i>Product Catalog</a>
        <a href="{{ url_for('transactions') }}"><i class="fas fa-exchange-alt me-3 w-20px"></i>Stock Movement</a>
        <div style="position: absolute; bottom: 30px; width: 100%;">
            <a href="{{ url_for('logout') }}"><i class="fas fa-sign-out-alt me-3"></i>Secure Logout</a>
        </div>
    </div>
    <div class="main-content">
    {% else %}
    <div class="login-container">
    {% endif %}

        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert glass-card mb-4 border-0 d-flex align-items-center" style="background: rgba({{ '16, 185, 129' if category == 'success' else '239, 68, 68' }}, 0.2); padding: 15px 20px;">
                  <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-circle' }} me-3" style="font-size: 1.5rem; color: {{ '#10b981' if category == 'success' else '#ef4444' }};"></i>
                  <div class="fw-bold">{{ message }}</div>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}

    </div>
</body>
</html>
'''

LOGIN_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', '''
<div class="glass-card login-box text-center">
    <h3 class="mb-2 fw-bold"><i class="fas fa-layer-group text-primary me-2"></i>Inventory <span style="font-weight: 300;">System</span></h3>
    <p class="text-muted mb-4 small text-uppercase" style="letter-spacing: 1px;">Inventory System</p>
    <form method="POST">
        <div class="mb-3 text-start">
            <label class="form-label text-light small fw-bold"><i class="fas fa-user text-muted me-2"></i>USERNAME</label>
            <input type="text" name="username" class="form-control form-control-lg" value="admin" required>
        </div>
        <div class="mb-4 text-start">
            <label class="form-label text-light small fw-bold"><i class="fas fa-lock text-muted me-2"></i>PASSWORD</label>
            <input type="password" name="password" class="form-control form-control-lg" value="admin123" required>
        </div>
        <button type="submit" class="btn btn-primary btn-lg w-100 fw-bold mt-2 shadow">Secure Sign In <i class="fas fa-arrow-right ms-2"></i></button>
    </form>
</div>
''')

DASHBOARD_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', '''
<h2 class="fw-bold mb-4">Dashboard Overview</h2>
<div class="row g-4">
    <div class="col-md-4">
        <div class="glass-card p-4 h-100 position-relative overflow-hidden" style="border-left: 4px solid #3b82f6;">
            <p class="text-light opacity-75 mb-1 text-uppercase fw-bold" style="letter-spacing: 1px; font-size: 0.85rem;">Total Products</p>
            <h1 class="fw-bold mb-0 display-5">{{ summary.total_products }}</h1>
            <i class="fas fa-box-open position-absolute" style="right: 20px; top: 50%; transform: translateY(-50%); font-size: 4rem; color: rgba(255,255,255,0.25);"></i>
        </div>
    </div>
    <div class="col-md-4">
        <div class="glass-card p-4 h-100 position-relative overflow-hidden" style="border-left: 4px solid #10b981;">
            <p class="text-light mb-1 text-uppercase fw-bold opacity-75" style="letter-spacing: 1px; font-size: 0.85rem;">Total Stock Volume</p>
            <h1 class="fw-bold mb-0 display-5">{{ summary.total_stock }}</h1>
            <i class="fas fa-pallet position-absolute" style="right: 20px; top: 50%; transform: translateY(-50%); font-size: 4rem; color: rgba(255,255,255,0.25);"></i>
        </div>
    </div>
    <div class="col-md-4">
        <div class="glass-card p-4 h-100 position-relative overflow-hidden" style="border-left: 4px solid #ef4444;">
            <p class="text-light mb-1 text-uppercase fw-bold opacity-75" style="letter-spacing: 1px; font-size: 0.85rem;">Critical Stock Alerts</p>
            <h1 class="fw-bold mb-0 text-danger display-5">{{ summary.low_stock }}</h1>
            <i class="fas fa-exclamation-triangle position-absolute" style="right: 20px; top: 50%; transform: translateY(-50%); font-size: 4rem; color: rgba(239,68,68,0.35);"></i>
        </div>
    </div>
</div>

<h4 class="mt-5 mb-3 fw-bold"><i class="fas fa-exclamation-circle text-danger me-2"></i>Items Requiring Restock</h4>
<div class="glass-card p-0 overflow-hidden">
    <table class="table table-hover table-striped mb-0">
        <thead class="table-dark" style="border-bottom: 2px solid rgba(255,255,255,0.1);">
            <tr><th class="ps-4">SKU ID</th><th>Product Name</th><th>Category</th><th>Current Qty</th><th>Min Threshold</th></tr>
        </thead>
        <tbody>
            {% for p in low_stock %}
            <tr>
                <td class="ps-4 text-light opacity-75">#{{ '%04d'|format(p[0]) }}</td>
                <td class="fw-bold">{{ p[1] }}</td>
                <td><span class="badge bg-secondary border border-light border-opacity-25">{{ p[2] }}</span></td>
                <td><span class="badge bg-danger rounded-pill px-3">{{ p[4] }}</span></td>
                <td class="text-light opacity-75">{{ p[5] }}</td>
            </tr>
            {% else %}
            <tr><td colspan="5" class="text-center py-5 text-muted"><i class="fas fa-check-circle text-success me-2" style="font-size: 1.5rem; vertical-align: middle;"></i><span style="vertical-align: middle;">All stock levels are optimal.</span></td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
''')

PRODUCTS_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', '''
<h2 class="fw-bold mb-4">Product Catalog</h2>
<div class="glass-card p-4 mb-4">
    <div class="row align-items-center">
        <div class="col-md-7">
            <form method="GET" class="d-flex">
                <div class="input-group shadow-sm">
                    <span class="input-group-text border-end-0"><i class="fas fa-search text-muted"></i></span>
                    <input type="text" name="search" class="form-control border-start-0 ps-0" placeholder="Search by name, category or SKU..." value="{{ search_term }}">
                    <button class="btn btn-primary px-4 fw-bold" type="submit">Search</button>
                    <a href="{{ url_for('products') }}" class="btn btn-outline-light">Reset</a>
                </div>
            </form>
        </div>
        <div class="col-md-5 text-end">
            <button class="btn btn-success fw-bold shadow" onclick="document.getElementById('addForm').style.display='block'"><i class="fas fa-plus me-2"></i>Add New Product</button>
        </div>
    </div>
</div>

<div id="addForm" class="glass-card p-4 mb-4 shadow-lg" style="display:none; border-left: 4px solid #10b981;">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h5 class="mb-0 fw-bold"><i class="fas fa-box-open me-2 text-success"></i>Register New Product</h5>
        <button class="btn-close btn-close-white" onclick="document.getElementById('addForm').style.display='none'"></button>
    </div>
    <form method="POST">
        <input type="hidden" name="action" value="add">
        <div class="row g-3">
            <div class="col-md-3"><label class="form-label text-light opacity-75 small text-uppercase fw-bold">Name</label><input type="text" name="name" class="form-control" required></div>
            <div class="col-md-2"><label class="form-label text-light opacity-75 small text-uppercase fw-bold">Category</label><input type="text" name="category" class="form-control" required></div>
            <div class="col-md-2"><label class="form-label text-light opacity-75 small text-uppercase fw-bold">Price ($)</label><input type="number" step="0.01" name="price" class="form-control" required></div>
            <div class="col-md-2"><label class="form-label text-light opacity-75 small text-uppercase fw-bold">Initial Qty</label><input type="number" name="quantity" class="form-control" required></div>
            <div class="col-md-2"><label class="form-label text-light opacity-75 small text-uppercase fw-bold">Min Stock</label><input type="number" name="min_stock" class="form-control" required></div>
            <div class="col-md-1 d-flex align-items-end"><button type="submit" class="btn btn-success w-100 fw-bold"><i class="fas fa-save me-1"></i>Save</button></div>
        </div>
    </form>
</div>

<div class="glass-card p-0 overflow-hidden shadow">
    <table class="table table-hover table-striped mb-0 align-middle">
        <thead class="table-dark" style="border-bottom: 2px solid rgba(255,255,255,0.1);">
            <tr><th class="ps-4 py-3">SKU ID</th><th class="py-3">Name</th><th class="py-3">Category</th><th class="py-3">Price</th><th class="py-3">Qty</th><th class="py-3">Min Stock</th><th class="text-end pe-4 py-3">Actions</th></tr>
        </thead>
        <tbody>
            {% for p in products %}
            <tr>
                <td class="ps-4 text-light opacity-75">#{{ '%04d'|format(p[0]) }}</td>
                <td class="fw-bold">{{ p[1] }}</td>
                <td><span class="badge bg-secondary border border-light border-opacity-25">{{ p[2] }}</span></td>
                <td>${{ p[3] }}</td>
                <td>
                    {% if p[4] <= p[5] %}
                    <span class="badge bg-danger rounded-pill px-2">{{ p[4] }}</span>
                    {% else %}
                    <span class="fw-bold">{{ p[4] }}</span>
                    {% endif %}
                </td>
                <td class="text-light opacity-75">{{ p[5] }}</td>
                <td class="text-end pe-4">
                    <form method="POST" class="d-inline" onsubmit="return confirm('Are you sure you want to delete {{ p[1] }}?');">
                        <input type="hidden" name="action" value="delete">
                        <input type="hidden" name="product_id" value="{{ p[0] }}">
                        <button type="submit" class="btn btn-sm btn-outline-danger" title="Delete Product"><i class="fas fa-trash-alt"></i></button>
                    </form>
                </td>
            </tr>
            {% else %}
            <tr><td colspan="7" class="text-center py-5 text-muted">No products found.</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
''')

TRANSACTIONS_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', '''
<h2 class="fw-bold mb-4">Stock Movement</h2>
<div class="row g-4 mb-4">
    <div class="col-lg-4">
        <div class="glass-card p-4 h-100 shadow">
            <h5 class="fw-bold mb-4 text-primary"><i class="fas fa-exchange-alt me-2"></i>Log Transaction</h5>
            <form method="POST">
                <div class="mb-4">
                    <label class="form-label text-light opacity-75 small text-uppercase fw-bold">Product SKU ID</label>
                    <input type="number" name="product_id" class="form-control form-control-lg" placeholder="e.g. 1" required>
                </div>
                <div class="mb-4">
                    <label class="form-label text-light opacity-75 small text-uppercase fw-bold">Transaction Type</label>
                    <select name="trans_type" class="form-select form-select-lg" required>
                        <option value="IN">📥 Stock IN (Receive)</option>
                        <option value="OUT">📤 Stock OUT (Dispatch)</option>
                    </select>
                </div>
                <div class="mb-5">
                    <label class="form-label text-light opacity-75 small text-uppercase fw-bold">Quantity</label>
                    <input type="number" name="quantity" min="1" class="form-control form-control-lg" placeholder="Amount" required>
                </div>
                <button type="submit" class="btn btn-primary btn-lg w-100 fw-bold shadow"><i class="fas fa-check-circle me-2"></i>Execute</button>
            </form>
        </div>
    </div>

    <div class="col-lg-8">
        <div class="glass-card p-0 overflow-hidden h-100 d-flex flex-column shadow">
            <div class="p-4 border-bottom" style="border-color: rgba(255,255,255,0.1) !important; background: rgba(15,23,42,0.5);">
                <h5 class="fw-bold mb-0"><i class="fas fa-history me-2 text-muted"></i>Recent Activity Log</h5>
            </div>
            <div class="table-responsive flex-grow-1" style="max-height: 550px; overflow-y: auto;">
                <table class="table table-hover table-striped mb-0 align-middle">
                    <thead class="table-dark" style="position: sticky; top: 0; z-index: 1;">
                        <tr><th class="ps-4 py-3">Log ID</th><th class="py-3">Product Name</th><th class="py-3">Type</th><th class="py-3">Qty</th><th class="py-3 text-end pe-4">Timestamp</th></tr>
                    </thead>
                    <tbody>
                        {% for t in logs %}
                        <tr>
                            <td class="ps-4 text-light opacity-75">#{{ '%06d'|format(t[0]) }}</td>
                            <td class="fw-bold">{{ t[1] }}</td>
                            <td>
                                {% if t[2] == 'IN' %}
                                <span class="badge bg-success bg-opacity-75 rounded-pill px-3 py-2 border border-success"><i class="fas fa-arrow-down me-1"></i> IN</span>
                                {% else %}
                                <span class="badge bg-warning text-dark bg-opacity-75 rounded-pill px-3 py-2 border border-warning"><i class="fas fa-arrow-up me-1"></i> OUT</span>
                                {% endif %}
                            </td>
                            <td class="fw-bold fs-5">{{ t[3] }}</td>
                            <td class="text-light opacity-75 small text-end pe-4">{{ t[4] }}</td>
                        </tr>
                        {% else %}
                        <tr><td colspan="5" class="text-center py-5 text-muted">No transactions logged yet.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
''')

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user_auth.authenticate(user, pwd):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    summary = inv_manager.get_summary()
    low_stock = inv_manager.get_low_stock_products()
    return render_template_string(DASHBOARD_HTML, summary=summary, low_stock=low_stock)

@app.route('/products', methods=['GET', 'POST'])
def products():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            try:
                inv_manager.add_product(
                    request.form.get('name'), request.form.get('category'),
                    float(request.form.get('price')), int(request.form.get('quantity')),
                    int(request.form.get('min_stock'))
                )
                flash('Product added successfully', 'success')
            except ValueError:
                flash('Invalid input data', 'danger')
        elif action == 'delete':
            inv_manager.delete_product(request.form.get('product_id'))
            flash('Product deleted', 'success')
        return redirect(url_for('products'))
        
    search_term = request.args.get('search', '')
    product_list = inv_manager.get_all_products(search_term)
    return render_template_string(PRODUCTS_HTML, products=product_list, search_term=search_term)

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            pid = int(request.form.get('product_id'))
            ttype = request.form.get('trans_type')
            qty = int(request.form.get('quantity'))
            success, msg = inv_manager.stock_transaction(pid, ttype, qty)
            if success:
                flash(msg, 'success')
            else:
                flash(msg, 'danger')
        except ValueError:
            flash('Invalid input', 'danger')
        return redirect(url_for('transactions'))
        
    recent_logs = inv_manager.get_all_transactions(100) # fetch last 100 logs
    return render_template_string(TRANSACTIONS_HTML, logs=recent_logs)

if __name__ == '__main__':
    # Parse FLASK_DEBUG safely from string
    is_debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    
    # Do not blindly allow debug True in production without explicit env flag
    app.run(debug=is_debug, port=5000)
