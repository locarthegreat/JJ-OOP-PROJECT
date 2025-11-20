from tkinter import *
from tkinter import messagebox
from MNE import *  
from tkinter import ttk
from tkcalendar import DateEntry
from cryptography.fernet import Fernet


gui = Tk()
gui.title("JOMAR & CARLO")
img = PhotoImage(file= r"C:\Users\ACER\OneDrive\Desktop\OOP PROJECT\logo.png")
gui.iconphoto(True, img)

db = Database()
def create_labeled_entries(parent, fields, date_fields=None, product=None):
    if date_fields is None:
        date_fields = ["Date Received (YYYY-MM-DD)", "Expiration Date (YYYY-MM-DD)"]

    entries = {}

    # Determine if fields is a list of tuples or list of strings
    if fields and isinstance(fields[0], tuple):
        field_items = fields
    else:
        field_items = [(field, "") for field in fields]

    for label_text, default in field_items:
        row = Frame(parent)
        row.pack(fill="x", padx=10, pady=4)

        Label(row, text=label_text, width=25, anchor="w").pack(side="left")

        # Determine database key name
        db_key = label_text.lower().replace(" ", "_").replace("(yyyy-mm-dd)", "").strip()

        # Pre-fill with product value if available, else default
        value = str(product.get(db_key, default)) if product else default

        if label_text in date_fields:
            ent = DateEntry(
                row, width=25, background='darkblue',
                foreground='white', borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            if product and product.get(db_key):
                ent.set_date(product[db_key])
        else:
            ent = Entry(row)
            ent.insert(0, value)

        ent.pack(side="left", fill="x", expand=True)
        entries[label_text] = ent

    return entries


def create_control_panel(parent, button_data):
    ctrl = Frame(parent, bg="#D9D9D9")
    ctrl.pack(side="left", padx=(5, 10))

    for text, cmd in button_data:
        Button(ctrl, text=text, font=("Arial", 10, "bold"), command=cmd).pack(side="left", padx=3)

    return ctrl


def create_search_bar(parent, search_callback, text="Search:"):
    search_frame = Frame(parent, bg="#D9D9D9")
    search_frame.pack(side="right", padx=(10, 10))

    Label(
        search_frame,
        text=text,
        bg="#D9D9D9",
        font=("Arial", 10, "bold")
    ).pack(side="left", padx=(0, 5))

    search_entry = Entry(search_frame, width=40)
    search_entry.pack(side="left", padx=(0, 5), ipady=5)

    # Trigger search whenever user types or deletes a character
    def on_key_release(event):
        query = search_entry.get().strip()
        search_callback(query)

    search_entry.bind("<KeyRelease>", on_key_release)

    return search_frame, search_entry


def refreshSection():
    for i in section.winfo_children():
        i.destroy()
def clearWindow():
    for i in gui.winfo_children():
        i.destroy()
def rounded_frame(parent, width, height, radius=25, bg="blue"):
    """Create a rounded-corner frame using a Canvas."""
    canvas = Canvas(parent, width=width, height=height, bg=section["bg"], highlightthickness=0)
    canvas.grid_propagate(False)

    # Draw rounded rectangle
    canvas.create_round_rect = canvas.create_arc
    canvas.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, fill=bg, outline=bg)  # Top-left
    canvas.create_arc(width-radius*2, 0, width, radius*2, start=0, extent=90, fill=bg, outline=bg) # Top-right
    canvas.create_arc(0, height-radius*2, radius*2, height, start=180, extent=90, fill=bg, outline=bg) # Bottom-left
    canvas.create_arc(width-radius*2, height-radius*2, width, height, start=270, extent=90, fill=bg, outline=bg) # Bottom-right
    canvas.create_rectangle(radius, 0, width-radius, height, fill=bg, outline=bg)
    canvas.create_rectangle(0, radius, width, height-radius, fill=bg, outline=bg)

    # Embed a frame on top
    frame = Frame(canvas, bg=bg)
    canvas.create_window(width/2, height/2, window=frame)
    return canvas, frame

def DashBoard():
    refreshSection()
    headText.config(text="DASHBOARD")

    # Make grid responsive
    for i in range(3):
        section.columnconfigure(i, weight=1)
    section.rowconfigure(0, weight=1)

    # Create rounded statistic cards
    salesCard, salesFrame = rounded_frame(section, 250, 150, radius=25, bg="#1E88E5")
    userCard, userFrame = rounded_frame(section, 250, 150, radius=25, bg="#1E88E5")
    prodCard, prodFrame = rounded_frame(section, 250, 150, radius=25, bg="#1E88E5")

    salesCard.grid(row=0, column=0, padx=10, pady=10)
    userCard.grid(row=0, column=1, padx=10, pady=10)
    prodCard.grid(row=0, column=2, padx=10, pady=10)

    # Database values
    db = sqlite3.connect("Hardware and Construction.db")
    cs = db.cursor()

    cs.execute("SELECT SUM(total_sales) FROM monthly_financials")
    total_sales = cs.fetchone()[0] or 0


    cs.execute("SELECT COUNT(*) FROM users")
    user_count = cs.fetchone()[0]

    cs.execute("SELECT COUNT(*) FROM products")
    product_count = cs.fetchone()[0]

    # Labels
    Label(salesFrame, text=f"₱ {total_sales}\nSales", fg="white", bg="#1E88E5",
          font=("Arial", 22, "bold")).pack(expand=True)

    Label(userFrame, text=f"👤 {user_count}\nActive Users", fg="white", bg="#1E88E5",
          font=("Arial", 22, "bold")).pack(expand=True)

    Label(prodFrame, text=f"{product_count}\nProducts Available", fg="white", bg="#1E88E5",
          font=("Arial", 18, "bold")).pack(expand=True)

    
def TreeView(frame, columns, width):
    tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode= "extended")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center")

    tree.pack(fill="both", expand=True, side="left")
    
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vsb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=vsb.set)
    
    return tree

def DialogBox(title, gui, fields = None):
    dialog = Toplevel(gui)
    dialog.title(title)
    dialog.geometry("400x480+300+200")
    dialog.transient(gui)
    dialog.grab_set()
    return dialog

def Inventory():
    refreshSection()
    headText.config(text="INVENTORY")

    inv_frame = Frame(section, bg="#D9D9D9")
    inv_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ===== CONTROL PANEL + SEARCH BAR (INLINE) =====
    top_bar = Frame(inv_frame, bg="#D9D9D9")
    top_bar.pack(fill="x", pady=(0, 8))

    # --- Left side: action buttons ---
    buttons = [
        ("Add Product", lambda: add_product_dialog()),
        ("Edit Selected", lambda: edit_selected_dialog()),
        ("Delete Selected", lambda: delete_selected()),
        ("Refresh", lambda: load_data())
    ]
    create_control_panel(top_bar, buttons)

    # --- Right side: search bar ---
    _ = create_search_bar(top_bar, lambda keyword: search_product(keyword), text="Search Product Info:")

    msg_label = Label(inv_frame, text="", bg="#D9D9D9", fg="blue", anchor="w")
    msg_label.pack(fill="x", pady=(2, 0))

    # ===== TREEVIEW TABLE =====
    tree_frame = Frame(inv_frame, bg="#D9D9D9")
    tree_frame.pack(fill="both", expand=True)

    header_map = {
        "product_id": "Product ID",
        "product_name": "Product Name",
        "category_name": "Category",
        "type_name": "Type",
        "quantity": "Quantity",
        "capital": "Capital per Piece",
        "srp": "SRP",
        "total_capital": "Total Capital",
        "supplier_name": "Supplier",
        "date_received": "Date Received",
        "expiration_date": "Expiration Date",
        "lifespan": "Lifespan"
    }

    headers = list(header_map.keys())
    columns = list(header_map.values())
    tree = TreeView(tree_frame, columns, width=100)

    # ===== BACKEND PROXY =====
    def _product_proxy():
        return Product("proxy_temp", 1, 1, 1, 0.0, 1)

    # ===== LOAD DATA =====
    def load_data():
        try:
            tree.delete(*tree.get_children())
            proxy = _product_proxy()
            res = proxy.view_method(db, choice="all")

            if isinstance(res, str):
                msg_label.config(text=res, fg="red")
                return

            for row in res:
                tree.insert("", "end", values=[row.get(h, "") for h in headers])

            msg_label.config(text=f"{len(res)} product(s) loaded.", fg="green")
        except Exception as e:
            msg_label.config(text=f"Error loading data: {e}", fg="red")

    # ===== SEARCH FUNCTION =====
    def search_product(keyword):
        keyword = keyword.strip()
        tree.delete(*tree.get_children())
        proxy = _product_proxy()
        res = proxy.view_method(db, choice="all")

        if not keyword:
            for row in res:
                tree.insert("", "end", values=[row.get(h, "") for h in headers])
            msg_label.config(text="Showing all products.", fg="blue")
            return

        filtered = [
            item for item in res
            if keyword.lower() in str(item.get("product_name", "")).lower()
            or keyword.lower() in str(item.get("category_name", "")).lower()
            or keyword.lower() in str(item.get("type_name", "")).lower()
            or keyword.lower() in str(item.get("supplier_name", "")).lower()
            or keyword in str(item.get("date_received", ""))
        ]

        for row in filtered:
            tree.insert("", "end", values=[row.get(h, "") for h in headers])

        msg_label.config(
            text=f"{len(filtered)} result(s) found for '{keyword}'." if filtered else f"No results for '{keyword}'.",
            fg="green" if filtered else "red"
        )

    # ===== ADD PRODUCT =====
    def add_product_dialog():
        dialog = DialogBox("Add New Product", gui)
        fields = [
            ("Product Name", ""), ("Category ID", "1"), ("Type ID", "1"),
            ("Quantity", "1"), ("Capital per Piece", "0.00"), ("Supplier ID", "1"),
            ("Date Received (YYYY-MM-DD)", ""), ("Expiration Date (YYYY-MM-DD)", ""), ("Lifespan (days)", "")
        ]
        entries = create_labeled_entries(dialog, fields)

        def save_new():
            try:
                pname = entries["Product Name"].get().strip().title()
                category_id = int(entries["Category ID"].get())
                type_id = int(entries["Type ID"].get())
                quantity = int(entries["Quantity"].get())
                capital = float(entries["Capital per Piece"].get())
                supplier_id = int(entries["Supplier ID"].get())
                date_received = entries["Date Received (YYYY-MM-DD)"].get().strip() or None
                expiration_date = entries["Expiration Date (YYYY-MM-DD)"].get().strip() or None
                lifespan = entries["Lifespan (days)"].get().strip()
                lifespan = int(lifespan) if lifespan else 0

                prod = Product(
                    pname, category_id, type_id, quantity, capital, supplier_id,
                    date_received=date_received, expiration_date=expiration_date, lifespan=lifespan
                )
                msg = prod.add_method(db)
                messagebox.showinfo("Add Product", msg)
                dialog.destroy()
                load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(dialog, text="Save Product", command=save_new).pack(pady=10)

    # ===== EDIT PRODUCT =====
    def edit_selected_dialog():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Edit", "Select a product first.")
            return

        # Extract product_id from selected row
        row_values = tree.item(sel[0], "values")
        product_id = row_values[0]

        proxy = _product_proxy()
        result = proxy.view_method(db, choice="one", product_id=product_id)

        #if isinstance(result, str):
            #messagebox.showerror("Error", result)
            #return

        # Use the first result (single product)
        product = result[0]

        # Create dialog window
        dialog = DialogBox(f"Edit Product #{product_id}", gui)

        # Map UI label → DB key (must match backend names)
        field_map = {
            "Product Name": "product_name",
            "Category Id": "category_id",
            "Type Id": "type_id",
            "Quantity": "quantity",
            "Capital per Piece": "capital",
            "Supplier Id": "supplier_id",
            "Date Received (YYYY-MM-DD)": "date_received",
            "Expiration Date (YYYY-MM-DD)": "expiration_date",
            "Lifespan": "lifespan"
        }

        # Generate entry fields (your helper function)
        entries = create_labeled_entries(dialog, list(field_map.keys()), product=product)

        # SAVE HANDLER
        def save_edit():
            try:
                updates = {}

                # Must match backend conversion rules
                int_columns = ["quantity", "category_id", "type_id", "supplier_id", "lifespan"]
                float_columns = ["capital"]

                # Collect values from the dialog
                for label, entry in entries.items():
                    db_key = field_map[label]
                    new_val = entry.get().strip()
                    old_val = product.get(db_key, "")

                    if old_val is None:
                        old_val = ""

                    # Skip empty OR unchanged values
                    if new_val == "" or str(old_val) == new_val:
                        continue

                    # Convert to integer
                    if db_key in int_columns:
                        try:
                            updates[db_key] = int(new_val)
                        except ValueError:
                            messagebox.showerror("Error", f"{label} must be an integer.")
                            return

                    # Convert to float
                    elif db_key in float_columns:
                        try:
                            updates[db_key] = float(new_val)
                        except ValueError:
                            messagebox.showerror("Error", f"{label} must be a number.")
                            return

                    else:
                        updates[db_key] = new_val

                # No fields changed
                if not updates:
                    messagebox.showinfo("Edit", "No changes have been made.")
                    return

                # Send to backend, which handles ALL FK validation + logic
                msg = proxy.update_method(db, product_id, updates)

                if "successfully" in msg.lower():
                    messagebox.showinfo("Update Successful", msg)
                    dialog.destroy()
                    load_data()
                else:
                    messagebox.showerror("Error", msg)

            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Save button
        Button(dialog, text="Save Changes", command=save_edit).pack(pady=10)


    def delete_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Delete", "Select at least one product to delete.")
            return

        product_ids = [tree.item(iid, "values")[0] for iid in sel]

        if not messagebox.askyesno("Confirm", f"Delete {len(product_ids)} product(s)?"):
            return

        proxy = _product_proxy()
        deleted_count = 0
        for pid in product_ids:
            msg = proxy.delete_method(pid, db)
            if "success" in msg.lower():
                deleted_count += 1

        messagebox.showinfo("Delete Product(s)", f"Deleted {deleted_count} of {len(product_ids)} selected product(s).")
        load_data()

    load_data()


    
def DailySales():
    refreshSection()
    headText.config(text="DAILY SALES")

    daily_frame = Frame(section, bg="#D9D9D9")
    daily_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ===== CONTROL PANEL =====
    top_bar = Frame(daily_frame, bg="#D9D9D9")
    top_bar.pack(fill="x", pady=(0, 8))

    Button(top_bar, text="Refresh", font=("Arial", 10, "bold"), command=lambda: load_data()).pack(side="left", padx=5)


    _ = create_search_bar(top_bar, lambda keyword: search_summary(keyword), text = "Search Date:")

    msg_label = Label(daily_frame, text="", bg="#D9D9D9", fg="blue", anchor="w")
    msg_label.pack(fill="x", pady=(2, 0))

    # ===== TREEVIEW TABLE =====
    tree_frame = Frame(daily_frame, bg="#D9D9D9")
    tree_frame.pack(fill="both", expand=True)

    display_headers = ["Date", "Total Sales"]
    
    tree = TreeView(tree_frame, display_headers, width=150)

    # ===== STORE CURRENT DATA =====
    all_data = []

    # ===== LOAD DATA =====
    def load_data():
        nonlocal all_data
        tree.delete(*tree.get_children())
        success, result = DailyFinancials.summarize_daily_sales(db)
        if not success:
            msg_label.config(text=result, fg="red")
            return

        all_data = result  # store for searching

        for row in result:
            tree.insert("", "end", values=row)
        msg_label.config(text=f"{len(result)} day(s) loaded.", fg="green")

    # ===== SEARCH FUNCTION =====
    def search_summary(keyword):
        keyword = keyword.lower()
        tree.delete(*tree.get_children())

        if not keyword:
            for row in all_data:
                tree.insert("", "end", values=row)
            msg_label.config(text="Showing all days.", fg="blue")
            return

        filtered = [r for r in all_data if keyword in str(r[0]).lower()]  # search by date only

        for row in filtered:
            tree.insert("", "end", values=row)

        msg_label.config(
            text=f"{len(filtered)} result(s) found for '{keyword}'." if filtered else f"No results for '{keyword}'.",
            fg="green" if filtered else "red"
        )

    load_data()

def MonthlySales(): #may bug sa show error sa pag aadd
    refreshSection()
    headText.config(text="MONTHLY FINANCIALS")

    fin_frame = Frame(section, bg="#D9D9D9")
    fin_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ===== CONTROL PANEL =====
    top_bar = Frame(fin_frame, bg="#D9D9D9")
    top_bar.pack(fill="x", pady=(0, 8))

    Button(top_bar, text="Refresh", font=("Arial", 10, "bold"), command=lambda: load_data()).pack(side="left", padx=5)
    Button(top_bar, text="Add/Update Taxes & Expenses", font=("Arial", 10, "bold"), command=lambda: add_taxes_expenses()).pack(side="left", padx=5)

    _ = create_search_bar(top_bar, lambda keyword: search_financial(keyword), text="Search Month:")

    msg_label = Label(fin_frame, text="", bg="#D9D9D9", fg="blue", anchor="w")
    msg_label.pack(fill="x", pady=(2, 0))

    # ===== TREEVIEW TABLE =====
    tree_frame = Frame(fin_frame, bg="#D9D9D9")
    tree_frame.pack(fill="both", expand=True)

    display_headers = [
        "Month", "Sales", "Capital", "Gross Profit",
        "Expenses", "Taxes", "Operating Profit", "Net Profit"
    ]

    tree = TreeView(tree_frame, display_headers, width=130)

    all_data = []

    # ===== LOAD DATA =====
    def load_data():
        nonlocal all_data
        tree.delete(*tree.get_children())
        success, result = Financials.calculate_monthly_financials(db)
        if not success:
            msg_label.config(text=result, fg="red")
            return

        all_data = result
        for row in result:
            values = [
                row["month"], row["total_sales"], row["total_capital"],
                row["gross_profit"], row["operating_expenses"], row["taxes"],
                row["operating_profit"], row["net_profit"]
            ]
            tree.insert("", "end", values=values)
        msg_label.config(text=f"{len(result)} month(s) loaded.", fg="green")

    # ===== SEARCH FUNCTION =====
    def search_financial(keyword):
        keyword = keyword.lower()
        tree.delete(*tree.get_children())
        filtered = []

        for row in all_data:
            if keyword in str(row["month"]).lower():
                filtered.append(row)

        for row in filtered:
            values = [
                row["month"], row["total_sales"], row["total_capital"],
                row["gross_profit"], row["operating_expenses"], row["taxes"],
                row["operating_profit"], row["net_profit"]
            ]
            tree.insert("", "end", values=values)

        if keyword:
            msg_label.config(
                text=f"{len(filtered)} result(s) found for '{keyword}'." if filtered else f"No results for '{keyword}'.",
                fg="green" if filtered else "red"
            )
        else:
            msg_label.config(text="Showing all months.", fg="blue")

    # ===== ADD/UPDATE TAXES & EXPENSES =====
    def add_taxes_expenses():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Month", "Please select a month to update.")
            return

        item = tree.item(selected[0])
        month = item['values'][0]

        # Find existing data
        row_data = next((row for row in all_data if row["month"] == month), None)
        if not row_data:
            messagebox.showerror("Error", "Selected month data not found.")
            return

        dialog = DialogBox(f"Add Taxes & Expenses - {month}", gui)

        fields = [
            ("Month (YYYY-MM)", month),
            ("Operating Expenses", str(row_data["operating_expenses"])),
            ("Taxes", str(row_data["taxes"]))
        ]
        entries = {}
        for label, default in fields:
            row = Frame(dialog)
            row.pack(fill="x", padx=10, pady=4)
            Label(row, text=label, width=20, anchor="w").pack(side="left")
            ent = Entry(row)
            ent.insert(0, default)
            ent.pack(side="left", fill="x", expand=True)
            entries[label] = ent

            def save_data():
                try:
                    # Get raw text first
                    exp_text = entries["Operating Expenses"].get().strip()
                    tax_text = entries["Taxes"].get().strip()

                    # Check for empty inputs
                    if not exp_text or not tax_text:
                        raise ValueError("Expenses and Taxes cannot be empty.")
                    if not exp_text.isdigit() or not tax_text.isdigit():
                        raise ValueError("Expenses and Taxes must be numeric values.")
                    # Convert to float
                    expenses = float(exp_text)
                    taxes = float(tax_text)

                    # Check for negative values
                    if expenses < 0 or taxes < 0:
                        raise ValueError("Expenses and Taxes cannot be negative.")

                    # Calculate and update monthly financials
                    success, results = Financials.calculate_monthly_financials(db, month, expenses, taxes)
                    if success:
                        messagebox.showinfo("Data Updated", "Additional Expenses and Taxes added successfully.")
                        dialog.destroy()
                        load_data()
                    else:
                        messagebox.showerror("Error", results)

                except ValueError as e:
                    messagebox.showerror("Input Error", str(e))
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        Button(dialog, text="Save Data", command=save_data).pack(pady=10)

    load_data()



def Suppliers():
    refreshSection()
    headText.config(text="SUPPLIERS")
    
    sup_frame = Frame(section, bg="#D9D9D9")
    sup_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ===== CONTROL PANEL =====
    top_bar = Frame(sup_frame, bg="#D9D9D9")
    top_bar.pack(fill="x", pady=(0, 8))

    buttons = [
    ("Add Supplier", lambda: add_supplier_dialog()),
    ("Edit Selected", lambda: edit_selected_dialog()),
    ("Delete Selected", lambda: delete_selected()),
    ("Refresh", lambda: load_data())
    ]
    create_control_panel(top_bar, buttons)

    # ===== SEARCH BAR =====
    _ = create_search_bar(top_bar, lambda keyword: search_supplier(keyword), text = "Search Supplier Info:")

    msg_label = Label(sup_frame, text="", bg="#D9D9D9", fg="blue", anchor="w")
    msg_label.pack(fill="x", pady=(2, 0))

    # ===== TREEVIEW TABLE =====
    tree_frame = Frame(sup_frame, bg="#D9D9D9")
    tree_frame.pack(fill="both", expand=True)

    headers = ["supplier_id", "supplier_name", "contact_person", "contact_number", "email", "address"]
    display_headers = ["Supplier ID", "Name", "Contact Person", "Contact Number", "Email", "Address"]

    tree = TreeView(tree_frame, display_headers, width=150)

    # ===== BACKEND PROXY =====
    def _supplier_proxy():
        return Supplier("temp", "temp", "123", "temp@mail.com", "temp address")

    # ===== LOAD DATA =====
    def load_data():
        try:
            tree.delete(*tree.get_children())
            proxy = _supplier_proxy()
            res = proxy.view_method(db, choice="all")

            if isinstance(res, str):
                msg_label.config(text=res, fg="red")
                return

            for row in res:
                tree.insert("", "end", values=[row.get(h, "") for h in headers])
            msg_label.config(text=f"{len(res)} supplier(s) loaded.", fg="green")
        except Exception as e:
            msg_label.config(text=f"Error loading data: {e}", fg="red")

    # ===== SEARCH SUPPLIER =====
    def search_supplier(keyword):
        keyword = keyword.strip()
        tree.delete(*tree.get_children())
        proxy = _supplier_proxy()
        res = proxy.view_method(db, choice="all")

        if not keyword:
            for row in res:
                tree.insert("", "end", values=[row.get(h, "") for h in headers])
            msg_label.config(text="Showing all suppliers.", fg="blue")
            return

        filtered = [
            item for item in res
            if keyword.lower() in str(item.get("supplier_name", "")).lower()
            or keyword.lower() in str(item.get("contact_person", "")).lower()
            or keyword.lower() in str(item.get("email", "")).lower()
        ]

        for row in filtered:
            tree.insert("", "end", values=[row.get(h, "") for h in headers])

        msg_label.config(
            text=f"{len(filtered)} result(s) found for '{keyword}'." if filtered else f"No results for '{keyword}'.",
            fg="green" if filtered else "red"
        )

    # ===== ADD SUPPLIER =====
    def add_supplier_dialog():
        dialog = DialogBox("Add New Supplier", gui)

        fields = [
            ("Supplier Name", ""),
            ("Contact Person", ""),
            ("Contact Number", ""),
            ("Email", ""),
            ("Address", "")
        ]
        entries = {}
        for label, default in fields:
            row = Frame(dialog)
            row.pack(fill="x", padx=10, pady=4)
            Label(row, text=label, width=20, anchor="w").pack(side="left")
            ent = Entry(row)
            ent.insert(0, default)
            ent.pack(side="left", fill="x", expand=True)
            entries[label] = ent

        def save_new():
            try:
                sname = entries["Supplier Name"].get().strip()
                cperson = entries["Contact Person"].get().strip()
                cnum = entries["Contact Number"].get().strip()
                email = entries["Email"].get().strip()
                addr = entries["Address"].get().strip()

                sup = Supplier(sname, cperson, cnum, email, addr)
                msg = sup.add_method(db)
                messagebox.showinfo("Add Supplier", msg)
                dialog.destroy()
                load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(dialog, text="Save Supplier", command=save_new).pack(pady=10)

    def edit_selected_dialog():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Edit", "Select a supplier first.")
            return
        row_values = tree.item(sel[0], "values")
        supplier_id = row_values[0]

        proxy = _supplier_proxy()
        result = proxy.view_method(db, choice="one", supplier_id=supplier_id)
        if isinstance(result, str):
            messagebox.showerror("Error", result)
            return
        supplier = result[0]

        dialog = DialogBox(f"Edit Supplier #{supplier_id}", gui)

        editable_fields = ["supplier_name", "contact_person", "contact_number", "email", "address"]
        entries = {}
        for field in editable_fields:
            row = Frame(dialog)
            row.pack(fill="x", padx=10, pady=4)
            Label(row, text=field.replace("_", " ").title(), width=20, anchor="w").pack(side="left")
            ent = Entry(row)
            ent.insert(0, str(supplier.get(field, "")))
            ent.pack(side="left", fill="x", expand=True)
            entries[field] = ent

        def save_edit():
            try:
                updates = {}
                for f, entry in entries.items():
                    val = entry.get().strip()
                    if val != str(supplier.get(f, "")) and val != "":
                        updates[f] = val

                if not updates:
                    messagebox.showinfo("Edit", "No changes detected.")
                    return

                proxy = _supplier_proxy()
                msg = proxy.update_method(db, supplier_id, updates)
                messagebox.showinfo("Update Successful", msg)
                dialog.destroy()
                load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(dialog, text="Save Changes", command=save_edit).pack(pady=10)

    def delete_selected():
        sel = tree.selection()  # Get all selected rows
        if not sel:
            messagebox.showwarning("Delete", "Select at least one supplier to delete.")
            return

        # Collect all selected supplier IDs
        supplier_ids = []
        for iid in sel:
            row_values = tree.item(iid, "values")
            supplier_id = row_values[0]  # Assuming first column is supplier_id
            supplier_ids.append(supplier_id)

        # Ask for confirmation (FIX: used supplier_ids, not supplier_id)
        if not messagebox.askyesno("Confirm", f"Delete {len(supplier_ids)} supplier(s)?"):
            return

        proxy = _supplier_proxy()
        deleted_count = 0

        for sid in supplier_ids:
            msg = proxy.delete_method(sid, db)
            if "success" in msg.lower():
                deleted_count += 1

        messagebox.showinfo(
            "Delete Supplier(s)",
            f"Deleted {deleted_count} of {len(supplier_ids)} selected supplier(s)."
        )

        load_data()
    
    load_data()


  
def Customer():
    refreshSection()
    
    headText.config(text="CUSTOMERS")
    Label(section, text="CUSTOMERS", font=("Arial", 20, "bold")).pack()
def OrderHistory():
    refreshSection()
    headText.config(text="ORDER HISTORY")

    # ===== MAIN FRAME =====
    hist_frame = Frame(section, bg="#D9D9D9")
    hist_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ===== CONTROL PANEL =====
    top_bar = Frame(hist_frame, bg="#D9D9D9")
    top_bar.pack(fill="x", pady=(0, 8))

    Button(top_bar, text="Refresh", font=("Arial", 10, "bold"), command=lambda: load_data()).pack(side="left", padx=5)

    # ===== SEARCH BAR =====
    _ = create_search_bar(top_bar, lambda keyword: search_orders(keyword), text = "Search Orders:")

    msg_label = Label(hist_frame, text="", bg="#D9D9D9", fg="blue", anchor="w")
    msg_label.pack(fill="x", pady=(2, 0))

    # ===== TREEVIEW TABLE =====
    tree_frame = Frame(hist_frame, bg="#D9D9D9")
    tree_frame.pack(fill="both", expand=True)

    display_headers = ["Order ID", "Date", "Customer","Contact","Address", "Product", "Price", "Qty", "Total"]
    tree = TreeView(tree_frame, display_headers, width=120)

    # ===== STORE CURRENT DATA =====
    all_data = []

    # ===== LOAD DATA =====
    def load_data():
        nonlocal all_data
        tree.delete(*tree.get_children())
        success, result = DailyFinancials.fetch_orders_report(db)
        if not success:
            msg_label.config(text=result, fg="red")
            return

        all_data = result  # store for searching
        for row in result:
            tree.insert("", "end", values=row)
        msg_label.config(text=f"{len(result)} record(s) loaded.", fg="green")

    # ===== SEARCH FUNCTION =====
    def search_orders(keyword):
        keyword = keyword.lower()
        tree.delete(*tree.get_children())

        if not keyword:
            for row in all_data:
                tree.insert("", "end", values=row)
            msg_label.config(text="Showing all orders.", fg="blue")
            return

        filtered = [
            r for r in all_data
            if keyword in str(r[2]).lower()  # customer_name
            or keyword in str(r[3]).lower()  # product_name
            or keyword in str(r[1]).lower()  # order_date
        ]

        for row in filtered:
            tree.insert("", "end", values=row)

        msg_label.config(
            text=f"{len(filtered)} result(s) found for '{keyword}'." if filtered else f"No results for '{keyword}'.",
            fg="green" if filtered else "red"
        )

    load_data()
    
def logCond(username, password_input):
    try:
        user = Users.login(db, username)

        # ADMIN CHECK
        if username == "admin" and password_input == "test1234":
            messagebox.showinfo("Admin", "Welcome, Admin")
            adminPanel()
            return
        
        if not user:
            messagebox.showerror("Wrong Login", "Invalid username or password")
            return


        # unpack values properly
        db_username, db_encrypted_password, fullname = user

        # ensure password is bytes
        if isinstance(db_encrypted_password, str):
            db_encrypted_password = db_encrypted_password.encode()

        # load Fernet key
        with open(".env/secret.key", "rb") as key_file:
            key = key_file.read()

        f = Fernet(key)
        decrypted_password = f.decrypt(db_encrypted_password).decode()

        # password match?
        if password_input == decrypted_password:
            messagebox.showinfo("User", f"Welcome back, {fullname}")
            UserPanel()
        else:
            messagebox.showerror("Wrong Login", "Invalid username or password")

    except Exception as e:
        print("DEBUG ERROR:", e)
        messagebox.showerror("Error", f"Something went wrong: {e}")

def SignUpToDatabase(username, password, fullname, contact_number, gender, age, address, entries, db = db):
    try:
        Users.validate_signup(
            username, password, fullname, contact_number, gender, age, address
        )
        
        try:
            with open(".env/secret.key", "rb") as key_file:
                key = key_file.read()
        except FileNotFoundError:
            raise FileNotFoundError("Encryption key not found!")

        f = Fernet(key)
        encrypted_password = f.encrypt(password.encode())

        # --- Create User Object (MATCHES your class order) ---
        user = Users(
            username=username,
            password=encrypted_password,
            fullname=fullname.title(),
            contact_number=contact_number,
            age=age,  
            gender=gender.upper(),
            address=address.title()
        )

        # --- Save to DB ---
        user.enter_to_db(db)

        # --- Success Message ---
        messagebox.showinfo("Success", f"Hello, {fullname.title()}, your account was created successfully!")

        UserPanel()
        return True

    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return False
    except FileNotFoundError as e:
        messagebox.showerror("Error", str(e))
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong: {e}")
        return False

def LogInPage():
    clearWindow()
    gui.geometry("700x500")
    header = Frame(gui,
                   bg="orange",
                   height=100 )
    header.pack(fill="x")

    lOne = Label(header,
                text="J&J HARDWARE SUPPLIES",
                font=("Arial", 20, "bold"),
                bg="orange")
    lOne.pack(padx=30,pady=30)

    section = Frame(gui, bg="grey")
    section.pack(fill="both", expand=True)
    Label(section,text='LOGIN',bg="grey", font=('Arail',30,'bold')).pack()
    Label(section,text='',bg="grey").pack()

    unL = Label(section,
                text="Username",
                font=("Arial",15,"bold"),
                bg="grey",
                fg="white")
    unL.pack()
    un = Entry(section,
               font=("Arial",15,"bold"))
    un.pack()
    pwL = Label(section,
                text="Password",
                font=("Arial",15,"bold"),
                bg="grey",
                fg="white")
    pwL.pack()
    pw = Entry(section, font=("Arial",15,"bold"), show='*')
    pw.pack()

    check_var = BooleanVar()

    checkbox = Checkbutton(
        section,
        text="Show Password",
        bg="grey",
        activebackground="grey",
        font=("Arial", 10),
        variable=check_var,
        command=lambda: pw.config(show='' if check_var.get() else '*')
    )

    # Place checkbox normally (below the button)
    checkbox.pack(pady=5)
    
    btLog = Button(
        section,
        text="Login",
        font=("Arial",15,"bold"),
        command=lambda: logCond(un.get(), pw.get())
    )
    btLog.pack(pady=15)

    signUpText = Label(section, text="Don't have an account? Sign up", fg="blue",bg= "grey", cursor="hand2", font=("Arial", 12, "underline"))
    signUpText.pack(pady=5)
    signUpText.bind("<Button-1>", lambda e: createAccount())
def createAccount():
    clearWindow()
    gui.geometry("700x800")
    
    header = Frame(gui, bg="orange", height=100)
    header.pack(fill="x")

    lOne = Label(header,
                 text="J&J HARDWARE SUPPLIES",
                 font=("Arial", 20, "bold"),
                 bg="orange")
    lOne.pack(padx=30, pady=30)

    section = Frame(gui, bg="grey")
    section.pack(fill="both", expand=True)
    Label(section, text='SIGN UP', bg="grey", font=('Arial', 30, 'bold')).pack()
    Label(section, text='', bg="grey").pack()

    # Create labels and entries
    entries = {}
    fields = [
        ("Username", "sUn"),
        ("Password", "SpW"),
        ("Full Name", "fn"),
        ("Contact Number", "cont"),
        ("Gender", "gender"),
        ("Age", "age"),
        ("Address", "address")
    ]
    
    for text, key in fields:
        Label(section, text=text, font=("Arial", 10, "bold"), bg="grey", fg="black").pack()
        show_char = "*" if key == "SpW" else ""
        e = Entry(section, font=("Arial", 10, "bold"), show=show_char)
        e.pack(ipadx = 50, ipady=5)
        entries[key] = e
        

    def signup_command():

        age_val = int(entries["age"].get()) if entries["age"].get().isdigit() else 0
        SignUpToDatabase(
                username=entries["sUn"].get(),
                password=entries["SpW"].get(),
                fullname=entries["fn"].get(),
                contact_number=entries["cont"].get(),
                gender=entries["gender"].get(),
                age=age_val,
                address=entries["address"].get(),
                entries=entries
            )

    check_var = BooleanVar()

    checkbox = Checkbutton(
            section,
            text="Show Password",
            bg = "grey",
            activebackground="grey",
            font=("Arial", 10),
            variable=check_var,
            command=lambda: entries["SpW"].config(show='' if check_var.get() else '*')
        )

        # Place checkbox normally (below the button)
    checkbox.pack(pady=5)
    
    SuBtn = Button(section, text="SIGNUP", font=("Arial", 15, "bold"), command=signup_command)
    SuBtn.pack(padx=15, pady=10)


def SideButton(y,z):
    def onHov(a):
        a.widget["background"] = "#FFFFFF"
        a.widget["foreground"]= "black"
    def unHov(a):
        a.widget["background"] = "#3A3A3A"
        a.widget["foreground"]= "#FFFFFF"
    btn = Button(sideDash,
          text=y,
          fg="white",
          width=15,
          font=("Arial",18, 'bold'),
          bg="#3A3A3A",
          command=z)
    btn.pack(pady=8,padx=4)
    btn.bind("<Enter>", onHov)
    btn.bind("<Leave>", unHov)
def adminPanel():
    global section,lOne,headText,sideDash
    clearWindow()
    gui.geometry("1200x650")
    sideDash = Frame(gui,
                    bg="#2F2F2F",
                    width=200,
                    border=1)
    sideDash.pack(side="left",
    
                  fill='y')

    greetLOne = Label(sideDash,
                    text="Hello, Admin!",
                    fg="#FFFFFF",
                    width=12,
                    font=("Arial",20, 'bold'),
                    bg="#2F2F2F")
    
    greetLOne.pack(padx=5,pady=8)
    Label(sideDash, text='',bg="#2F2F2F").pack(pady=5)
    btText = ['DASHBOARD','INVENTORY', 'DAILY SALES', 'MONTHLY SALES','SUPPLIERS', 'CUSTOMERS', 'ORDER HISTORY', 'LOGOUT']
    btCommads = [DashBoard, Inventory, DailySales, MonthlySales, Suppliers, Customer, OrderHistory, LogInPage]
    for i in range(8):
        SideButton(btText[i],btCommads[i])
    
    header = Frame(gui,
                bg="#F28C28",
                height=100 )
    header.pack(fill="x")
    
    dashHead = Frame(gui,
                    bg="blue",
                    height=20 )
    dashHead.pack(fill="x")
    
    headText = Label(dashHead,
        text="ADMIN",
        font=("Arial", 12, "bold"),
        bg="blue")
    headText.pack(padx=30,pady=15)
    
    lOne = Label(header,
                text="J&J HARDWARE SUPPLIES",
                font=("Segoe UI", 20, "bold"),
                bg="#F28C28")
    lOne.pack(padx=30,pady=30)

    section = Frame(gui,
                    bg="#D9D9D9")
    section.pack(fill="both",
                expand=True)
    
    Label(section,
          text="Welcome Back, Admin",
          font=("Arial", 40, "bold"),
          bg="#D9D9D9").pack(pady=50)
def UserPanel():
    clearWindow()
    gui.geometry("1000x700")

    # ===================== HEADER =====================
    header = Frame(gui, bg="orange", height=100)
    header.pack(fill="x")
    Label(header, text="J&J HARDWARE SUPPLIES",
          font=("Arial", 22, "bold"),
          bg="orange").pack(padx=30, pady=30)

    # ===================== NAVIGATION =====================
    navSec = Frame(gui, bg="grey", height=40)
    navSec.pack(fill="x")

    Button(navSec, text="<-", width=8, command=LogInPage).grid(row=0, column=0, padx=5)
    Button(navSec, text="Home", width=10, command=UserHomePage).grid(row=0, column=1, padx=5)
    Button(navSec, text="Orders", width=10).grid(row=0, column=2, padx=5)
    Button(navSec, text="Profile", width=10).grid(row=0, column=3, padx=5)
    userSec = Frame(gui,bg="grey")
    userSec.pack(fill="both",expand=True)
    Label(userSec,text="HELLOOO", bg="grey",font=("Arial",50,"bold")).pack()
def UserHomePage():
    clearWindow()
    gui.geometry("1000x700")

    # ===================== HEADER =====================
    header = Frame(gui, bg="orange", height=100)
    header.pack(fill="x")
    Label(header, text="J&J HARDWARE SUPPLIES",
          font=("Arial", 22, "bold"),
          bg="orange").pack(padx=30, pady=30)

    # ===================== NAVIGATION =====================
    navSec = Frame(gui, bg="grey", height=40)
    navSec.pack(fill="x")

    Button(navSec, text="<-", width=8, command=LogInPage).grid(row=0, column=0, padx=5)
    Button(navSec, text="Home", width=10).grid(row=0, column=1, padx=5)
    Button(navSec, text="Orders", width=10).grid(row=0, column=2, padx=5)
    Button(navSec, text="Profile", width=10).grid(row=0, column=3, padx=5)
    # ===================== SCROLLABLE AREA =====================
    container = Frame(gui)
    container.pack(fill="both", expand=True)

    canvas = Canvas(container, bg="#f0f0f0", highlightthickness=0)
    scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = Frame(canvas, bg="#f0f0f0")

    # Connect scroll region
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ===================== MOUSE SCROLL HANDLER =====================
    def _on_mousewheel(event):
        if event.delta:  # Windows / Mac
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:  # Linux
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

    # ===================== LOAD ITEMS FROM DATABASE =====================
    def load_items():
        conn = sqlite3.connect("./Hardware and Construction.db")
        c = conn.cursor()
        c.execute("SELECT product_name, srp FROM products")
        items = c.fetchall()
        conn.close()
        return items

    products = load_items()

    # ===================== RENDER PRODUCT CARDS =====================
    def render_items(event=None):
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        canvas_width = canvas.winfo_width()
        min_width = 260
        padding = 20

        cols = max(1, canvas_width // (min_width + padding))
        col = row = 0

        for name, price in products:
            card = Frame(scroll_frame, bg="white", bd=1, relief="solid")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            Label(card, text=name, bg="white",
                  font=("Arial", 13, "bold")).pack(anchor="nw", padx=10, pady=5)

            Label(card, text=f"₱{price}", bg="white",
                  font=("Arial", 11)).pack(anchor="nw", padx=10)

            Button(card, text="Add to Cart",
                   bg="#7a0000", fg="white").pack(anchor="nw", padx=10, pady=10)

            col += 1
            if col >= cols:
                col = 0
                row += 1

        for c in range(cols):
            scroll_frame.grid_columnconfigure(c, weight=1)

    # Initial render
    render_items()

    # Re-render on resize
    canvas.bind("<Configure>", render_items)

if __name__ == "__main__":
    UserPanel()
    gui.mainloop()