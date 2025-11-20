from datetime import datetime
import sqlite3
from abc import ABC, abstractmethod

class CRUD(ABC):
    @abstractmethod
    def add_method(self, db):
        pass
    
    @abstractmethod
    def delete_method(self, id, db):
        pass
    
    @abstractmethod
    def update_method(self, db, id, updates):
        pass
    
    @abstractmethod
    def view_method(self, db, choice, name=None, product_id=None):
        pass

class Database:
    def __init__(self, database_name = "Hardware and Construction.db"):
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('PRAGMA foreign_keys = ON')


class Product(CRUD):
    def __init__(self, product_name, category_id, type_id, quantity, capital, supplier_id,
                 date_received=None, expiration_date=None, lifespan=None):

        if not product_name or not product_name.strip():
            raise ValueError("Product name cannot be empty.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if capital < 0:
            raise ValueError("Capital must be non-negative.")
        if product_name.isdigit():
            raise ValueError("Product name cannot be numbers.")

        self.product_name = product_name.strip()
        self.category_id = category_id
        self.type_id = type_id
        self.quantity = quantity
        self.capital = capital
        self.srp = round(self.capital * 1.25, 2)
        self.total_capital = round(self.capital * self.quantity, 2)
        self.supplier_id = supplier_id
        self.date_received = date_received or datetime.now().date()
        self.expiration_date = expiration_date
        self.lifespan = lifespan

    def fk_exists(self, db, table, col, value):
        db.cursor.execute(f"SELECT {col} FROM {table} WHERE {col} = ?", (value,))
        return db.cursor.fetchone() is not None
    
    def add_method(self, db: Database):
        try:
            db.cursor.execute("""
                SELECT * FROM products
                WHERE product_name = ? AND category_id = ? AND type_id = ? AND supplier_id = ?
            """, (self.product_name, self.category_id, self.type_id, self.supplier_id))

            if db.cursor.fetchone():
                return f"Product '{self.product_name}' already exists. Use Edit instead."

            db.cursor.execute("""
                INSERT INTO products (
                    product_name, category_id, type_id, quantity,
                    capital, srp, supplier_id, date_received,
                    expiration_date, lifespan, total_capital
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.product_name, self.category_id, self.type_id, self.quantity,
                self.capital, self.srp, self.supplier_id, self.date_received,
                self.expiration_date, self.lifespan, self.total_capital
            ))

            db.conn.commit()
            return f"Product '{self.product_name}' added successfully."

        except sqlite3.IntegrityError as e:
            return f"Database error: {e}"

    def delete_method(self, product_id, db):
        try:
            if not str(product_id).isdigit():
                raise ValueError("Product ID must be a number.")

            db.cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            if not db.cursor.fetchone():
                return f"No product found with ID {product_id}."

            db.cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            db.conn.commit()
            return f"Product with ID {product_id} deleted successfully."

        except Exception as e:
            return f"Error deleting product: {str(e)}"

    def update_method(self, db: Database, product_id, updates: dict):
        try:
            if not updates:
                raise ValueError("No updates provided.")

            if not str(product_id).isdigit():
                raise ValueError("Product ID must be a number.")

            allowed = [
                "product_name", "category_id", "type_id", "quantity",
                "capital", "srp", "supplier_id", "date_received",
                "expiration_date", "lifespan", "total_capital"
            ]

            float_columns = ["capital", "srp"]
            int_columns = ["quantity", "category_id", "type_id", "supplier_id", "lifespan"]

            # Convert types
            for col in list(updates.keys()):
                if col not in allowed:
                    return f"Invalid column name: {col}"

                if col in float_columns:
                    updates[col] = float(updates[col])

                elif col in int_columns:
                    updates[col] = int(updates[col])

            # -------- CENTRALIZED FOREIGN KEY VALIDATION --------
            if "supplier_id" in updates:
                if not self.fk_exists(db, "supplier", "supplier_id", updates["supplier_id"]):
                    return "Supplier ID does not exist."

            if "category_id" in updates:
                if not self.fk_exists(db, "category", "category_id", updates["category_id"]):
                    return "Category ID does not exist."

            if "type_id" in updates:
                if not self.fk_exists(db, "product_type", "type_id", updates["type_id"]):
                    return "Type ID does not exist."
            # -----------------------------------------------------

            # Auto-update SRP when capital changes
            if "capital" in updates:
                updates["srp"] = round(updates["capital"] * 1.25, 2)

            # Get product for total capital calculation
            db.cursor.execute(
                "SELECT quantity, capital FROM products WHERE product_id = ?",
                (product_id,)
            )
            product = db.cursor.fetchone()

            if not product:
                return f"No product found with ID {product_id}."

            old_qty, old_cap = product

            qty = updates.get("quantity", old_qty)
            cap = updates.get("capital", old_cap)

            updates["total_capital"] = round(qty * cap, 2)

            # Build update query dynamically
            set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
            values = list(updates.values()) + [product_id]

            db.cursor.execute(f"UPDATE products SET {set_clause} WHERE product_id = ?", values)
            db.conn.commit()

            return f"Product with ID {product_id} updated successfully."

        except Exception as e:
            return f"Database error: {str(e)}"



    def view_method(self, db, choice="all", name=None, product_id=None):
        try:
            # --- Base query ---
            base_query = """
            SELECT 
                p.product_id,
                p.product_name,
                c.category_name,
                t.type_name,
                p.quantity,
                p.capital,
                p.srp,
                p.total_capital,
                s.supplier_name,
                p.date_received,
                p.expiration_date,
                p.lifespan
            FROM products p
            JOIN category c ON p.category_id = c.category_id
            JOIN product_type t ON p.type_id = t.type_id
            JOIN supplier s ON p.supplier_id = s.supplier_id
            """

            params = ()

            # --- Filtering for one product ---
            if choice == "one":
                if product_id:
                    base_query += " WHERE p.product_id = ?"
                    params = (product_id,)
                elif name:
                    base_query += " WHERE p.product_name LIKE ?"
                    params = (f"%{name}%",)
                else:
                    return "Please provide product ID or name."

            db.cursor.execute(base_query, params)
            rows = db.cursor.fetchall()

            columns = [
                "product_id", "product_name", "category_name",
                "type_name", "quantity", "capital",
                "srp", "total_capital", "supplier_name",
                "date_received", "expiration_date", "lifespan"
            ]

            formatted_rows = []
            for r in rows:
                r = list(r)

                # Format quantity (2 decimals + commas)
                r[4] = f"{r[4]:,.2f}"

                # Format capital, srp, total_capital with peso sign + commas + 2 decimals
                r[5] = f"₱{r[5]:,.2f}"  # capital
                r[6] = f"₱{r[6]:,.2f}"  # srp
                r[7] = f"₱{r[7]:,.2f}"  # total_capital

                formatted_rows.append(dict(zip(columns, r)))

            return formatted_rows if formatted_rows else "No product found."

        except Exception as e:
            return f"Database error: {str(e)}"


class Supplier(CRUD):
    def __init__(self, supplier_name, contact_person, contact_number, email, address):
    
        if not supplier_name or not supplier_name.strip():
            raise ValueError("Supplier name cannot be empty.")
        if not contact_person or not contact_person.strip():
            raise ValueError("Contact person cannot be empty.")
        if not contact_number or not contact_number.strip():
            raise ValueError("Contact number cannot be empty.")
        if not address or not address.strip():
            raise ValueError("Address cannot be empty.")
        if not str(contact_number).isdigit():
            raise ValueError("Contact number must contain only digits.")
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Invalid email format. Must contain '@' and a domain (e.g., example@mail.com).")

        self.supplier_name = supplier_name.strip()
        self.contact_person = contact_person.strip()
        self.contact_number = contact_number.strip()
        self.email = email.strip()
        self.address = address.strip()
 
    def add_method(self, db):
        try:
            db.cursor.execute("""
                INSERT INTO supplier (
                    supplier_name, contact_person, contact_number, email, address
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                self.supplier_name, self.contact_person, self.contact_number, self.email, self.address
            ))
            db.conn.commit()
            return f"{self.supplier_name}' added successfully."
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Database error: {e}")
    
    def delete_method(self, supplier_id, db):
        try:
            if not supplier_id:
                raise ValueError("Enter the supplier ID")
            
            if not str(supplier_id).isdigit():
                raise ValueError("Supplier ID must be a number")

            db.cursor.execute("SELECT * FROM supplier WHERE supplier_id = ?", (supplier_id,))
            supplier = db.cursor.fetchone()
            
            if supplier:
                db.cursor.execute("DELETE FROM supplier WHERE supplier_id = ?", (supplier_id,))
                db.conn.commit()
                return f"Supplier with ID {supplier_id} deleted successfully."
            else:
                return f"No supplier found with ID {supplier_id}."
        except ValueError as e:
            return str(e)
        except Exception as e:
            return f"Error deleting supplier: {str(e)}"
        
    def update_method(self, db: Database, supplier_id, updates: dict):
        try:
            if not updates:
                raise ValueError("No updates provided.")

            if not str(supplier_id).isdigit():
                raise ValueError("Supplier ID must be a number.")

            allowed_columns = [
                "supplier_name", "contact_person", "contact_number",
                "email", "address"
            ]
            allowed_columns_lower = [col.lower() for col in allowed_columns]

            for col, value in updates.items():
                col_lower = col.lower()
                if col_lower not in allowed_columns_lower:
                    raise ValueError(f"Invalid column name: {col}")

                if col_lower in ["supplier_name", "contact_person", "address"]:
                    if not str(value).strip():
                        raise ValueError(f"{col.replace('_', ' ').title()} cannot be empty.")

                elif col_lower == "contact_number":
                    if not str(value).isdigit():
                        raise ValueError("Contact number must contain only digits.")

                elif col_lower == "email":
                    if "@" not in value or "." not in value.split("@")[-1]:
                        raise ValueError("Invalid email format. Must contain '@' and a domain (e.g., example@mail.com).")

            
            db.cursor.execute("SELECT * FROM supplier WHERE supplier_id = ?", (supplier_id,))
            existing = db.cursor.fetchone()
            if not existing:
                return f"No supplier found with ID {supplier_id}."

            
            set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
            values = list(updates.values())
            values.append(supplier_id)

            query = f"UPDATE supplier SET {set_clause} WHERE supplier_id = ?"
            db.cursor.execute(query, values)
            db.conn.commit()

            return f"Supplier with ID {supplier_id} updated successfully."

        except ValueError as e:
            return str(e)
        except sqlite3.Error as e:
            return f"Database error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
        
    def view_method(self, db, choice="all", name = None, supplier_id = None):
        try:
            db.cursor.execute("PRAGMA table_info(supplier)")
            columns = [col[1] for col in db.cursor.fetchall()]

            if choice.lower() not in ["all", "one"]:
                raise ValueError("Choice must be either 'all' or 'one'.")

            if choice.lower() == "one":
                if supplier_id is not None:
                    if not str(supplier_id).isdigit():
                        raise ValueError("Supplier ID must be numeric.")
                    db.cursor.execute("SELECT * FROM supplier WHERE supplier_id = ?", (supplier_id,))
                elif name:
                    db.cursor.execute("SELECT * FROM supplier WHERE supplier_name LIKE ?", (f"%{name}%",))
                else:
                    raise ValueError("Provide either 'name' or 'supplier_id' to view a supplier.")

                result = db.cursor.fetchall()
                if result:
                    return [dict(zip(columns, row)) for row in result]
                else:
                    return "No supplier found matching your criteria."

            else:
                db.cursor.execute("SELECT * FROM supplier")
                result = db.cursor.fetchall()
                if result:
                    return [dict(zip(columns, row)) for row in result]
                else:
                    return "No suppliers found in database."

        except ValueError as e:
            return str(e)
        except sqlite3.Error as e:
            return f"Database error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


class Users:
    def __init__(self, username, password, fullname, contact_number, age, gender, address):
        # Store attributes
        self.__username = username
        self.__password = password        # Encrypt before saving
        self.fullname = fullname.title()
        self.contact_number = contact_number
        self.age = age
        self.gender = gender
        self.address = address.title()
        
    def get_username(self):
        return self.__username
    
    def get_password(self):
        return self.__password
    
    def set_username(self, username):
        self.__username = username
    
    def set_password(self, password):
        self.__password = password
        
    def enter_to_db(self, db):
        try:       
            db.cursor.execute(
                """
                INSERT INTO users (username, password, fullName, contNumber, gender, age, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.__username,
                    self.__password,
                    self.fullname,
                    self.contact_number,
                    self.gender,
                    self.age,
                    self.address
                )
            )
            db.conn.commit()   # <-- FIXED (was self.db.conn, which is wrong)

        except sqlite3.IntegrityError as e:
            raise ValueError(f"Database error: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}")
    
    @staticmethod 
    def check_users(username, db):
        try:
            db.cursor.execute(
                "SELECT username FROM users WHERE username = ?",
                (username,)
            )
            row = db.cursor.fetchone()
            return True if row else False
        except sqlite3.Error as e:
            raise ValueError(f"Database error: {e}")
    
    @staticmethod
    def login(db, username):
        try:
            db.cursor.execute("SELECT username, password, fullName FROM users WHERE username = ?", (username,))
            user = db.cursor.fetchone()
            return user   
        except sqlite3.Error as e:
            raise ValueError(f"Database error: {e}")
        
    @staticmethod
    
    def validate_signup(username, password, fullname, contact_number, gender, age, address):
        # Username validation
        if not username.strip():
            raise ValueError("Username cannot be empty.")
        if username.lower() == "admin":
            raise ValueError("Cannot use username 'admin'.")

        # Password validation
        if not password.strip():
            raise ValueError("Password cannot be empty.")
        if len(password.strip()) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        # Full name validation
        if not fullname.strip():
            raise ValueError("Full name cannot be empty.")

        # Contact validation
        if not contact_number.strip() or not contact_number.isdigit():
            raise ValueError("Contact number must contain only digits.")

        # Gender validation
        if not gender.strip():
            raise ValueError("Gender is required.")
        if len(gender.strip()) > 1:
            raise ValueError("Enter \'M\' for Male and \'F\' for Female")

        # Age validation
        if age < 18:
            raise ValueError("You must be at least 18 years old to register.")

        # Address validation
        if not address.strip():
            raise ValueError("Address cannot be empty.")
        if address.isdigit():
            raise ValueError("Address cannot be a number.")

        # Check if username already exists in DB
        if Users.check_users(username, db = Database()):
            raise ValueError("Username already exists. Please choose a different username.")

        return True  # Valid


class Customers(CRUD):
    
    def __init__(self, customer_name, contact=None, address=None, db: Database = None):
        self.customer_name = customer_name.strip()
        self.contact = contact.strip() if contact else None
        self.address = address.strip() if address else None

    def add_method(self, db):
        try:
            db.cursor.execute("""
                INSERT INTO customers (customer_name, contact, address)
                VALUES (?, ?, ?)
            """, (self.customer_name, self.contact, self.address))
            db.conn.commit()
            return f"Customer '{self.customer_name}' added successfully."
        except sqlite3.IntegrityError as e:
            return f"Database error: {e}"
        except sqlite3.Error as e:
            return f"Error adding customer: {e}"

    def delete_method(self, customer_id, db):
        try:
            if not str(customer_id).isdigit():
                raise ValueError("Customer ID must be a number.")

            db.cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
            customer = db.cursor.fetchone()
            if customer:
                db.cursor.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
                db.conn.commit()
                return f"Customer with ID {customer_id} deleted successfully."
            else:
                return f"No customer found with ID {customer_id}."
        except ValueError as e:
            return str(e)
        except sqlite3.Error as e:
            return f"Database error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def update_method(self, db, customer_id, updates: dict):
        try:
            if not updates:
                raise ValueError("No updates provided.")

            if not str(customer_id).isdigit():
                raise ValueError("Customer ID must be a number.")

            allowed_columns = ["customer_name", "contact", "address"]
            for col, value in updates.items():
                if col not in allowed_columns:
                    raise ValueError(f"Invalid column name: {col}")
                if col == "customer_name" and (not value.strip() or value.isdigit()):
                    raise ValueError("Customer name cannot be empty or a number.")

            db.cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
            existing = db.cursor.fetchone()
            if not existing:
                return f"No customer found with ID {customer_id}."

            set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
            values = list(updates.values())
            values.append(customer_id)

            query = f"UPDATE customers SET {set_clause} WHERE customer_id = ?"
            db.cursor.execute(query, values)
            db.conn.commit()
            return f"Customer with ID {customer_id} updated successfully."
        except ValueError as e:
            return str(e)
        except sqlite3.Error as e:
            return f"Database error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def view_method(self, db, choice="all", name=None, customer_id=None):
        try:
            db.cursor.execute("PRAGMA table_info(customers)")
            columns = [col[1] for col in db.cursor.fetchall()]

            if choice.lower() not in ["all", "one"]:
                raise ValueError("Choice must be either 'all' or 'one'.")

            if choice.lower() == "one":
                if customer_id is not None:
                    if not str(customer_id).isdigit():
                        raise ValueError("Customer ID must be numeric.")
                    db.cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
                elif name:
                    db.cursor.execute("SELECT * FROM customers WHERE customer_name LIKE ?", (f"%{name}%",))
                else:
                    raise ValueError("Provide either 'name' or 'customer_id' to view a customer.")

                result = db.cursor.fetchall()
                if result:
                    return [dict(zip(columns, row)) for row in result]
                else:
                    return "No customer found matching your criteria."

            else:
                db.cursor.execute("SELECT * FROM customers")
                result = db.cursor.fetchall()
                if result:
                    return [dict(zip(columns, row)) for row in result]
                else:
                    return "No customers found in database."

        except ValueError as e:
            return str(e)
        except sqlite3.Error as e:
            return f"Database error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"


class Order:
    # ===== CREATE CUSTOMER =====
    def create_customer(self, customer: 'Customers', db: 'Database') -> tuple[bool, int | str]:
        try:
            db.cursor.execute("""
                SELECT customer_id FROM customers
                WHERE customer_name = ? AND contact = ? AND address = ?
            """, (customer.customer_name, customer.contact, customer.address))
            existing = db.cursor.fetchone()

            if existing:
                return True, existing[0] 

            db.cursor.execute("""
                INSERT INTO customers (customer_name, contact, address)
                VALUES (?, ?, ?)
            """, (customer.customer_name, customer.contact, customer.address))
            db.conn.commit()
            return True, db.cursor.lastrowid 
        except sqlite3.Error as e:
            return False, f"Failed to create customer: {e}"

    # ===== CREATE ORDER =====
    def create_order(self, customer_id: int, db: 'Database') -> tuple[bool, int | str]:
        try:
            order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.cursor.execute("""
                INSERT INTO orders (customer_id, order_date)
                VALUES (?, ?)
            """, (customer_id, order_date))
            db.conn.commit()
            return True, db.cursor.lastrowid
        except sqlite3.Error as e:
            return False, f"Failed to create order: {e}"

    # ===== ADD ORDER ITEM =====
    def add_order_item(self, order_id: int, product_id: int, quantity: int, db: 'Database') -> tuple[bool, str]:
        try:
            db.cursor.execute("""
                SELECT quantity FROM order_items
                WHERE order_id = ? AND product_id = ?
            """, (order_id, product_id))
            existing = db.cursor.fetchone()

            if existing:
                new_quantity = existing[0] + quantity
                db.cursor.execute("""
                    UPDATE order_items
                    SET quantity = ?
                    WHERE order_id = ? AND product_id = ?
                """, (new_quantity, order_id, product_id))
                message = f"Updated product {product_id} to quantity {new_quantity}."
            else:
                db.cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity)
                    VALUES (?, ?, ?)
                """, (order_id, product_id, quantity))
                message = f"Added product {product_id} (x{quantity}) to order {order_id}."

            db.conn.commit()
            return True, message

        except sqlite3.IntegrityError as e:
            return False, f"Integrity error: {e}"
        except sqlite3.Error as e:
            return False, f"Failed to add order item: {e}"

class DailyFinancials:
    # ===== FETCH DETAILED ORDERS =====
    @staticmethod
    def fetch_orders_report(db: 'Database') -> tuple[bool, list[tuple] | str]:
        """
        Fetches full order history for all orders.
        Returns:
            (True, list of tuples) on success
            (False, error message) on failure
        Each tuple contains:
            (order_id, order_date, customer_name, contact, address, product_name, srp, quantity, total_price)
        """
        try:
            query = """
                SELECT
                    o.order_id,
                    o.order_date,
                    c.customer_name,
                    c.contact,
                    c.address,
                    p.product_name,
                    p.srp,
                    oi.quantity,
                    (oi.quantity * p.srp) AS total_price
                FROM order_items AS oi
                INNER JOIN orders AS o ON oi.order_id = o.order_id
                INNER JOIN customers AS c ON o.customer_id = c.customer_id
                INNER JOIN products AS p ON oi.product_id = p.product_id
                ORDER BY o.order_date, o.order_id;
            """
            db.cursor.execute(query)
            rows = db.cursor.fetchall()

            formatted_rows = []
            for r in rows:
                r = list(r)
                # srp=6, total_price=8
                r[6] = f"₱{r[6]:,.2f}"         # srp
                r[8] = f"₱{r[8]:,.2f}"         # total_price
                formatted_rows.append(tuple(r))

            return True, formatted_rows

        except sqlite3.Error as e:
            return False, f"Failed to fetch order history: {e}"

    # ===== SUMMARIZE DAILY SALES =====
    @staticmethod
    def summarize_daily_sales(db: 'Database') -> tuple[bool, list[tuple] | str]:
        """
        Fetches daily sales totals.
        Returns list of tuples:
            (order_day, total_sales)
        total_sales is formatted with ₱, commas, and 2 decimals.
        """
        try:
            db.cursor.execute("""
                SELECT
                    DATE(o.order_date) AS order_day,
                    COALESCE(SUM(oi.quantity * p.srp), 0) AS total_sales
                FROM orders AS o
                LEFT JOIN order_items AS oi ON oi.order_id = o.order_id
                LEFT JOIN products AS p ON oi.product_id = p.product_id
                GROUP BY order_day
                ORDER BY order_day;
            """)
            rows = db.cursor.fetchall()
            formatted_rows = []

            for r in rows:
                order_day, total_sales = r
                formatted_total = f"₱{total_sales:,.2f}"
                formatted_rows.append((order_day, formatted_total))

            return True, formatted_rows

        except sqlite3.Error as e:
            return False, f"Failed to summarize daily sales: {e}"


class Financials:
    @staticmethod
    def calculate_monthly_financials(db: 'Database', month_to_update: str = None, operating_expenses: float = None, taxes: float = None) -> tuple:
        try:
            results = []
            if not operating_expenses:
                operating_expenses = 0.0
            if not taxes:
                taxes = 0.0
            if isinstance(operating_expenses, str):
                return False, "Operating expenses must be a numeric value."
            if isinstance(taxes, str):
                return False, "Taxes must be a numeric value."
            # Fetch monthly sales and capital
            db.cursor.execute('''
                SELECT 
                    SUBSTR(o.order_date, 1, 7) AS month,
                    SUM(oi.quantity * p.srp) AS total_sales,
                    SUM(oi.quantity * p.capital) AS total_capital
                FROM order_items AS oi
                JOIN orders AS o ON oi.order_id = o.order_id
                JOIN products AS p ON oi.product_id = p.product_id
                GROUP BY month
            ''')
            monthly_data = db.cursor.fetchall()

            for row in monthly_data:
                month, total_sales, total_capital = row
                gross_profit = total_sales - total_capital

                # Fetch existing expenses/taxes
                db.cursor.execute('''
                    SELECT operating_expenses, taxes
                    FROM monthly_financials
                    WHERE month = ?
                ''', (month,))
                existing = db.cursor.fetchone()
                current_expenses = existing[0] if existing else 0
                current_taxes = existing[1] if existing else 0

                # Determine which expenses/taxes to use
                if month_to_update and month == month_to_update:
                    op_exp = float(operating_expenses)
                    tx = float(taxes)
                else:
                    op_exp = current_expenses
                    tx = current_taxes

                operating_profit = gross_profit - op_exp
                net_profit = operating_profit - tx

                # Insert or update monthly_financials
                db.cursor.execute('''
                    INSERT INTO monthly_financials
                    (month, total_sales, total_capital, gross_profit, operating_expenses, taxes, operating_profit, net_profit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(month) DO UPDATE SET
                        total_sales = excluded.total_sales,
                        total_capital = excluded.total_capital,
                        gross_profit = excluded.gross_profit,
                        operating_expenses = ?,
                        taxes = ?,
                        operating_profit = excluded.operating_profit,
                        net_profit = excluded.net_profit
                ''', (month, total_sales, total_capital, gross_profit, op_exp, tx, operating_profit, net_profit, op_exp, tx))

                # --- Format numeric values for display ---
                formatted_result = {
                    'month': month,
                    'total_sales': f"₱{total_sales:,.2f}",
                    'total_capital': f"₱{total_capital:,.2f}",
                    'gross_profit': f"₱{gross_profit:,.2f}",
                    'operating_expenses': f"₱{op_exp:,.2f}",
                    'taxes': f"₱{tx:,.2f}",
                    'operating_profit': f"₱{operating_profit:,.2f}",
                    'net_profit': f"₱{net_profit:,.2f}"
                }

                results.append(formatted_result)

            db.conn.commit()
            return True, results

        except sqlite3.Error as e:
            return False, f"Failed to calculate monthly financials: {e}"
    
class InventoryManager(Order):
    def checkout_order(self, order_id: int, db: 'Database') -> tuple[bool, str]:
        try:
            # Get all items in this order
            db.cursor.execute("""
                SELECT product_id, quantity
                FROM order_items
                WHERE order_id = ?
            """, (order_id,))
            order_items = db.cursor.fetchall()

            if not order_items:
                return False, f"No order items found for order ID {order_id}."

            # Verify product availability
            for product_id, order_qty in order_items:
                db.cursor.execute("""
                    SELECT quantity, product_name
                    FROM products
                    WHERE product_id = ?
                """, (product_id,))
                product = db.cursor.fetchone()

                if not product:
                    return False, f"Product ID {product_id} does not exist."

                available_qty, name = product
                if available_qty < order_qty:
                    return False, f"Insufficient stock for '{name}' (ID {product_id}). Only {available_qty} left."

            # Deduct quantities safely from inventory 
            for product_id, order_qty in order_items:
                db.cursor.execute("""
                    UPDATE products
                    SET quantity = quantity - ?
                    WHERE product_id = ? AND quantity >= ?
                """, (order_qty, product_id, order_qty))

                # Check if the update actually succeeded 
                if db.cursor.rowcount == 0:
                    db.conn.rollback()
                    return False, f"Failed to update stock for product ID {product_id}. Not enough quantity."

            # Commit all changes
            db.conn.commit()
            return True, f"Checkout successful! Inventory updated for order ID {order_id}."

        except sqlite3.Error as e:
            db.conn.rollback()
            return False, f"Checkout failed: {e}"

    
if __name__ == "__main__":
    db = Order()
    dbs = Database()
    db.add_order_item(20, 1, 115, dbs)