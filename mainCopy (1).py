from tkinter import *
from tkinter import messagebox
from tksheet import Sheet
from tkinter import ttk
import sqlite3
from MNEBackEnd import *
from cryptography.fernet import Fernet

gui = Tk()
gui.title("JOMAR & CARLO")
img = PhotoImage(file="Python Files/logo.png")
gui.iconphoto(True,img)
def refreshSection():
    for i in section.winfo_children():
        i.destroy()
def clearWindow():
    for i in gui.winfo_children():
        i.destroy()

"""def DSales():
    refreshGraph()
    conn = sqlite3.connect("c:/Users/admin/Desktop/OOP SEMPROJ/Hardware and Construction.db")  # temporary DB
    c = conn.cursor()

    c.execute(
        SELECT orders.order_date, SUM(order_items.quantity) AS total_quantity
        FROM orders
        LEFT JOIN order_items ON orders.order_id = order_items.order_id
        GROUP BY orders.order_date
        ORDER BY orders.order_date

    )
    
    data = c.fetchall()
    conn.close()
    
    if not data:
        messagebox.showinfo("message","No sales data found.")
        return
    x = [str(row[0]) for row in data]
    y = [row[1] for row in data]
    xx = str(x)
    print(xx,y)"""
def DashBoard():

    refreshSection()
    headText.config(text="DASHBOARD")
    salesFrame = Frame(section,width=250, height=150,bg="blue")
    salesFrame.grid(row=0, column=1, pady=10,padx=10)
    userCountFrame = Frame(section,width=250, height=150,bg="blue")
    userCountFrame.grid(row=0, column=2, pady=10,padx=10)
    productsFrame = Frame(section,width=250, height=150,bg="blue")
    productsFrame.grid(row=0, column=3, pady=10,padx=10)
    
    for f in (salesFrame, userCountFrame, productsFrame):
        f.grid_propagate(False)
        f.rowconfigure(0, weight=1)      # Y
        f.columnconfigure(0, weight=1)   # X
     # Centered labels
    db = sqlite3.connect("C:/Users/admin/Desktop/OOP SEMPROJ/Hardware and Construction.db")
    cs = db.cursor()
    cs.execute("SELECT SUM(total_sales) AS powah FROM monthly_financials")
    xx = cs.fetchone()
    cs.execute("SELECT COUNT(*) FROM users")
    xc = cs.fetchone()
    
    Label(salesFrame, text=f"₱ {xx[0]}\nsales",fg="white", bg="blue", font=("Arial",25,"bold")).grid(row=0, column=0)
    Label(userCountFrame, text=f"👤{xc[0]}\nactive users",fg="white", bg="blue", font=("Arial",25,"bold")).grid(row=0, column=0)
    Label(productsFrame, text="38 Products\navailable products",fg="white", bg="blue", font=("Arial",20,"bold")).grid(row=0, column=0)
def Inventory():
    #NAGWA NA NI PARTNER
    refreshSection()
    headText.config(text="INVENTORY")

    dbc = Database("c:/Users/admin/Desktop/OOP SEMPROJ/Hardware and Construction.db")
    db = sqlite3.connect("c:/Users/admin/Desktop/OOP SEMPROJ/Hardware and Construction.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    sht = Sheet(section, 
                data=data,
                header=["Product ID",
                    "Product Name",
                    "Category ID",
                    "Type ID",
                    "Quantity",
                    "Capital",
                    "SRP",
                    "Supplier ID",
                    "Date Recieved",
                    "Expiration Date",
                    "Life Span"])
    def reload_data():
        cursor.execute("SELECT * FROM products")
        x = cursor.fetchall()
        sht.set_sheet_data(x) #SELECT NALANG LAHAT SA DATBASE TABLE
    def add_dataByRowAddedInSheet(event = None):
        allData = sht.get_sheet_data()
        lastRow = allData[-1]
        for cols in lastRow:
            b =lastRow[cols]
        x = Product(b)
        x.add_method(dbc)
        for cols in lastRow:
            for i in range(1,8):
                x = cols[i]
        if lastRow[11] != "":
            try:
                
                cursor.execute("INSERT INTO products (product_name,category_id, type_id, quantity,\
                    capital, srp, supplier_id, date_received) VALUES (?)",(x))
                db.commit()
                
                reload_data()
                print(x)
            except Exception as e:
                print(e)
    sht.extra_bindings(
        [
            ("end_edit_cell",
             add_dataByRowAddedInSheet)
        ]
    )
    reload_data()
    sht.pack(fill="both", expand=True)
    sht.enable_bindings("all")
def DailySales():
    refreshSection()
    headText.config(text="DAILY SALES")
def MonthlySales():
    refreshSection()
    headText.config(text="MONTHLY SALES")
def Suppliers():
    refreshSection()
    headText.config(text="SUPPLIERS")
def Customer():
    refreshSection()
    headText.config(text="CUSTOMERS")
def Incase():
    refreshSection()
    headText.config(text="INCASE OR ORDER PWEDE")

def logCond(a,b):
    db = sqlite3.connect("c:/Users/admin/Desktop/OOP SEMPROJ/Hardware and Construction.db")
    cursor = db.cursor()
    cursor.execute("SELECT username FROM users")
    x = cursor.fetchall()
    cursor.execute("SELECT password FROM users WHERE username = (?)",(a,))
    c = cursor.fetchone()
    usernames = [u[0] for u in x]
    with open(".env/secret.key", "rb") as key_file:
        key = key_file.read()
    f = Fernet(key)
    dcd = b
    print(c,dcd)
    if a == "admin" and b == "test1234": 
        messagebox.showinfo("Admin", "Welcome, Admin")
        adminPanel()
    elif a in usernames and dcd == f.decrypt(c[0]).decode():
        messagebox.showinfo("User", f"Welcome Back {a}")
        UserPanel()
    else: messagebox.showerror("Wrong Login", "Invalid username or Password")
def SignUpToDatabase(a,b,fn, contNum, gndr, age):
    db = sqlite3.connect("c:/Users/admin/Desktop/OOP SEMPROJ/Hardware and Construction.db")
    cursor = db.cursor()
    cursor.execute("SELECT username FROM users")
    usernames = [row[0] for row in cursor.fetchall()]
    print(a)
    with open(".env/secret.key", "rb") as key_file:
        key = key_file.read()

    f = Fernet(key)

    token = f.encrypt(b.encode())
    f.decrypt(token).decode()
    if a in usernames:
        messagebox.showerror("error","username used already")
        return
    else:
        cursor.execute("INSERT INTO users(username,\
    password,\
    fullName,\
    contNumber,\
    gender,\
    age) VALUES(?,?,?,?,?,?)",(a,token,fn, contNum, gndr, age))
        db.commit()
        db.close()
        messagebox.showinfo("user", f"Hello, {fn}, your account created successfully")
        UserPanel()
    
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
    pw = Entry(section,font=("Arial",15,"bold"),show='*')
    pw.pack()
    btLog = Button(section, 
                text="Login",
                font=("Arial",15,"bold"),
                command=lambda: logCond(un.get(), pw.get()))
    btLog.pack(pady=15)
    sUBtn = Button(section,
                   text="Sign Up",
                   command=createAccount,
                   bg="blue")
    
    sUBtn.pack(pady=15)
    signUpText = Label(section, text="Don't have an account? Sign up", fg="blue",bg= "grey", cursor="hand2", font=("Arial", 12, "underline"))
    signUpText.pack(pady=5)
    signUpText.bind("<Button-1>", lambda e: createAccount())
def createAccount():
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
    Label(section,text='SIGN UP',bg="grey", font=('Arial',30,'bold')).pack()
    Label(section,text='',bg="grey").pack()

    unL = Label(section,
                text="Username",
                font=("Arial",10,"bold"),
                bg="grey",
                fg="black")
    unL.pack()
    sUn = Entry(section,
               font=("Arial",10,"bold"))
    sUn.pack()
    pwL = Label(section,
                text="Password",
                font=("Arial",10,"bold"),
                bg="grey",
                fg="black")
    pwL.pack()
    SpW = Entry(section,font=("Arial",10,"bold"),show='*')
    SpW.pack()
    fname = Label(section,
                text="Full Name",
                font=("Arial",10,"bold"),
                bg="grey",
                fg="black")
    fname.pack()
    fn = Entry(section,font=("Arial",10,"bold"))
    fn.pack()
    cnL = Label(section,
                text="Contact Number",
                font=("Arial",10,"bold"),
                bg="grey",
                fg="black")
    cnL.pack()
    cont = Entry(section,font=("Arial",10,"bold"))
    cont.pack()
    gndr = Label(section,
                text="Gender",
                font=("Arial",10,"bold"),
                bg="grey",
                fg="black")
    gndr.pack()
    gender = Entry(section,font=("Arial",10,"bold"))
    gender.pack()
    ageL = Label(section,
                text="Age",
                font=("Arial",10,"bold"),
                bg="grey",
                fg="black")
    ageL.pack()
    age = Entry(section,font=("Arial",10,"bold"))
    age.pack()
    SuBtn = Button(section, 
                text="SIGNUP",
                font=("Arial",15,"bold"),
                command=lambda: SignUpToDatabase(sUn.get(),
                                                SpW.get(),
                                                fn.get(),
                                                cont.get(),
                                                gender.get(),
                                                age.get()))
    SuBtn.pack(padx=15,pady=10)
    
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
    gui.geometry("1080x650")
    sideDash = Frame(gui,
bg="#2F2F2F",
width=200,
border=1)
    sideDash.pack(side="left",
                  fill='y')

    greetLOne = Label(sideDash,
text="Hello,Admin",
fg="#FFFFFF",
width=12,
font=("Arial",20, 'bold'),
bg="#2F2F2F")
    
    greetLOne.pack(padx=5,pady=8)
    Label(sideDash, text='',bg="#2F2F2F").pack(pady=5)
    btText = ['DASHBOARD','INVENTORY', 'DAILY SALES', 'MONTHLY SALES','SUPPLIERS', 'CUSTOMERS', 'INCASE', 'LOGOUT']
    btCommads = [DashBoard, Inventory, DailySales, MonthlySales, Suppliers, Customer, Incase, LogInPage]
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

    # Header
    header = Frame(gui, bg="orange", height=100)
    header.pack(fill="x")
    Label(header, text="J&J HARDWARE SUPPLIES", font=("Arial", 20, "bold"), bg="orange").pack(padx=30, pady=30)

    # Navigation
    navSec = Frame(gui, bg="grey", height=25)
    navSec.pack(fill="x")
    Button(navSec, text='<-').grid(row=0, column=0)
    Button(navSec, text="Home").grid(row=0, column=5)
    Button(navSec, text="Orders").grid(row=0, column=6)
    Button(navSec, text="Profile").grid(row=0, column=7)

    # Scrollable canvas
    section_frame = Frame(gui)
    section_frame.pack(fill="both", expand=True)

    canvas = Canvas(section_frame, bg="grey")
    scrollbar = Scrollbar(section_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="grey")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Mouse wheel scrolling
    def _on_mousewheel(event):
        if event.delta:
            canvas.yview_scroll(-1*(event.delta//120), "units")
        else:
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

    # Load items from database
    def load_items():
        conn = sqlite3.connect("./Hardware and Construction.db")
        c = conn.cursor()
        c.execute("SELECT product_name, srp FROM products")
        items = c.fetchall()
        conn.close()
        return items

    data = load_items()

    # Render items responsively
    def render_items(event=None):
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        canvas_width = canvas.winfo_width()
        min_item_width = 250
        padding = 20
        cols = max(1, canvas_width // (min_item_width + padding))

        row = 0
        col = 0
        for item_name, price in data:
            frame = Frame(scrollable_frame, bg="#d9d9d9", padx=5, pady=5)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Correct indentation — all widgets inside frame
            Label(frame, text=item_name, font=("Arial", 12, "bold"), bg="#d9d9d9").pack(anchor="nw", padx=10, pady=10)
            Label(frame, text=f"₱{price}", font=("Arial", 10), bg="#d9d9d9").pack(anchor="nw", padx=10)
            Button(frame, text="Add to Cart", bg="#7a0000", fg="white").pack(anchor="nw", padx=10, pady=10)

            col += 1
            if col >= cols:
                col = 0
                row += 1

        # Make columns expand equally
        for c in range(cols):
            scrollable_frame.grid_columnconfigure(c, weight=1)

    # Initial render
    render_items()
    # Re-render on window resize for responsiveness
    canvas.bind("<Configure>", render_items)



    
if __name__ == "__main__":
    UserPanel()
    gui.mainloop()
    #HAHAHAHAHAH ERROR AMPOTA
    