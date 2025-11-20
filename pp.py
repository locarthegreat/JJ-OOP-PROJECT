import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from MNE import Database, Product, Customers, Supplier

# If your backend classes are in another file/module, import them:
# from backend_module import Database, Product, Supplier, Customers
# For this snippet we assume Database, Product, Supplier, Customers are available in the namespace.

class TreeviewDBApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sales System - Treeview Admin")
        self.geometry("1100x650")
        self.db = Database()  # uses your Database class

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Tabs
        self.products_tab = ttk.Frame(notebook)
        self.suppliers_tab = ttk.Frame(notebook)
        self.customers_tab = ttk.Frame(notebook)

        notebook.add(self.products_tab, text="Products")
        notebook.add(self.suppliers_tab, text="Suppliers")
        notebook.add(self.customers_tab, text="Customers")

        self._build_products_tab()
        self._build_suppliers_tab()
        self._build_customers_tab()

    # -------------------- Utilities --------------------
    def _get_table_columns(self, table_name):
        """Return list of (name, type) from PRAGMA table_info"""
        self.db.cursor.execute(f"PRAGMA table_info({table_name})")
        info = self.db.cursor.fetchall()
        # info rows: (cid, name, type, notnull, dflt_value, pk)
        return [(row[1], row[2]) for row in info]

    def _query_all(self, table_name):
        self.db.cursor.execute(f"SELECT * FROM {table_name}")
        return self.db.cursor.fetchall()

    def _clear_tree(self, tree):
        for row in tree.get_children():
            tree.delete(row)

    def _insert_rows_into_tree(self, tree, rows):
        # rows from sqlite are tuples - convert to list for display consistency
        for r in rows:
            tree.insert("", "end", values=list(r))

    # -------------------- PRODUCTS TAB --------------------
    def _build_products_tab(self):
        frame = self.products_tab
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=4)

        ttk.Button(toolbar, text="Refresh", command=self.load_products).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Add Product", command=self.add_product_popup).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Edit Selected", command=lambda: self.edit_selected("products")).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Delete Selected", command=lambda: self.delete_selected("products")).pack(side="left", padx=3)

        cols = self._get_table_columns("products")
        col_names = [c[0] for c in cols]
        self.products_tree = ttk.Treeview(frame, columns=col_names, show="headings", selectmode="browse")
        for c in col_names:
            self.products_tree.heading(c, text=c)
            self.products_tree.column(c, width=100, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.products_tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.products_tree.pack(fill="both", expand=True, side="left")
        vsb.pack(fill="y", side="left")
        hsb.pack(fill="x", side="bottom")

        # double click to edit
        self.products_tree.bind("<Double-1>", lambda e: self.edit_selected("products"))

        self.load_products()

    def load_products(self):
        try:
            self._clear_tree(self.products_tree)
            rows = self._query_all("products")
            self._insert_rows_into_tree(self.products_tree, rows)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")

    # -------------------- SUPPLIERS TAB --------------------
    def _build_suppliers_tab(self):
        frame = self.suppliers_tab
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=4)

        ttk.Button(toolbar, text="Refresh", command=self.load_suppliers).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Add Supplier", command=self.add_supplier_popup).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Edit Selected", command=lambda: self.edit_selected("supplier")).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Delete Selected", command=lambda: self.delete_selected("supplier")).pack(side="left", padx=3)

        cols = self._get_table_columns("supplier")
        col_names = [c[0] for c in cols]
        self.suppliers_tree = ttk.Treeview(frame, columns=col_names, show="headings", selectmode="browse")
        for c in col_names:
            self.suppliers_tree.heading(c, text=c)
            self.suppliers_tree.column(c, width=150, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.suppliers_tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.suppliers_tree.xview)
        self.suppliers_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.suppliers_tree.pack(fill="both", expand=True, side="left")
        vsb.pack(fill="y", side="left")
        hsb.pack(fill="x", side="bottom")

        self.suppliers_tree.bind("<Double-1>", lambda e: self.edit_selected("supplier"))

        self.load_suppliers()

    def load_suppliers(self):
        try:
            self._clear_tree(self.suppliers_tree)
            rows = self._query_all("supplier")
            self._insert_rows_into_tree(self.suppliers_tree, rows)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {e}")

    # -------------------- CUSTOMERS TAB --------------------
    def _build_customers_tab(self):
        frame = self.customers_tab
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=4)

        ttk.Button(toolbar, text="Refresh", command=self.load_customers).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Add Customer", command=self.add_customer_popup).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Edit Selected", command=lambda: self.edit_selected("customers")).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Delete Selected", command=lambda: self.delete_selected("customers")).pack(side="left", padx=3)

        cols = self._get_table_columns("customers")
        col_names = [c[0] for c in cols]
        self.customers_tree = ttk.Treeview(frame, columns=col_names, show="headings", selectmode="browse")
        for c in col_names:
            self.customers_tree.heading(c, text=c)
            self.customers_tree.column(c, width=150, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.customers_tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.customers_tree.xview)
        self.customers_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.customers_tree.pack(fill="both", expand=True, side="left")
        vsb.pack(fill="y", side="left")
        hsb.pack(fill="x", side="bottom")

        self.customers_tree.bind("<Double-1>", lambda e: self.edit_selected("customers"))

        self.load_customers()

    def load_customers(self):
        try:
            self._clear_tree(self.customers_tree)
            rows = self._query_all("customers")
            self._insert_rows_into_tree(self.customers_tree, rows)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {e}")

    # -------------------- Generic selection helpers --------------------
    def _get_selected_item_values(self, tree):
        sel = tree.selection()
        if not sel:
            return None
        return tree.item(sel[0])["values"]

    def delete_selected(self, table):
        if table == "products":
            tree = self.products_tree
            id_col = 0
            id_name = "product_id"
            delete_fn = lambda pk: Product("", 0, 0, 1, 0, 0).delete_method(pk, self.db)  # reuse method signature
        elif table == "supplier":
            tree = self.suppliers_tree
            id_col = 0
            id_name = "supplier_id"
            delete_fn = lambda pk: Supplier("", "", "0", "a@b.c", "addr").delete_method(pk, self.db)
        elif table == "customers":
            tree = self.customers_tree
            id_col = 0
            id_name = "customer_id"
            delete_fn = lambda pk: Customers("x").delete_method(pk, self.db)
        else:
            return

        vals = self._get_selected_item_values(tree)
        if not vals:
            messagebox.showinfo("Select row", "Please select a row to delete.")
            return

        pk = vals[id_col]
        if not messagebox.askyesno("Confirm Delete", f"Delete {table[:-1]} with ID {pk}?"):
            return

        try:
            result = delete_fn(pk)
            # Many of your delete_method implementations return strings; handle both
            if isinstance(result, str):
                # success message or error message
                messagebox.showinfo("Delete Result", result)
            else:
                messagebox.showinfo("Deleted", f"{table[:-1].title()} deleted (id={pk})")
            # refresh
            if table == "products":
                self.load_products()
            elif table == "supplier":
                self.load_suppliers()
            else:
                self.load_customers()
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {e}")

    # -------------------- Edit / Add dialogs --------------------
    def edit_selected(self, table):
        if table == "products":
            tree = self.products_tree
            col_info = self._get_table_columns("products")
            id_name = "product_id"
            updater = self._update_product_via_backend
        elif table == "supplier":
            tree = self.suppliers_tree
            col_info = self._get_table_columns("supplier")
            id_name = "supplier_id"
            updater = self._update_supplier_via_backend
        elif table == "customers":
            tree = self.customers_tree
            col_info = self._get_table_columns("customers")
            id_name = "customer_id"
            updater = self._update_customer_via_backend
        else:
            return

        values = self._get_selected_item_values(tree)
        if not values:
            messagebox.showinfo("Select row", "Please select a row to edit.")
            return

        # Build edit popup
        popup = tk.Toplevel(self)
        popup.title("Edit record")
        popup.transient(self)
        popup.grab_set()

        entries = {}
        for idx, (col_name, col_type) in enumerate(col_info):
            ttk.Label(popup, text=col_name).grid(row=idx, column=0, padx=5, pady=3, sticky="w")
            ent = ttk.Entry(popup, width=40)
            ent.grid(row=idx, column=1, padx=5, pady=3, sticky="w")
            ent.insert(0, values[idx] if values[idx] is not None else "")
            if col_name == id_name:
                ent.config(state="disabled")
            entries[col_name] = ent

        def on_save():
            pk = values[0]
            updates = {}
            for col_name, ent in entries.items():
                if col_name == id_name:
                    continue
                val = ent.get().strip()
                # if empty set to None (let backend validate)
                updates[col_name] = val if val != "" else None

            try:
                ok, msg = updater(pk, updates)
                # backend methods in your code return strings or booleans; handle both
                if isinstance(ok, bool) and ok:
                    messagebox.showinfo("Updated", "Record updated successfully.")
                else:
                    messagebox.showinfo("Result", msg if isinstance(msg, str) else str(ok))
                popup.destroy()
                # refresh view
                if table == "products":
                    self.load_products()
                elif table == "supplier":
                    self.load_suppliers()
                else:
                    self.load_customers()
            except Exception as e:
                messagebox.showerror("Error", f"Update failed: {e}")

        ttk.Button(popup, text="Save", command=on_save).grid(row=len(col_info), column=0, padx=5, pady=8)
        ttk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(col_info), column=1, padx=5, pady=8)

    # -------------------- Backend update wrappers --------------------
    def _update_product_via_backend(self, product_id, updates: dict):
        """
        Calls Product.update_method(db, product_id, updates) and returns (True, message) or raises.
        Your Product.update_method returns a string on error or success, so normalize.
        """
        # Normalize: remove None values if backend expects non-null or leave to backend validate
        # If a value is numeric column, backend will validate later.
        result = Product("", 0, 0, 1, 0, 0).update_method(self.db, product_id, updates)
        # Product.update_method returns a string message on success or error
        return (True, result) if "updated successfully" in str(result).lower() else (False, result)

    def _update_supplier_via_backend(self, supplier_id, updates: dict):
        result = Supplier("", "", "0", "a@b.c", "addr").update_method(self.db, supplier_id, updates)
        return (True, result) if "updated successfully" in str(result).lower() else (False, result)

    def _update_customer_via_backend(self, customer_id, updates: dict):
        result = Customers("x").update_method(self.db, customer_id, updates)
        return (True, result) if "updated successfully" in str(result).lower() else (False, result)

    # -------------------- Add popups --------------------
    def add_product_popup(self):
        cols = self._get_table_columns("products")
        # Minimal required fields for Product constructor in your backend:
        # Product(product_name, category_id, type_id, quantity, capital, supplier_id, date_received=None, expiration_date=None, lifespan=None)
        popup = tk.Toplevel(self)
        popup.title("Add Product")
        popup.transient(self)
        popup.grab_set()

        labels = ["product_name", "category", "product type", "quantity", "capital", "supplier_id", "date_received (YYYY-MM-DD, optional)"]
        entries = {}
        for i, lbl in enumerate(labels):
            ttk.Label(popup, text=lbl).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            ent = ttk.Entry(popup, width=40)
            ent.grid(row=i, column=1, padx=5, pady=3)
            entries[lbl] = ent

        def on_add():
            try:
                name = entries["product_name"].get().strip()
                cat = int(entries["category_id"].get().strip() or 0)
                typ = int(entries["type_id"].get().strip() or 0)
                qty = int(entries["quantity"].get().strip() or 1)
                cap = float(entries["capital"].get().strip() or 0.0)
                supp = int(entries["supplier_id"].get().strip() or 0)
                dr = entries["date_received (YYYY-MM-DD, optional)"].get().strip() or None
                date_received = datetime.strptime(dr, "%Y-%m-%d") if dr else None

                prod = Product(name, cat, typ, qty, cap, supp, date_received=date_received)
                msg = prod.add_method(self.db)
                messagebox.showinfo("Added", msg)
                popup.destroy()
                self.load_products()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {e}")

        ttk.Button(popup, text="Add", command=on_add).grid(row=len(labels), column=0, padx=5, pady=8)
        ttk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(labels), column=1, padx=5, pady=8)

    def add_supplier_popup(self):
        # Supplier(supplier_name, contact_person, contact_number, email, address)
        popup = tk.Toplevel(self)
        popup.title("Add Supplier")
        popup.transient(self)
        popup.grab_set()

        labels = ["supplier_name", "contact_person", "contact_number", "email", "address"]
        entries = {}
        for i, lbl in enumerate(labels):
            ttk.Label(popup, text=lbl).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            ent = ttk.Entry(popup, width=50)
            ent.grid(row=i, column=1, padx=5, pady=3)
            entries[lbl] = ent

        def on_add():
            try:
                s = Supplier(
                    entries["supplier_name"].get().strip(),
                    entries["contact_person"].get().strip(),
                    entries["contact_number"].get().strip(),
                    entries["email"].get().strip(),
                    entries["address"].get().strip()
                )
                msg = s.add_method(self.db)
                messagebox.showinfo("Added", msg)
                popup.destroy()
                self.load_suppliers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add supplier: {e}")

        ttk.Button(popup, text="Add", command=on_add).grid(row=len(labels), column=0, padx=5, pady=8)
        ttk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(labels), column=1, padx=5, pady=8)

    def add_customer_popup(self):
        # Customers(customer_name, contact=None, address=None)
        popup = tk.Toplevel(self)
        popup.title("Add Customer")
        popup.transient(self)
        popup.grab_set()

        labels = ["customer_name", "contact (optional)", "address (optional)"]
        entries = {}
        for i, lbl in enumerate(labels):
            ttk.Label(popup, text=lbl).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            ent = ttk.Entry(popup, width=50)
            ent.grid(row=i, column=1, padx=5, pady=3)
            entries[lbl] = ent

        def on_add():
            try:
                c = Customers(
                    entries["customer_name"].get().strip(),
                    contact=entries["contact (optional)"].get().strip() or None,
                    address=entries["address (optional)"].get().strip() or None
                )
                msg = c.add_method(self.db)
                messagebox.showinfo("Added", msg)
                popup.destroy()
                self.load_customers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {e}")

        ttk.Button(popup, text="Add", command=on_add).grid(row=len(labels), column=0, padx=5, pady=8)
        ttk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(labels), column=1, padx=5, pady=8)

# -------------------- Run App --------------------
if __name__ == "__main__":
    app = TreeviewDBApp()
    app.mainloop()
