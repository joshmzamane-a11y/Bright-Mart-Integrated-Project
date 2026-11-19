import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ==========================================
# 1. DATABASE SETUP & INTEGRATION
# ==========================================
def init_db():
    """Initializes the SQLite database and creates necessary tables."""
    conn = sqlite3.connect('brightmart.db')
    cursor = conn.cursor()
    
    # Create Suppliers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT
        )
    ''')
    
    # Create Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            low_stock_threshold INTEGER DEFAULT 10,
            supplier_id INTEGER,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(supplier_id)
        )
    ''')
    
    # Create Sales Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity_sold INTEGER,
            total_price REAL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# ==========================================
# 2. APPLICATION CLASS & USER INTERFACE
# ==========================================
class BrightMartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BrightMart Traders - Inventory & Sales System")
        self.root.geometry("900x600")

        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        # Tab 1: Dashboard (Low Stock Alerts)
        self.dashboard_tab = ttk.Frame(self.notebook, width=900, height=550)
        self.notebook.add(self.dashboard_tab, text="Dashboard & Low Stock")
        self.setup_dashboard_tab()

        # Tab 2: Inventory Management
        self.inventory_tab = ttk.Frame(self.notebook, width=900, height=550)
        self.notebook.add(self.inventory_tab, text="Manage Inventory")
        self.setup_inventory_tab()

        # Tab 3: Record Sales
        self.sales_tab = ttk.Frame(self.notebook, width=900, height=550)
        self.notebook.add(self.sales_tab, text="Process Sales")
        self.setup_sales_tab()

        # Tab 4: Reports
        self.reports_tab = ttk.Frame(self.notebook, width=900, height=550)
        self.notebook.add(self.reports_tab, text="Sales & Inventory Reports")
        self.setup_reports_tab()

        # Load initial data
        self.refresh_all_data()

    # ------------------------------------------
    # TAB 1: DASHBOARD
    # ------------------------------------------
    def setup_dashboard_tab(self):
        tk.Label(self.dashboard_tab, text="Low Stock Alerts", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.low_stock_tree = ttk.Treeview(self.dashboard_tab, columns=("ID", "Product", "Quantity"), show="headings")
        self.low_stock_tree.heading("ID", text="Product ID")
        self.low_stock_tree.heading("Product", text="Product Name")
        self.low_stock_tree.heading("Quantity", text="Current Stock")
        self.low_stock_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Button(self.dashboard_tab, text="Refresh Dashboard", command=self.refresh_dashboard).pack(pady=10)

    def refresh_dashboard(self):
        for row in self.low_stock_tree.get_children():
            self.low_stock_tree.delete(row)
            
        conn = sqlite3.connect('brightmart.db')
        cursor = conn.cursor()
        cursor.execute('SELECT product_id, name, quantity FROM products WHERE quantity <= low_stock_threshold')
        for row in cursor.fetchall():
            self.low_stock_tree.insert("", tk.END, values=row)
        conn.close()

    # ------------------------------------------
    # TAB 2: INVENTORY MANAGEMENT
    # ------------------------------------------
    def setup_inventory_tab(self):
        # Input Frame
        input_frame = tk.Frame(self.inventory_tab)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Product Name:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_name = tk.Entry(input_frame)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Price (R):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_price = tk.Entry(input_frame)
        self.entry_price.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Quantity:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_quantity = tk.Entry(input_frame)
        self.entry_quantity.grid(row=0, column=5, padx=5, pady=5)

        tk.Button(input_frame, text="Add Product", command=self.add_product, bg="green", fg="white").grid(row=0, column=6, padx=10)

        # Treeview Frame
        self.inventory_tree = ttk.Treeview(self.inventory_tab, columns=("ID", "Name", "Price", "Quantity"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Product Name")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def add_product(self):
        name = self.entry_name.get()
        price = self.entry_price.get()
        quantity = self.entry_quantity.get()

        if not name or not price or not quantity:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            conn = sqlite3.connect('brightmart.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)', (name, float(price), int(quantity)))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"{name} added to inventory.")
            self.refresh_all_data()
        except ValueError:
            messagebox.showerror("Error", "Price must be a decimal, Quantity must be a whole number.")

    def refresh_inventory(self):
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)
            
        conn = sqlite3.connect('brightmart.db')
        cursor = conn.cursor()
        cursor.execute('SELECT product_id, name, price, quantity FROM products')
        for row in cursor.fetchall():
            self.inventory_tree.insert("", tk.END, values=(row[0], row[1], f"R{row[2]:.2f}", row[3]))
        conn.close()

    # ------------------------------------------
    # TAB 3: PROCESS SALES
    # ------------------------------------------
    def setup_sales_tab(self):
        sales_frame = tk.Frame(self.sales_tab)
        sales_frame.pack(pady=20)

        tk.Label(sales_frame, text="Select Product:").grid(row=0, column=0, padx=5, pady=5)
        self.sale_product_combo = ttk.Combobox(sales_frame, state="readonly")
        self.sale_product_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(sales_frame, text="Quantity to Sell:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_sale_qty = tk.Entry(sales_frame)
        self.entry_sale_qty.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(sales_frame, text="Complete Sale", command=self.process_sale, bg="blue", fg="white", width=20).grid(row=2, column=0, columnspan=2, pady=15)

    def refresh_sales_combo(self):
        conn = sqlite3.connect('brightmart.db')
        cursor = conn.cursor()
        cursor.execute('SELECT product_id, name, price, quantity FROM products WHERE quantity > 0')
        products = cursor.fetchall()
        
        self.product_dict = {f"{p[1]} (ID:{p[0]}) - R{p[2]:.2f} [Stock: {p[3]}]": p for p in products}
        self.sale_product_combo['values'] = list(self.product_dict.keys())
        conn.close()

    def process_sale(self):
        selected = self.sale_product_combo.get()
        qty_str = self.entry_sale_qty.get()

        if not selected or not qty_str:
            messagebox.showerror("Error", "Please select a product and enter quantity.")
            return

        try:
            qty_to_sell = int(qty_str)
            if qty_to_sell <= 0:
                raise ValueError
            
            product_data = self.product_dict[selected]
            product_id = product_data[0]
            price = product_data[2]
            current_stock = product_data[3]

            if qty_to_sell > current_stock:
                messagebox.showerror("Error", f"Insufficient stock! Only {current_stock} available.")
                return

            total_price = qty_to_sell * price

            # Perform Database Transaction
            conn = sqlite3.connect('brightmart.db')
            cursor = conn.cursor()
            
            # 1. Record the sale
            cursor.execute('INSERT INTO sales (product_id, quantity_sold, total_price) VALUES (?, ?, ?)', 
                           (product_id, qty_to_sell, total_price))
            
            # 2. Update the stock
            new_stock = current_stock - qty_to_sell
            cursor.execute('UPDATE products SET quantity = ? WHERE product_id = ?', (new_stock, product_id))
            
            conn.commit()
            conn.close()

            messagebox.showinfo("Sale Complete", f"Sale Successful!\nTotal: R{total_price:.2f}")
            self.entry_sale_qty.delete(0, tk.END)
            self.refresh_all_data()

        except ValueError:
            messagebox.showerror("Error", "Quantity must be a valid positive number.")

    # ------------------------------------------
    # TAB 4: REPORTS
    # ------------------------------------------
    def setup_reports_tab(self):
        tk.Label(self.reports_tab, text="Total Sales Revenue", font=("Arial", 14)).pack(pady=5)
        self.lbl_revenue = tk.Label(self.reports_tab, text="R0.00", font=("Arial", 20, "bold"), fg="green")
        self.lbl_revenue.pack(pady=10)

        tk.Button(self.reports_tab, text="Generate/Refresh Reports", command=self.generate_report).pack(pady=10)

        self.report_tree = ttk.Treeview(self.reports_tab, columns=("SaleID", "ProductID", "Qty", "Total", "Date"), show="headings")
        self.report_tree.heading("SaleID", text="Sale ID")
        self.report_tree.heading("ProductID", text="Product ID")
        self.report_tree.heading("Qty", text="Qty Sold")
        self.report_tree.heading("Total", text="Total (R)")
        self.report_tree.heading("Date", text="Date")
        self.report_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def generate_report(self):
        for row in self.report_tree.get_children():
            self.report_tree.delete(row)

        conn = sqlite3.connect('brightmart.db')
        cursor = conn.cursor()
        
        # Calculate total revenue
        cursor.execute('SELECT SUM(total_price) FROM sales')
        revenue = cursor.fetchone()[0]
        self.lbl_revenue.config(text=f"R{revenue if revenue else 0.00:.2f}")

        # Display all sales
        cursor.execute('SELECT sale_id, product_id, quantity_sold, total_price, sale_date FROM sales ORDER BY sale_date DESC')
        for row in cursor.fetchall():
            self.report_tree.insert("", tk.END, values=(row[0], row[1], row[2], f"R{row[3]:.2f}", row[4]))
        
        conn.close()

    # ------------------------------------------
    # UTILITY METHODS
    # ------------------------------------------
    def refresh_all_data(self):
        self.refresh_dashboard()
        self.refresh_inventory()
        self.refresh_sales_combo()
        self.generate_report()

# ==========================================
# 3. APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    init_db() # Initialize database tables if they don't exist
    root = tk.Tk()
    app = BrightMartApp(root)
    root.mainloop()
