import sqlite3

def reset_menu():
    """
    Wipes the current menu and replaces it with a clean, small default list.
    Run this ONCE to fix your database.
    """
    # Connect to the database
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    
    # 1. Wipe the old menu completely
    cursor.execute("DELETE FROM menu")
    print("🗑️  Old menu deleted.")
    
    # 2. Add the new "Smart Menu"
    new_items = [
        ("Chicken Burger", 120),
        ("Veg Pizza", 200),
        ("Masala Coke", 50),
        ("French Fries", 80),
        ("Chocolate Lava Cake", 150)
    ]
    
    # Insert new items
    cursor.executemany("INSERT INTO menu (name, price) VALUES (?, ?)", new_items)
    
    # Save changes
    conn.commit()
    conn.close()
    print("✅ Menu has been successfully reset to 5 items!")

if __name__ == "__main__":
    reset_menu()