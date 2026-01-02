import sqlite3

DB_NAME = "hotel.db"

def init_db():
    """
    Creates the database tables if they don't exist.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            order_details TEXT,
            total_price REAL,
            payment_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Menu Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price REAL
        )
    ''')

    # Check if menu is empty, if so, add default items
    cursor.execute('SELECT count(*) FROM menu')
    if cursor.fetchone()[0] == 0:
        default_items = [
            ("Chicken Burger", 120),
            ("Veg Pizza", 200),
            ("Coke", 40),
            ("Fries", 80)
        ]
        cursor.executemany("INSERT INTO menu (name, price) VALUES (?, ?)", default_items)
        print("✅ Default menu created.")

    conn.commit()
    conn.close()

# --- USER FUNCTIONS ---
def add_user(phone_number):
    """Adds a new user if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    try:
        with conn:
            conn.execute("INSERT OR IGNORE INTO users (phone_number) VALUES (?)", (phone_number,))
    finally:
        conn.close()

# --- ORDER FUNCTIONS ---
def add_order(phone_number, order_details, total_price, payment_id):
    """Saves a new order."""
    conn = sqlite3.connect(DB_NAME)
    try:
        with conn:
            conn.execute('''
                INSERT INTO orders (phone_number, order_details, total_price, payment_id)
                VALUES (?, ?, ?, ?)
            ''', (phone_number, order_details, total_price, payment_id))
    finally:
        conn.close()

# --- MENU FUNCTIONS (AI Helper) ---
def get_menu_string():
    """Returns the menu as a formatted string for the AI."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM menu")
    items = cursor.fetchall()
    conn.close()
    
    # Format: "Item : ₹Price\n"
    menu_text = "\n".join([f"{item[0]} : ₹{item[1]}" for item in items])
    return menu_text

# --- MENU MANAGEMENT (Dashboard Helpers) ---
def add_menu_item(name, price):
    """Adds a new item to the database."""
    conn = sqlite3.connect(DB_NAME)
    try:
        with conn:
            conn.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, price))
        return True
    except sqlite3.IntegrityError:
        return False # Item already exists
    finally:
        conn.close()

def delete_menu_item(item_name):
    """Removes an item from the database."""
    conn = sqlite3.connect(DB_NAME)
    try:
        with conn:
            conn.execute("DELETE FROM menu WHERE name = ?", (item_name,))
    finally:
        conn.close()

def get_raw_menu():
    """Returns the menu as a list of tuples for the GUI."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM menu")
    items = cursor.fetchall()
    conn.close()
    return items