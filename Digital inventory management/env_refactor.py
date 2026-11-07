import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add os and dotenv imports
import_section = """import sqlite3
import hashlib
import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv()
"""

content = content.replace('import sqlite3\nimport hashlib\nfrom datetime import datetime\nfrom flask import Flask, render_template_string, request, redirect, url_for, session, flash', import_section)

# Update secret key and debug flags
app_init_old = """app = Flask(__name__)
app.secret_key = "super_secret_inventory_key\""""

app_init_new = """app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_dev_key")

# Database name from environment (fallback to inventory.db for dev)
DB_NAME = os.environ.get("DATABASE_NAME", "inventory.db")"""

content = content.replace(app_init_old, app_init_new)

# Update DatabaseManager initialization
db_init_old = 'db = DatabaseManager()'
db_init_new = 'db = DatabaseManager(DB_NAME)'
content = content.replace(db_init_old, db_init_new)

# Ensure DatabaseManager uses the parameter gracefully
db_class_old = """class DatabaseManager:
    def __init__(self, db_name="inventory.db"):
        self.db_name = db_name
        self.create_tables()"""
        
# It already uses db_name="inventory.db", so passing DB_NAME works perfectly.

# Update the app.run
run_old = """if __name__ == '__main__':
    app.run(debug=True, port=5000)"""

run_new = """if __name__ == '__main__':
    # Parse FLASK_DEBUG safely from string
    is_debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    
    # Do not blindly allow debug True in production without explicit env flag
    app.run(debug=is_debug, port=5000)"""

content = content.replace(run_old, run_new)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
