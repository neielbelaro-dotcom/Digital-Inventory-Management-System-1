# Digital Inventory Management System

## Overview
The Digital Inventory Management System is a streamlined web-based application designed to manage product records and monitor stock movements efficiently. It solves the problem of inaccurate quantities and missing records by providing a centralized, digital method for tracking stock movements and ensuring businesses always know their current inventory levels.

## Core Features
- **Dashboard Analytics**: Real-time overview of total products, total stock volume, and critical stock alerts.
- **Product Management**: Full CRUD (Create, Read, Update, Delete) capabilities for the product catalog.
- **Stock Movement Tracking**: Accurately log Stock IN (receiving) and Stock OUT (dispatching) transactions.
- **Low Stock Alerts**: Automatic identification and highlighting of products that have reached or fallen below their minimum stock threshold.
- **Transaction History**: A comprehensive, timestamped log of all inventory movements.
- **Secure Authentication**: Protected access to ensure only authorized personnel can view or modify inventory data.

## User Roles
- **Administrator / Warehouse Manager**: Has full access to the system. Can manage the product catalog, process stock transactions, and view all dashboard metrics and transaction logs.
- *(Note: Currently implemented as a single-role system with secure authentication, expandable for future multi-role capabilities).*

## Inventory Workflow
1. **Authentication**: Users securely log into the system.
2. **Product Registration**: New items are registered in the Product Catalog with their initial quantities and minimum stock thresholds.
3. **Stock Transactions**: When stock is received or dispatched, a user navigates to the Stock Movement tab to log an IN or OUT transaction.
4. **Monitoring**: The system automatically updates the stock levels. If an item's quantity drops below its minimum threshold, it is immediately flagged on the Dashboard's Critical Stock Alerts.

## Reports and Exports
- **Dashboard Summary**: Real-time aggregation of total products, stock volume, and active alerts.
- **Transaction Logs**: A scrollable, timestamped history of all recent stock IN/OUT operations available directly within the application for immediate review and auditing.

## Technology Stack
- **Backend**: Python 3, Flask
- **Database**: SQLite (via `sqlite3`)
- **Frontend**: HTML5, CSS3, Bootstrap 5, FontAwesome
- **Architecture**: Lightweight Model-View-Controller (MVC) pattern

## Project Structure
```text
.
├── app.py                   # Main Flask application, routes, and UI templates
├── inventory.db             # SQLite database file (auto-generated)
├── seed_db.py               # Utility script to generate mock transaction logs
├── add_critical_stocks.py   # Utility script to generate critical stock scenarios
├── update_ui.py             # Utility script used for UI enhancements
├── rename.py                # Utility script used for system renaming
└── README.md                # System documentation
```

## Local Setup
1. Ensure Python 3.x is installed on your machine.
2. Ensure `pip` (Python package installer) is available.
3. Clone or download the repository to your local machine.
4. Open a terminal or command prompt in the project directory.

## Environment Configuration
1. Install the required Python dependencies:
   ```bash
   pip install flask python-dotenv
   ```
2. The repository includes an `.env.example` file. Copy this to create your local `.env` file:
   ```bash
   cp .env.example .env
   ```
3. **Development vs. Production**:
   - In **development**, you may set `FLASK_DEBUG=True` in your `.env` file.
   - In **production**, ensure `FLASK_DEBUG=False` and set a strong, unique `SECRET_KEY` to protect session cookies.
4. **Security Note**: The `.env` file and the local SQLite database (`inventory.db`) are excluded from version control via `.gitignore` to prevent accidental exposure of credentials and data.

## Database Configuration
1. The database (`inventory.db`) is automatically initialized the first time the application runs.
2. Tables for `users`, `products`, and `transactions` are created automatically if they do not exist.
3. A default admin user is seeded automatically upon initialization.

## Running the Application
1. Start the application server:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to:
   ```text
   http://localhost:5000
   ```

## Testing
1. Log in with the default credentials provided by your system administrator.
2. Navigate to the **Products** tab to ensure you can add and delete items.
3. Navigate to the **Transactions** tab to log a Stock IN and Stock OUT, verifying the quantities update correctly.
4. Check the **Dashboard** to ensure metrics reflect your recent changes.

## Documentation
- The primary documentation is this `README.md` file.
- Code-level documentation and logic structure are available directly within `app.py`.

## Deployment
This application currently runs via the built-in Flask development server. For production deployment on a cloud provider (e.g., AWS, Heroku, or DigitalOcean), it is recommended to use a WSGI server such as Gunicorn and configure a reverse proxy like Nginx.
