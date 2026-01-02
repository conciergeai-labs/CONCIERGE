import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import threading
import app  
import database 

# --- FLASK SERVER (Background Thread) ---
def start_server():
    """Runs the AI Bot in the background"""
    # use_reloader=False is crucial for threading!
    app.app.run(port=5000, use_reloader=False)

# --- GUI LOGIC ---
class HotelAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel AI Manager - Admin Console")
        self.root.geometry("900x600")

        # Create Tabs
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=1, fill="both")

        # Tab 1: Live Orders
        self.tab_orders = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_orders, text="🛎️ Live Orders")
        self.setup_orders_tab()

        # Tab 2: Menu Manager
        self.tab_menu = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_menu, text="🍔 Menu Manager")
        self.setup_menu_tab()

        # Start Auto-Refresh Loop
        self.refresh_data()

    # --- TAB 1: ORDERS ---
    def setup_orders_tab(self):
        # Table Columns
        cols = ("ID", "Phone", "Items", "Total (₹)", "Pay ID")
        self.order_tree = ttk.Treeview(self.tab_orders, columns=cols, show="headings", height=20)
        
        # Define Headings
        for col in cols:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=150)

        self.order_tree.pack(expand=True, fill="both", padx=10, pady=10)

    # --- TAB 2: MENU MANAGER ---
    def setup_menu_tab(self):
        # Frame for Adding New Items
        input_frame = tk.Frame(self.tab_menu, bg="#f0f0f0", bd=2, relief="groove")
        input_frame.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(input_frame, text="Add New Item", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)
        
        tk.Label(input_frame, text="Item Name:", bg="#f0f0f0").pack(anchor="w", padx=5)
        self.entry_name = tk.Entry(input_frame, width=25)
        self.entry_name.pack(padx=5, pady=5)

        tk.Label(input_frame, text="Price (₹):", bg="#f0f0f0").pack(anchor="w", padx=5)
        self.entry_price = tk.Entry(input_frame, width=25)
        self.entry_price.pack(padx=5, pady=5)

        btn_add = tk.Button(input_frame, text="➕ Add to Menu", bg="green", fg="white", command=self.add_item)
        btn_add.pack(pady=20, fill="x", padx=10)

        # Frame for Listing Current Menu
        list_frame = tk.Frame(self.tab_menu)
        list_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        tk.Label(list_frame, text="Current Menu", font=("Arial", 12, "bold")).pack(pady=5)

        # Menu Table
        self.menu_tree = ttk.Treeview(list_frame, columns=("Name", "Price"), show="headings")
        self.menu_tree.heading("Name", text="Item Name")
        self.menu_tree.heading("Price", text="Price (₹)")
        self.menu_tree.pack(expand=True, fill="both")

        btn_del = tk.Button(list_frame, text="🗑️ Delete Selected Item", bg="red", fg="white", command=self.delete_item)
        btn_del.pack(pady=10, fill="x")

    # --- ACTIONS ---
    def add_item(self):
        name = self.entry_name.get()
        price = self.entry_price.get()

        if name and price:
            try:
                # Calls the database function to add item
                success = database.add_menu_item(name, float(price))
                if success:
                    self.entry_name.delete(0, 'end')
                    self.entry_price.delete(0, 'end')
                    self.refresh_menu_list()
                    messagebox.showinfo("Success", f"Added {name} to menu!")
                else:
                    messagebox.showerror("Error", "Could not add item.")
            except ValueError:
                messagebox.showerror("Error", "Price must be a number!")
        else:
            messagebox.showwarning("Warning", "Please fill both fields.")

    def delete_item(self):
        selected = self.menu_tree.selection()
        if selected:
            item_values = self.menu_tree.item(selected[0])['values']
            item_name = item_values[0] # Get name from the selected row
            
            confirm = messagebox.askyesno("Confirm", f"Remove '{item_name}' from menu?")
            if confirm:
                database.delete_menu_item(item_name)
                self.refresh_menu_list()

    # --- REFRESH LOOPS ---
    def refresh_data(self):
        """Refreshes orders every 5 seconds"""
        # 1. Update Orders
        for row in self.order_tree.get_children():
            self.order_tree.delete(row)
            
        # Helper to get orders directly
        conn = sqlite3.connect("hotel.db")
        cur = conn.cursor()
        cur.execute("SELECT id, phone_number, order_details, total_price, payment_id FROM orders ORDER BY id DESC")
        orders = cur.fetchall()
        conn.close()

        for order in orders:
            self.order_tree.insert("", "end", values=order)

        # 2. Refresh Menu List (if tab is active)
        if self.tabs.select() == str(self.tab_menu): 
             self.refresh_menu_list()

        self.root.after(5000, self.refresh_data)

    def refresh_menu_list(self):
        """Updates the visual menu list"""
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)
        
        items = database.get_raw_menu()
        for item in items:
            self.menu_tree.insert("", "end", values=item)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Start Flask Server in Thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 2. Start GUI
    root = tk.Tk()
    app_ui = HotelAdminApp(root)
    root.mainloop()