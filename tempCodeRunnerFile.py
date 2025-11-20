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
                lifespan = int(lifespan) if lifespan else None

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