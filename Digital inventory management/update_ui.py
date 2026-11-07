import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The new HTML blocks
new_base = """BASE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Enterprise Inventory Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80') no-repeat center center fixed;
            background-size: cover;
            color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            margin: 0;
            overflow-x: hidden;
        }
        .sidebar {
            height: 100vh;
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255,255,255,0.05);
            position: fixed;
            top: 0;
            left: 0;
            width: 260px;
            padding-top: 30px;
            z-index: 1000;
        }
        .sidebar a {
            padding: 15px 30px;
            text-decoration: none;
            font-size: 16px;
            color: #94a3b8;
            display: block;
            transition: 0.3s;
            border-left: 4px solid transparent;
            font-weight: 500;
        }
        .sidebar a:hover, .sidebar a.active {
            color: #fff;
            background: rgba(255, 255, 255, 0.05);
            border-left-color: #3b82f6;
        }
        .sidebar .navbar-brand {
            color: #fff;
            font-weight: 800;
            font-size: 24px;
            padding: 0 30px 40px;
            display: block;
            letter-spacing: 1px;
        }
        .main-content {
            margin-left: 260px;
            padding: 40px;
            min-height: 100vh;
        }
        .glass-card {
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.4);
            color: white;
        }
        .table {
            color: #f1f5f9;
            --bs-table-bg: transparent;
            --bs-table-color: #f1f5f9;
        }
        .table-dark {
            background-color: rgba(15, 23, 42, 0.9) !important;
        }
        .table-striped>tbody>tr:nth-of-type(odd)>* {
            background-color: rgba(255,255,255,0.03);
            color: #f1f5f9;
        }
        .table-striped>tbody>tr:nth-of-type(even)>* {
            background-color: transparent;
            color: #f1f5f9;
        }
        .table-hover>tbody>tr:hover>* {
            background-color: rgba(255,255,255,0.08);
            color: #fff;
        }
        /* Custom Inputs */
        .form-control, .form-select, .input-group-text {
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            color: white !important;
        }
        .form-control:focus, .form-select:focus {
            background-color: rgba(15, 23, 42, 0.9) !important;
            border-color: #3b82f6 !important;
            color: white !important;
            box-shadow: 0 0 0 0.25rem rgba(59, 130, 246, 0.25) !important;
        }
        .form-control::placeholder {
            color: #64748b !important;
        }
        .text-danger { color: #ef4444 !important; }
        .text-success { color: #10b981 !important; }
        .text-primary { color: #3b82f6 !important; }
        .btn-primary { background-color: #3b82f6; border: none; }
        .btn-primary:hover { background-color: #2563eb; }
        .btn-success { background-color: #10b981; border: none; }
        .btn-success:hover { background-color: #059669; }
        
        .login-container {
            margin-left: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .login-box {
            width: 420px;
            padding: 50px 40px;
        }
    </style>
</head>
<body>
    {% if session.get('logged_in') %}
    <div class="sidebar">
        <a class="navbar-brand" href="{{ url_for('dashboard') }}"><i class="fas fa-layer-group text-primary me-2"></i>Nexus<span style="font-weight: 300;">ERP</span></a>
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
    <h3 class="mb-2 fw-bold"><i class="fas fa-layer-group text-primary me-2"></i>Nexus<span style="font-weight: 300;">ERP</span></h3>
    <p class="text-muted mb-4 small text-uppercase" style="letter-spacing: 1px;">Enterprise Inventory Management</p>
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
            <p class="text-muted mb-1 text-uppercase fw-bold" style="letter-spacing: 1px; font-size: 0.85rem;">Total Products</p>
            <h1 class="fw-bold mb-0 display-5">{{ summary.total_products }}</h1>
            <i class="fas fa-box-open position-absolute" style="right: 20px; top: 50%; transform: translateY(-50%); font-size: 4rem; color: rgba(255,255,255,0.05);"></i>
        </div>
    </div>
    <div class="col-md-4">
        <div class="glass-card p-4 h-100 position-relative overflow-hidden" style="border-left: 4px solid #10b981;">
            <p class="text-muted mb-1 text-uppercase fw-bold" style="letter-spacing: 1px; font-size: 0.85rem;">Total Stock Volume</p>
            <h1 class="fw-bold mb-0 display-5">{{ summary.total_stock }}</h1>
            <i class="fas fa-pallet position-absolute" style="right: 20px; top: 50%; transform: translateY(-50%); font-size: 4rem; color: rgba(255,255,255,0.05);"></i>
        </div>
    </div>
    <div class="col-md-4">
        <div class="glass-card p-4 h-100 position-relative overflow-hidden" style="border-left: 4px solid #ef4444;">
            <p class="text-muted mb-1 text-uppercase fw-bold" style="letter-spacing: 1px; font-size: 0.85rem;">Critical Stock Alerts</p>
            <h1 class="fw-bold mb-0 text-danger display-5">{{ summary.low_stock }}</h1>
            <i class="fas fa-exclamation-triangle position-absolute" style="right: 20px; top: 50%; transform: translateY(-50%); font-size: 4rem; color: rgba(239,68,68,0.1);"></i>
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
                <td class="ps-4 text-muted">#{{ '%04d'|format(p[0]) }}</td>
                <td class="fw-bold">{{ p[1] }}</td>
                <td><span class="badge bg-secondary border border-light border-opacity-25">{{ p[2] }}</span></td>
                <td><span class="badge bg-danger rounded-pill px-3">{{ p[4] }}</span></td>
                <td class="text-muted">{{ p[5] }}</td>
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
            <div class="col-md-3"><label class="form-label text-muted small text-uppercase fw-bold">Name</label><input type="text" name="name" class="form-control" required></div>
            <div class="col-md-2"><label class="form-label text-muted small text-uppercase fw-bold">Category</label><input type="text" name="category" class="form-control" required></div>
            <div class="col-md-2"><label class="form-label text-muted small text-uppercase fw-bold">Price ($)</label><input type="number" step="0.01" name="price" class="form-control" required></div>
            <div class="col-md-2"><label class="form-label text-muted small text-uppercase fw-bold">Initial Qty</label><input type="number" name="quantity" class="form-control" required></div>
            <div class="col-md-2"><label class="form-label text-muted small text-uppercase fw-bold">Min Stock</label><input type="number" name="min_stock" class="form-control" required></div>
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
                <td class="ps-4 text-muted">#{{ '%04d'|format(p[0]) }}</td>
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
                <td class="text-muted">{{ p[5] }}</td>
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
                    <label class="form-label text-muted small text-uppercase fw-bold">Product SKU ID</label>
                    <input type="number" name="product_id" class="form-control form-control-lg" placeholder="e.g. 1" required>
                </div>
                <div class="mb-4">
                    <label class="form-label text-muted small text-uppercase fw-bold">Transaction Type</label>
                    <select name="trans_type" class="form-select form-select-lg" required>
                        <option value="IN">📥 Stock IN (Receive)</option>
                        <option value="OUT">📤 Stock OUT (Dispatch)</option>
                    </select>
                </div>
                <div class="mb-5">
                    <label class="form-label text-muted small text-uppercase fw-bold">Quantity</label>
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
                            <td class="ps-4 text-muted">#{{ '%06d'|format(t[0]) }}</td>
                            <td class="fw-bold">{{ t[1] }}</td>
                            <td>
                                {% if t[2] == 'IN' %}
                                <span class="badge bg-success bg-opacity-75 rounded-pill px-3 py-2 border border-success"><i class="fas fa-arrow-down me-1"></i> IN</span>
                                {% else %}
                                <span class="badge bg-warning text-dark bg-opacity-75 rounded-pill px-3 py-2 border border-warning"><i class="fas fa-arrow-up me-1"></i> OUT</span>
                                {% endif %}
                            </td>
                            <td class="fw-bold fs-5">{{ t[3] }}</td>
                            <td class="text-muted small text-end pe-4">{{ t[4] }}</td>
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
"""

# Extract the part before HTML strings
start_idx = content.find("BASE_HTML = '''")
end_idx = content.find("# Routes\n@app.route")

new_content = content[:start_idx] + new_base + "\n" + content[end_idx:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
