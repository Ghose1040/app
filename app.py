from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from cryptography.fernet import Fernet
import os
import re
import pymysql
pymysql.install_as_MySQLdb()



    class OnlineDelivery:
        def __init__(self, name): 
            self.app = Flask(name)
            self.app.secret_key = "hshshshshs"
            self.app.config["UPLOAD"] = "static"
    
            # 1. Get the URI from Render's Environment Variables
            # On Render, you should create an Environment Variable named DATABASE_URL
            # and paste your Aiven link: mysql://avnadmin:password@host:port/defaultdb
            uri = os.getenv("DATABASE_URL")
    
            if uri:
                # Fix the prefix for SQLAlchemy/PyMySQL
                if uri.startswith("mysql://"):
                    uri = uri.replace("mysql://", "mysql+pymysql://", 1)
                self.app.config['SQLALCHEMY_DATABASE_URI'] = uri
            else:
                # LOCAL PC SETTINGS (XAMPP)
                self.app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/online_delivery"
    
            self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            
            # Initialize the database here so it's available to all routes
            self.db = SQLAlchemy(self.app)
            
            # Now set up the routes
            self.setup_routes()

#public  
        # --- PUBLIC ROUTES ---
        
        @self.app.route("/")
        def home_public():
            # Use SQLAlchemy session + text() for raw SQL
            result = self.db.session.execute(text("SELECT * FROM menu"))
            menus = result.mappings().all()
            return render_template("home_public.html", menu_list=menus)

        @self.app.route("/bestsellers_public")
        def bestseller_public(): 
            result = self.db.session.execute(
                text("SELECT * FROM menu WHERE category2 = :cat"), {"cat": 'Best Sellers'}
            )
            menus = result.mappings().all()
            return render_template("bestsellers_public.html", menu_list=menus)

        @self.app.route("/newproducts_public")
        def newproducts_public(): 
            result = self.db.session.execute(
                text("SELECT * FROM menu WHERE category2 = :cat"), {"cat": 'New Products'}
            )
            menus = result.mappings().all()
            return render_template("newproducts_public.html", menu_list=menus)

        @self.app.route("/burger_public")
        def burger_public(): 
            result = self.db.session.execute(
                text("SELECT * FROM menu WHERE category = :cat"), {"cat": 'Burgers'}
            )
            menus = result.mappings().all()
            return render_template("burger_public.html", menu_list=menus)

        @self.app.route("/filipinofoods_public")
        def filipinofoods_public(): 
            result = self.db.session.execute(
                text("SELECT * FROM menu WHERE category2 = :cat"), {"cat": 'Filipino Foods'}
            )
            menus = result.mappings().all()
            return render_template("filipinofoods_public.html", menu_list=menus)

        @self.app.route("/meal_public")
        def meal_public(): 
            result = self.db.session.execute(
                text("SELECT * FROM menu WHERE category = :cat"), {"cat": 'Meal'}
            )
            menus = result.mappings().all()
            return render_template("meal_public.html", menu_list=menus)

        @self.app.route("/snack_public")
        def snack_public(): 
            result = self.db.session.execute(
                text("SELECT * FROM menu WHERE category = :cat"), {"cat": 'Snacks'}
            )
            menus = result.mappings().all()
            return render_template("snack_public.html", menu_list=menus)

        @self.app.route("/drinks_public")
        def drinks_public(): 
            result = self.db.session.execute(
                text("SELECT * FROM menu WHERE category = :cat"), {"cat": 'Drinks N Desserts'}
            )
            menus = result.mappings().all()
            return render_template("drinks_public.html", menu_list=menus)
        
        
#####################
#Login & Register   
    
        ENCRYPTION_KEY = b'ln2ipngFdv9ofcmYcHVlCNJ5ct_vpKgxtxPKIcu7J5w=' 
        fernet = Fernet(ENCRYPTION_KEY)
        def sanitize_input(text):
            """Basic sanitization to remove HTML tags and leading/trailing whitespace."""
            if not text: return ""
            return re.sub('<[^<]+?>', '', str(text)).strip()

        def hash_password(password):
            """Hashes a password using bcrypt."""
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        def check_password(password, hashed):
            """Verifies a password against its hash."""
            return bcrypt.checkpw(password.encode('utf-8'), hashed)

        def encrypt_data(data):
            """Encrypts sensitive strings."""
            return fernet.encrypt(str(data).encode()).decode()

        def decrypt_data(encrypted_data):
            """Decrypts sensitive strings."""
            try:
                return fernet.decrypt(encrypted_data.encode()).decode()
            except:
                return "[Decryption Error]"

        def validate_password_complexity(password):
            """Validates alphanumeric and length >= 8."""
            if len(password) < 8:
                return False
            if not re.match("^[a-zA-Z0-9]*$", password):
                return False
            return True

        # --- MIDDLEWARE / AUTH WRAPPERS ---

        # --- MIDDLEWARE / AUTH WRAPPERS ---

        def is_admin():
            return session.get('role') == 'admin'

        def is_user():
            return session.get('role') == 'user'
        
        @self.app.route("/login")
        def login():
            return render_template("login.html")
        
        @self.app.route("/login_process", methods=["POST", "GET"])
        def login_process():
            # Static admin check
            if request.form.get("username") == "admin" and request.form.get("password") == "francis":
                session["role"] = "admin"
                session["user"] = "admin"
                return redirect("/admin")
            
            if request.method == "POST":
                user_textbox = request.form["username"]
                pass_textbox = request.form["password"]

                # Use SQLAlchemy session
                query = text("SELECT id, Password, status FROM register WHERE Username = :u")
                result = self.db.session.execute(query, {"u": user_textbox})
                account_found = result.fetchone()
                
                if account_found:
                    user_id = account_found[0]
                    hashed_password = account_found[1]
                    status = account_found[2]
                    
                    # Verify hashed password
                    if bcrypt.checkpw(pass_textbox.encode('utf-8'), hashed_password.encode('utf-8')):
                        if status == "Restricted":
                            flash("Your account is Restricted.")
                            return redirect("/login")
                        else:
                            session["user"] = user_id
                            session["role"] = "user"
                            return redirect("/home")
                    else:
                        flash("Incorrect Username or Password.")
                        return redirect("/login")
                else:
                    flash("Incorrect Username or Password.")
                    return redirect("/login")
            return render_template("login.html")

        @self.app.route("/register", methods=["GET", "POST"])
        def register():
            if request.method == "POST":
                std_first = request.form["firstname"]
                std_last = request.form["lastname"]
                std_age = request.form["age"]
                std_address = request.form["address"]
                std_contact = request.form["contact"]
                std_username = request.form["username"]
                std_password = request.form["password"]
                
                # Hash the password
                hashed_password = bcrypt.hashpw(std_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                # Use SQLAlchemy to INSERT
                query = text("""
                    INSERT INTO register (First_name, Last_name, Age, Address, Contact, Username, Password) 
                    VALUES (:f, :l, :a, :addr, :c, :u, :p)
                """)
                
                self.db.session.execute(query, {
                    "f": std_first, "l": std_last, "a": std_age, 
                    "addr": std_address, "c": std_contact, 
                    "u": std_username, "p": hashed_password
                })
                
                self.db.session.commit() # Crucial for saving to Aiven
                    
                return redirect(url_for('login'))
            return render_template("register.html")

######################
#Menus

        # --- LOGGED-IN USER ROUTES ---

        @self.app.route("/home")
        def home():
            if "user" in session:
                user_id = session["user"]
                
                # Fetch Menu
                menus = self.db.session.execute(text("SELECT * FROM menu")).mappings().all()
                
                # Fetch Cart Count
                cart_res = self.db.session.execute(
                    text("SELECT COUNT(*) FROM cart WHERE user_id = :u"), {"u": user_id}
                ).fetchone()
                cart_count = cart_res[0] if cart_res else 0
                
                return render_template("home.html", menu_list=menus, cart_count=cart_count)
            return redirect("/login")

        @self.app.route("/search", methods=["GET", "POST"])
        def search():
            if "user" in session:
                search_term = request.form.get("search", "")
                user_id = session["user"]
                
                # Fetch Menu with LIKE (adding wildcards for better searching)
                menus = self.db.session.execute(
                    text("SELECT * FROM menu WHERE name LIKE :s"), 
                    {"s": f"%{search_term}%"}
                ).mappings().all()
                
                # Fetch Cart Count
                cart_res = self.db.session.execute(
                    text("SELECT COUNT(*) FROM cart WHERE user_id = :u"), {"u": user_id}
                ).fetchone()
                cart_count = cart_res[0] if cart_res else 0
                
                # Fetch User Info
                user_info = self.db.session.execute(
                    text("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID = :u"), 
                    {"u": user_id}
                ).fetchone()
                
                return render_template("search.html", menu_list=menus, search=search_term, cart_count=cart_count, user_info=user_info)
            return redirect("/login")

        # --- CATEGORY ROUTES (Logged In) ---

        def get_category_data(self, category_col, category_val, user_id):
            """Helper function to reduce repeated code"""
            menus = self.db.session.execute(
                text(f"SELECT * FROM menu WHERE {category_col} = :val"), {"val": category_val}
            ).mappings().all()
            
            cart_res = self.db.session.execute(
                text("SELECT COUNT(*) FROM cart WHERE user_id = :u"), {"u": user_id}
            ).fetchone()
            
            user_info = self.db.session.execute(
                text("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID = :u"), 
                {"u": user_id}
            ).fetchone()
            
            return menus, (cart_res[0] if cart_res else 0), user_info

        @self.app.route("/bestsellers")
        def bestsellers(): 
            if "user" in session:
                menus, count, info = self.get_category_data("category2", "Best Sellers", session["user"])
                return render_template("bestsellers.html", menu_list=menus, cart_count=count, user_info=info)
            return redirect('/login')

        @self.app.route("/newproducts")
        def newproducts(): 
            if "user" in session:
                menus, count, info = self.get_category_data("category2", "New Products", session["user"])
                return render_template("newproducts.html", menu_list=menus, cart_count=count, user_info=info)
            return redirect('/login')

        @self.app.route("/burger")
        def burger(): 
            if "user" in session:
                menus, count, info = self.get_category_data("category", "Burgers", session["user"])
                return render_template("burger.html", menu_list=menus, cart_count=count, user_info=info)
            return redirect('/login')

        @self.app.route("/filipinofoods")
        def filipinofoods(): 
            if "user" in session:
                menus, count, info = self.get_category_data("category2", "Filipino Foods", session["user"])
                return render_template("filipinofoods.html", menu_list=menus, cart_count=count, user_info=info)
            return redirect('/login')

        @self.app.route("/meal")
        def meal(): 
            if "user" in session:
                menus, count, info = self.get_category_data("category", "Meal", session["user"])
                return render_template("meal.html", menu_list=menus, cart_count=count, user_info=info)
            return redirect('/login')

        @self.app.route("/snack")
        def snack():
            if "user" in session:
                menus, count, info = self.get_category_data("category", "Snacks", session["user"])
                return render_template("snack.html", menu_list=menus, cart_count=count, user_info=info)
            return redirect('/login')

        @self.app.route("/drinks")
        def drinks(): 
            if "user" in session:
                menus, count, info = self.get_category_data("category", "Drinks N Desserts", session["user"])
                return render_template("drinks.html", menu_list=menus, cart_count=count, user_info=info)
            return redirect("/login")
            
        
        
# --- HELPER: Unified Add to Cart Logic ---
        def handle_add_to_cart(self, redirect_to):
            if "user" not in session:
                return redirect("/login")
            
            item_name = request.form['item_name']
            item_price = float(request.form['item_price'])
            item_img = request.form['item_img'] 
            quantity = int(request.form['quantity'])
            user_id = session["user"]
            total_price = item_price * quantity

            # Check if item exists in user's cart
            query_check = text("SELECT quantity FROM cart WHERE item_name = :n AND user_id = :u")
            existing = self.db.session.execute(query_check, {"n": item_name, "u": user_id}).fetchone()

            if existing:
                new_qty = existing[0] + quantity
                new_total = new_qty * item_price
                self.db.session.execute(
                    text("UPDATE cart SET quantity = :q, total_price = :t WHERE item_name = :n AND user_id = :u"),
                    {"q": new_qty, "t": new_total, "n": item_name, "u": user_id}
                )
            else:
                self.db.session.execute(
                    text("""INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) 
                            VALUES (:n, :q, :p, :i, :t, :u)"""),
                    {"n": item_name, "q": quantity, "p": item_price, "i": item_img, "t": total_price, "u": user_id}
                )
            
            self.db.session.commit()
            return redirect(url_for(redirect_to))

        # --- REPLACED: Category-Specific Add to Cart Routes ---
        @self.app.route("/add_to_cart_search", methods=["POST"])
        def add_to_cart_search(): return self.handle_add_to_cart('search')

        @self.app.route("/add_to_cart", methods=["POST"])
        def add_to_cart(): return self.handle_add_to_cart('home')

        @self.app.route("/add_to_cart_bestsellers", methods=["POST"])
        def add_to_cart_bestsellers(): return self.handle_add_to_cart('bestsellers')

        @self.app.route("/add_to_cart_newproducts", methods=["POST"])
        def add_to_cart_newproducts(): return self.handle_add_to_cart('newproducts')

        @self.app.route("/add_to_cart_burger", methods=["POST"])
        def add_to_cart_burger(): return self.handle_add_to_cart('burger')

        @self.app.route("/add_to_cart_filipinofoods", methods=["POST"])
        def add_to_cart_filipinofoods(): return self.handle_add_to_cart('filipinofoods')

        # --- ORDERING SYSTEM ---

        @self.app.route("/place_the_order", methods=["GET", "POST"])
        def place_the_order():
            if request.method == "POST":
                user_id = session.get("user")
                # Fetch User Info for the confirmation page
                user_info = self.db.session.execute(
                    text("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=:u"), 
                    {"u": user_id}
                ).fetchone()
                
                return render_template(
                    "place_the_order.html", 
                    item_name=request.form['item_name'], 
                    item_price=request.form['item_price'], 
                    item_img=request.form['item_img'], 
                    quantity=request.form['quantity'], 
                    total_price=float(request.form['item_price']) * int(request.form['quantity']),
                    name=request.form['name'], 
                    address=request.form['address'], 
                    number=request.form['number'], 
                    user_info=user_info
                )
            return render_template("cart.html")
            
        @self.app.route("/place_order", methods=["POST"])
        def place_order():
            if "user" in session:
                user_id = session["user"]
                item_price = float(request.form['item_price'])
                quantity = int(request.form['quantity'])
                
                query = text("""
                    INSERT INTO orders (item_name, item_price, item_img, quantity, name, address, number, payment_method, total, user_id) 
                    VALUES (:item, :price, :img, :qty, :name, :addr, :num, :pay, :total, :u)
                """)
                
                self.db.session.execute(query, {
                    "item": request.form['item_name'], "price": item_price, "img": request.form['item_img'],
                    "qty": quantity, "name": request.form['name'], "addr": request.form['address'],
                    "num": request.form['number'], "pay": request.form['payment_method'],
                    "total": item_price * quantity, "u": user_id
                })
                self.db.session.commit()
                return redirect(url_for('home'))
            return redirect("/login")
        


        # These routes now use the helper function we created earlier
        # which handles both NEW items and UPDATING existing quantities.

        @self.app.route("/add_to_cart_snack", methods=["POST"])
        def add_to_cart_snack():
            return self.handle_add_to_cart('snack')

        @self.app.route("/add_to_cart_drinks", methods=["POST"])
        def add_to_cart_drinks():
            return self.handle_add_to_cart('drinks')

        @self.app.route("/add_to_cart_meal", methods=["POST"])
        def add_to_cart_meal():
            return self.handle_add_to_cart('meal')

        @self.app.route("/add_to_cart_dessert", methods=["POST"])
        def add_to_cart_dessert():
            # Ensure you have a 'dessert' route defined in your setup_routes
            return self.handle_add_to_cart('dessert')


        @self.app.route("/cart")
        def cart():
            if "user" in session:
                user_id = session["user"]
                
                # Fetch cart items as dictionaries for easier access
                cart_items = self.db.session.execute(
                    text("SELECT * FROM cart WHERE user_id=:u"), {"u": user_id}
                ).mappings().all()

                # Calculate total using key names
                total_price = sum(item['item_price'] * item['quantity'] for item in cart_items)
                
                user_info = self.db.session.execute(
                    text("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=:u"), 
                    {"u": user_id}
                ).fetchone()

                return render_template("cart.html", cart_items=cart_items, total_price=total_price, user_info=user_info)
            return redirect("/login")
            
        @self.app.route("/confirmation", methods=["POST"])
        def confirmation():
            if "user" in session:
                user_id = session["user"]
                selected_items = request.form.getlist("selected_items")
                
                items_for_order = []
                total_order_price = 0

                for item_id in selected_items:
                    item = self.db.session.execute(
                        text("SELECT item_name, quantity, item_price, item_img FROM cart WHERE id=:id AND user_id=:u"),
                        {"id": item_id, "u": user_id}
                    ).fetchone()

                    if item:
                        name, qty, price, img = item
                        subtotal = price * qty
                        total_order_price += subtotal
                        items_for_order.append({
                            "item_id": item_id, "item_name": name, "quantity": qty,
                            "item_price": price, "total_price": subtotal, "item_img": img
                        })

                user_info = self.db.session.execute(
                    text("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=:u"), 
                    {"u": user_id}
                ).fetchone()

                return render_template("confirmation.html", items_for_order=items_for_order, total_order_price=total_order_price, user_info=user_info)
            return redirect("/login")
        
        @self.app.route("/confirm_order", methods=["POST"])
        def confirm_order():
            if "user" in session:
                user_id = session["user"]
                # Zip all lists from form to iterate together
                order_data = zip(
                    request.form.getlist("item_id"), request.form.getlist("item_name"),
                    request.form.getlist("item_price"), request.form.getlist("item_img"),
                    request.form.getlist("item_quantity"), request.form.getlist("item_total_price")
                )
                
                for item_id, name, price, img, qty, total in order_data:
                    # Insert into orders
                    self.db.session.execute(text("""
                        INSERT INTO orders (item_name, item_price, item_img, quantity, name, address, number, payment_method, total, user_id) 
                        VALUES (:n, :p, :i, :q, :un, :addr, :num, :pay, :t, :u)
                    """), {
                        "n": name, "p": price, "i": img, "q": qty, "un": request.form['user_name'],
                        "addr": request.form['address'], "num": request.form['number'],
                        "pay": request.form['payment_method'], "t": total, "u": user_id
                    })
                    # Clear this specific item from cart
                    self.db.session.execute(text("DELETE FROM cart WHERE id=:id AND user_id=:u"), {"id": item_id, "u": user_id})

                self.db.session.commit()
                return redirect(url_for("cart"))
            return redirect(url_for("login"))

        @self.app.route("/history", methods=["GET", "POST"]) # Changed to allow GET if needed
        def history(): 
            if "user" in session:
                user_id = session["user"]
                orders_items = self.db.session.execute(
                    text("SELECT * FROM orders WHERE status ='order deliver' AND user_id=:u"), {"u": user_id}
                ).mappings().all()
                return render_template("history.html", orders_items=orders_items)
            return redirect("/login")

        @self.app.route("/delete", methods=["POST"])
        def delete(): 
            item_id = request.form["id"]
            self.db.session.execute(text("DELETE FROM cart WHERE id=:id"), {"id": item_id})
            self.db.session.commit()
            return redirect("/cart")    
        
        @self.app.route("/profile", methods=['GET', 'POST'])
        def profile():
            if "user" not in session: return redirect("/login")
            user_id = session["user"]

            if request.method == 'POST':
                if 'profile_picture' in request.files:
                    pic = request.files['profile_picture']
                    if pic and pic.filename:
                        filename = os.path.join(self.app.config["UPLOAD"], pic.filename)
                        pic.save(filename)
                        path = "static/" + pic.filename
                        self.db.session.execute(text("UPDATE register SET Profile=:p WHERE ID=:u"), {"p": path, "u": user_id})
                        self.db.session.commit()
                elif 'delete' in request.form:
                    self.db.session.execute(text("UPDATE register SET Profile=NULL WHERE ID=:u"), {"u": user_id})
                    self.db.session.commit()
                return redirect(url_for('profile'))

            user_info = self.db.session.execute(
                text("SELECT First_name, Last_name, Age, Address, Contact, Username, Password, Profile FROM register WHERE ID=:u"), 
                {"u": user_id}
            ).fetchone()
            return render_template("profile.html", user_info=user_info)

        @self.app.route('/logout', methods=['POST', 'GET'])
        def logout():
            session.clear()
            return redirect('/login')

        @self.app.route("/update_profile", methods=["GET", "POST"])
        def update_profile():
            if "user" not in session: return redirect("/login")
            user_id = session["user"]
            
            if request.method == "POST":
                # Hash the updated password
                hashed = bcrypt.hashpw(request.form["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                profile_path = None
                if "profile" in request.files and request.files["profile"].filename:
                    pic = request.files["profile"]
                    filename = os.path.join(self.app.config["UPLOAD"], pic.filename)
                    pic.save(filename)
                    profile_path = "static/" + pic.filename
                
                self.db.session.execute(text("""
                    UPDATE register SET First_name=:f, Last_name=:l, Age=:a, Address=:addr, Contact=:c, Username=:u, Password=:p, Profile=COALESCE(:pr, Profile)
                    WHERE ID=:id
                """), {
                    "f": request.form["firstname"], "l": request.form["lastname"], "a": request.form["age"],
                    "addr": request.form["address"], "c": request.form["contact"], "u": request.form["username"],
                    "p": hashed, "pr": profile_path, "id": user_id
                })
                self.db.session.commit()
                return redirect(url_for('profile'))
            
            user_info = self.db.session.execute(
                text("SELECT First_name, Last_name, Age, Address, Contact FROM register WHERE ID=:u"), {"u": user_id}
            ).fetchone()
            return render_template("update_profile.html", user_info=user_info)
            

        @self.app.route("/admin")
        def admin():
            # Using mappings() makes record[4] access much cleaner as record['total_price']
            query = text("""
                SELECT item_name, DATE(date_order) as order_date, SUM(quantity) as total_quantity, 
                       item_price, SUM(quantity * item_price) as total_price
                FROM orders
                WHERE status = 'order deliver'
                GROUP BY item_name, DATE(date_order), item_price
                ORDER BY order_date DESC
            """)
            sales_data = self.db.session.execute(query).all()
            
            # Calculate overall total from the fetched results
            overall_total_price = sum(record[4] for record in sales_data) if sales_data else 0
            return render_template("admin.html", sales_data=sales_data, overall_total_price=overall_total_price)

        @self.app.route("/orders")
        def orders():
            # Fetch pending orders
            query = text("SELECT * FROM orders WHERE status IS NULL OR status = ''")
            cart_items = self.db.session.execute(query).mappings().all()
            return render_template("orders.html", cart_items=cart_items)
            
        @self.app.route("/success", methods=["POST"])
        def success(): 
            if request.method == "POST":
                self.db.session.execute(
                    text("UPDATE orders SET status=:s WHERE Id=:id"),
                    {"s": request.form["status"], "id": request.form["id"]}
                )
                self.db.session.commit()
                return redirect(url_for('orders'))
        
        @self.app.route("/accounts")
        def accounts():
            user_info = self.db.session.execute(text("SELECT * FROM register")).mappings().all()
            return render_template("accounts.html", user_info=user_info)
            
        @self.app.route("/restricted", methods=["POST"])
        def restricted():
            self.db.session.execute(
                text("UPDATE register SET status=:s WHERE Id=:id"),
                {"s": request.form["status"], "id": request.form["Id"]}
            )
            self.db.session.commit()
            return redirect(url_for('accounts'))
            
        @self.app.route("/admin_delete", methods=["POST"])
        def admin_delete(): 
            self.db.session.execute(text("DELETE FROM register WHERE Id=:id"), {"id": request.form["Id"]})
            self.db.session.commit()
            return redirect("/accounts")
        
        @self.app.route("/edit_menu", methods=["GET", "POST"])
        def edit_menu():
            if request.method == "POST":
                img = request.files["img"]
                if img and img.filename:
                    filename = os.path.join(self.app.config["UPLOAD"], img.filename)
                    img.save(filename)
                    img_path = "static/" + img.filename
                
                    self.db.session.execute(text("""
                        INSERT INTO menu (name, price, img, category, category2) 
                        VALUES (:n, :p, :i, :c1, :c2)
                    """), {
                        "n": request.form["name"], "p": request.form["price"], 
                        "i": img_path, "c1": request.form["category"], "c2": request.form["category2"]
                    })
                    self.db.session.commit()
                return redirect(url_for('edit_menu'))
            return render_template("edit_menu.html")
        
        @self.app.route("/admin_menu")
        def admin_menu():
            menus = self.db.session.execute(text("SELECT * FROM menu")).mappings().all()
            return render_template("admin_menu.html", menu_list=menus)
            
        @self.app.route("/update_process", methods=["POST"])
        def update_process():
            id = request.form["id"]
            img_path = None
            
            # Only update image if a new one is uploaded
            if "img" in request.files and request.files["img"].filename:
                img = request.files["img"]
                filename = os.path.join(self.app.config["UPLOAD"], img.filename)
                img.save(filename)
                img_path = "static/" + img.filename

            query = text("""
                UPDATE menu SET name=:n, price=:p, img=COALESCE(:i, img) WHERE id=:id
            """)
            self.db.session.execute(query, {
                "n": request.form["name"], "p": request.form["price"], "i": img_path, "id": id
            })
            self.db.session.commit()
            return redirect("/admin_menu")

        @self.app.route("/deletes", methods=["POST"])
        def deletes(): 
            self.db.session.execute(text("DELETE FROM menu WHERE id=:id"), {"id": request.form["id"]})
            self.db.session.commit()
            return redirect("/admin_menu")
            
        # --- STATIC PAGES ---
        @self.app.route("/aboutus")
        def aboutus(): return render_template("aboutus.html")
            
        @self.app.route("/termsandconditions")
        def terms(): return render_template("terms.html")
            
        @self.app.route("/privacypolicy")
        def privacy(): return render_template("privacy.html")
            
        @self.app.route('/contact', methods=["POST", "GET"])
        def contact():
            if request.method == "POST":
                self.db.session.execute(text("""
                    INSERT INTO messages (name, email, message) VALUES (:n, :e, :m)
                """), {"n": request.form['name'], "e": request.form['email'], "m": request.form['message']})
                self.db.session.commit()
                return redirect("/contact")
            return render_template("contact.html")
        
        @self.app.route('/admin_contactus')
        def admin_contact():
            messages = self.db.session.execute(text("SELECT * FROM messages ORDER BY id DESC")).mappings().all()
            return render_template('admin_contact.html', messages=messages)
        
 # 1. Initialize your class
delivery_service = OnlineDelivery(__name__)

# 2. Set up the routes (this also sets up self.db)
delivery_service.setup_routes()

# 3. EXPOSE the Flask instance for Gunicorn
app = delivery_service.app

# --- FIX: Use the correct instance name ---
with app.app_context():
    delivery_service.db.create_all()

# 4. Only for local PC testing
if __name__ == "__main__":
    app.run(debug=True)
