from datetime import datetime
import sqlite3
from abc import ABC, abstractmethod

class CRUD(ABC):
    """In this class, we define the abstract methods for CRUD operations."""
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
    """
    This class manages the SQLite database connection and cursor.
    
    It supports context manager protocol for automatic commit and close.
    """

    def __init__(self):
        self.conn = sqlite3.connect("HNC_DB.db")
        self.cursor = self.conn.cursor()

    def __enter__(self):
        """
        Enter the runtime context for the Database object.

        Returns:
            Database: The current Database instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context and commit the changes to the database.

        Automatically commits any pending transaction and closes the connection.

        Args:
            exc_type (type): The exception type (if any occurred).
            exc_val (Exception): The exception instance (if any occurred).
            exc_tb (traceback): The traceback object (if any occurred).
        """
        self.conn.commit()
        self.conn.close()



class Product(CRUD):
    """
    Implements CRUD operations for products in the database.

    Inherits from the abstract base class CRUD. Provides methods to add,
    delete, update, and view products.
    """

    def __init__(self, product_name, product_type, quantity, capital, supplier,
                 date_received=None, expiration_date=None):
        """
        Initialize a Product instance.

        Args:
            product_name (str): Name of the product.
            product_type (str): Type or category of the product.
            quantity (int): Number of items in stock.
            capital (float): Cost price of the product.
            supplier (str): Supplier name.
            date_received (str, optional): Date the product was received in YYYY-MM-DD format. Defaults to today.
            expiration_date (str, optional): Expiration date if applicable.
        """
        self.product_name = product_name.strip()
        self.product_type = product_type.strip()
        self.__quantity = int(quantity)
        self.__capital = float(capital)
        self.__total_capital = round(self.capital * self.quantity, 2)
        self.srp = round(self.capital * 1.30, 2)
        self.__supplier = supplier
        self.__date_received = date_received or datetime.now().strftime("%Y-%m-%d")
        self.__expiration_date = expiration_date

    def add_method(self, db: Database):
        """
        Add this product to the database.

        """
        try:
            # Check for duplicates
            db.cursor.execute("""
                SELECT product_id FROM products
                WHERE product_name = ? AND product_type = ? AND supplier = ?
            """, (self.product_name, self.product_type, self.__supplier))
            if db.cursor.fetchone():
                return False, f"Product '{self.product_name}' already exists."

            db.cursor.execute("""
                INSERT INTO products (
                    product_name, product_type, quantity,
                    capital, total_capital, srp, supplier,
                    date_received, expiration_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.product_name, self.product_type, self.__quantity,
                self.__capital, self.__total_capital, self.srp, self.__supplier,
                self.__date_received, self.__expiration_date
            ))
            return True, f"Product '{self.product_name}' added successfully."
        except sqlite3.Error as e:
            return False, f"Error adding product: {e}"

    def delete_method(self, product_id, db: Database):
        """
        Delete a product from the database by ID.

        """
        try:
            db.cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            if not db.cursor.fetchone():
                return False, f"No product found with ID {product_id}."
            db.cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            return True, f"Product with ID {product_id} deleted successfully."
        except sqlite3.Error as e:
            return False, f"Error deleting product: {e}"

    def update_method(self, db: Database, product_id, updates: dict):
        """
        Update product details in the database.

        Args:
            db (Database): Database connection instance.
            product_id (int): ID of the product to update.
            updates (dict): Dictionary of column-value pairs to update.

        Returns:
            tuple[bool, str]: Success flag and message.
        """
        try:
            if not updates:
                return False, "No updates provided."

            allowed = [
                "product_name", "product_type", "quantity",
                "capital", "srp", "supplier",
                "date_received", "expiration_date",
                "total_capital"
            ]

            float_cols = ["capital", "srp"]
            int_cols = ["quantity"]

            # Validate and convert data types
            for col in list(updates.keys()):
                if col not in allowed:
                    return False, f"Invalid column name: {col}"
                if col in float_cols:
                    updates[col] = float(updates[col])
                elif col in int_cols:
                    updates[col] = int(updates[col])

            # Auto-update SRP if capital changes
            if "capital" in updates:
                updates["srp"] = round(float(updates["capital"]) * 1.30, 2)

            # Compute total capital
            db.cursor.execute("SELECT quantity, capital FROM products WHERE product_id = ?", (product_id,))
            product = db.cursor.fetchone()
            if not product:
                return False, f"No product found with ID {product_id}."
            old_qty, old_cap = product
            qty = updates.get("quantity", old_qty)
            cap = updates.get("capital", old_cap)
            updates["total_capital"] = round(qty * cap, 2)

            # Build SQL update
            set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
            values = list(updates.values()) + [product_id]
            db.cursor.execute(f"UPDATE products SET {set_clause} WHERE product_id = ?", values)
            return True, f"Product with ID {product_id} updated successfully."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

    def view_method(self, db: Database, choice="all", name=None, product_id=None):
        """
        Retrieve products from the database.

        Args:
            db (Database): Database connection instance.
            choice (str, optional): 'all' to retrieve all products, 'one' for a specific product. Defaults to "all".
            name (str, optional): Product name for search. Used if choice="one".
            product_id (int, optional): Product ID for search. Used if choice="one".

        Returns:
            tuple[bool, list[dict] | str]: Success flag and either a list of products or error message.
        """
        try:
            query = """
            SELECT product_id, product_name, product_type, quantity,
                   capital, srp, total_capital, supplier,
                   date_received, expiration_date
            FROM products
            """
            params = ()
            if choice == "one":
                if product_id:
                    query += " WHERE product_id = ?"
                    params = (product_id,)
                elif name:
                    query += " WHERE product_name LIKE ?"
                    params = (f"%{name}%",)
                else:
                    return False, "Provide product ID or name."

            db.cursor.execute(query, params)
            rows = db.cursor.fetchall()
            if not rows:
                return False, "No product found."

            columns = ["product_id", "product_name", "product_type", "quantity",
                       "capital", "srp", "total_capital", "supplier",
                       "date_received", "expiration_date"]
            formatted = []
            for r in rows:
                r = list(r)
                r[4] = f"₱{r[4]:,.2f}"  # capital
                r[5] = f"₱{r[5]:,.2f}"  # srp
                r[6] = f"₱{r[6]:,.2f}"  # total capital
                formatted.append(dict(zip(columns, r)))
            return True, formatted
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

        

class Customers:

    def __init__(self, customer_name: str, contact: str, address: str):
        self.customer_name = customer_name.strip()
        self.contact = contact.strip()
        self.address = address.strip()


class Deliveries(Customers):
    """
    Represents a delivery record for a customer. Inherits from Customers.
    """

    def __init__(self, product: str, customer_name: str, contact: str, address: str,
                 deliveryaddress: str, delivery_date: str, status="Pending", remarks=None):
        """
        Initialize a new Delivery instance.

        Args:
            product (str): Name of the product to deliver.
            customer_name (str): Name of the customer.
            contact (str): Customer's contact number.
            address (str): Customer's main address.
            deliveryaddress (str): Delivery address.
            delivery_date (str): Scheduled delivery date.
            status (str, optional): Delivery status. Defaults to "Pending".
            remarks (str, optional): Optional remarks. Defaults to None.
        """
        super().__init__(customer_name, contact, address)
        self.product = product
        self.deliveryaddress = deliveryaddress
        self.delivery_date = delivery_date
        self.status = status
        self.remarks = remarks

    @staticmethod
    def show_deliveries(db: 'Database') -> tuple[list[str], list[list]]:
        """
        Retrieve all deliveries from the database.

        Args:
            db (Database): Database connection instance.

        """
        try:
            db.cursor.execute("SELECT * FROM deliveries")
            rows = db.cursor.fetchall()

            if not rows:
                headers = ["delivery_id", "product", "customer_name", "contact",
                           "customers_address", "delivery_date", "delivery_address",
                           "status", "remarks"]
                return headers, []

            headers = [desc[0] for desc in db.cursor.description]
            data = [list(row) for row in rows]
            return headers, data

        except Exception as e:
            return ["Error"], [[f"Database error: {str(e)}"]]

    def add_delivery(self, db: 'Database') -> tuple[bool, str]:
        """
        Add a new delivery record to the database.

        Args:
            db (Database): Database connection instance.

        """
        try:
            query = """
                INSERT INTO deliveries
                (product, customer_name, contact, customers_address, 
                 delivery_date, delivery_address, status, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            db.cursor.execute(query, (
                self.product,
                self.customer_name,
                self.contact,
                self.address,
                self.delivery_date,
                self.deliveryaddress,
                self.status,
                self.remarks
            ))
            return True, "Delivery added successfully."

        except Exception as e:
            return False, f"Error adding delivery: {str(e)}"

    @staticmethod
    def update_delivery(db: 'Database', delivery_id: int, updates: dict) -> tuple[bool, str]:
        """
        Update an existing delivery record in the database.

        Args:
            db (Database): Database connection instance.
            delivery_id (int): ID of the delivery to update.
            updates (dict): Dictionary of fields to update (column_name: value).

        """
        try:
            if not updates:
                return False, "No updates provided."

            valid_columns = {
                "product", "customer_name", "contact", "customers_address",
                "delivery_date", "delivery_address", "status", "remarks"
            }

            filtered = {k: v for k, v in updates.items() if k in valid_columns}

            if not filtered:
                return False, "Invalid update fields."

            set_clause = ", ".join([f"{col} = ?" for col in filtered.keys()])
            values = list(filtered.values()) + [delivery_id]

            db.cursor.execute(f"UPDATE deliveries SET {set_clause} WHERE delivery_id = ?", values)

            return True, f"Delivery ID {delivery_id} updated successfully."

        except Exception as e:
            return False, f"Error updating delivery: {str(e)}"

    @staticmethod
    def delete_delivery(db: 'Database', delivery_id: int) -> tuple[bool, str]:
        """
        Delete a delivery record from the database.

        Args:
            db (Database): Database connection instance.
            delivery_id (int): ID of the delivery to delete.

        """
        try:
            db.cursor.execute("DELETE FROM deliveries WHERE delivery_id = ?", (delivery_id,))
            return True, f"Delivery ID {delivery_id} deleted successfully."

        except Exception as e:
            return False, f"Error deleting delivery: {str(e)}"

class Order:
    """
    Handles customer orders including creation of customers, orders, and order items.
    """

    def create_customer(self, customer: 'Customers', db: 'Database') -> tuple[bool, int | str]:
        """
        Check if the customer exists; if not, create a new customer.

        Parameters:
            customer (Customers): Customer object containing name, contact, and address.
            db (Database): Database connection object.

        """
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
            return True, db.cursor.lastrowid

        except sqlite3.Error as e:
            return False, f"Failed to create customer: {e}"

    def create_order(self, customer_id: int, db: 'Database') -> tuple[bool, int | str]:
        """
        Create a new order for a given customer ID.

        Parameters:
            customer_id (int): ID of the customer placing the order.
            db (Database): Database connection object.

        """
        try:
            order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.cursor.execute("""
                INSERT INTO orders (customer_id, order_date)
                VALUES (?, ?)
            """, (customer_id, order_date))
            return True, db.cursor.lastrowid
        except sqlite3.Error as e:
            return False, f"Failed to create order: {e}"

    def add_order_item(self, order_id: int, product_id: int, quantity: int, db: 'Database') -> tuple[bool, str]:
        """
        Add a product to an order. Updates quantity if product already exists in the order.

        Parameters:
            order_id (int): ID of the order.
            product_id (int): ID of the product to add.
            quantity (int): Quantity of the product.
            db (Database): Database connection object.

        """
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

            return True, message

        except sqlite3.IntegrityError as e:
            return False, f"Integrity error: {e}"
        except sqlite3.Error as e:
            return False, f"Failed to add order item: {e}"

        
class SellProducts:
    """Handles selling products using Order and Product classes."""

    def __init__(self):
        self.cart = []  # Each item: dict with product_id, name, quantity, price

    @staticmethod
    def fetch_products(db: 'Database'):
        """
        Fetch all products and their SRP from the database.

        """
        try:
            db.cursor.execute("SELECT product_id, product_name, srp FROM products")
            rows = db.cursor.fetchall()
            if not rows:
                return ["Product ID", "Product Name", "Selling Price"], []

            data = []
            for pid, name, srp in rows:
                data.append([pid, name, f"₱{srp:,.2f}"])
            return ["Product ID", "Product Name", "Selling Price"], data
        except Exception as e:
            return ["Error"], [[f"Database error: {e}"]]

    def add_to_cart(self, product_id: int, name: str, price: float, quantity: int = 1):
        """
        Add a product to the cart. Updates quantity if already exists.
        """
        for item in self.cart:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                item["subtotal"] = round(item["quantity"] * item["price"], 2)
                return f"Updated {name} quantity to {item['quantity']}."
        
        self.cart.append({
            "product_id": product_id,
            "name": name,
            "price": price,
            "quantity": quantity,
            "subtotal": round(price * quantity, 2)
        })
        return f"Added {name} (x{quantity}) to cart."

    def cart_summary(self):
        """
        Return the total items and total price in the cart.
        """
        total_items = sum(item["quantity"] for item in self.cart)
        total_price = sum(item["subtotal"] for item in self.cart)
        return total_items, round(total_price, 2)

    def checkout(self, customer: 'Customers', db: 'Database'):
        """
        Finalize sale: create customer, order, and order_items.

        """
        if not self.cart:
            return False, "Cart is empty."

        order_handler = Order()

        # Create or fetch customer
        success, customer_id = order_handler.create_customer(customer, db)
        if not success:
            return False, f"Customer creation failed: {customer_id}"

        # Create order
        success, order_id = order_handler.create_order(customer_id, db)
        if not success:
            return False, f"Order creation failed: {order_id}"

        # Add each cart item
        messages = []
        for item in self.cart:
            success, msg = order_handler.add_order_item(
                order_id, item["product_id"], item["quantity"], db
            )
            messages.append(msg)
            if not success:
                return False, f"Failed to add product {item['name']}: {msg}"

        # Clear cart after checkout
        self.cart.clear()

        total_items, total_price = self.cart_summary()
        summary = f"Order {order_id} completed successfully. Total items: {total_items}, Total price: ₱{total_price:,.2f}\nDetails:\n" + "\n".join(messages)
        return True, summary

        
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

            return True, results

        except sqlite3.Error as e:
            return False, f"Failed to calculate monthly financials: {e}"
    
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