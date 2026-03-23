from flask import Flask, render_template, redirect, request, url_for, session, flash
import bcrypt
from cryptography.fernet import Fernet
import os
import re
from flask_mysqldb import MySQL
import pymysql
pymysql.install_as_MySQLdb()
from flask_sqlalchemy import SQLAlchemy


class OnlineDelivery:
    def __init__(self, name): 
        self.app = Flask(name)
        self.app.secret_key = "hshshshshs"

        # Check if we are on Render (If DATABASE_URL exists)
        if os.getenv("DATABASE_URL"):
            self.app.config['MYSQL_HOST'] = "mysql-13dadf74-franciselmido867-3a7e.i.aivencloud.com"
            self.app.config['MYSQL_USER'] = "avnadmin"
            # We tell Flask to look for the password on Render, not here!
            self.app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
            self.app.config['MYSQL_PORT'] = 28542
            self.app.config['MYSQL_DB'] = "defaultdb"
        else:
            # LOCAL PC SETTINGS (XAMPP)
            self.app.config['MYSQL_HOST'] = "localhost"
            self.app.config['MYSQL_USER'] = "root"
            self.app.config['MYSQL_PASSWORD'] = ""
            self.app.config['MYSQL_DB'] = "online_delivery"

        self.mysql = MySQL(self.app)
        self.app.config["UPLOAD"] = "static"

    def setup_routes(self):
        
        # 1. Look for the "nickname" DATABASE_URL on Render
        uri = os.getenv("DATABASE_URL")

        # 2. Convert it for SQLAlchemy if it exists (for Aiven)
        if uri and uri.startswith("mysql://"):
            uri = uri.replace("mysql://", "mysql+pymysql://", 1)

        # 3. Apply the URI or use local fallback
        if uri:
            self.app.config['SQLALCHEMY_DATABASE_URI'] = uri
        else:
            # This is for your local XAMPP/WAMP testing
            self.app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/online_delivery"

        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = SQLAlchemy(self.app)

#public  
        @self.app.route("/")
        def home_public():
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM menu")
            menus = cursor.fetchall()
            return render_template("home_public.html", menu_list=menus)
        
        
        @self.app.route("/bestsellers_public")
        def bestseller_public(): 
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM menu WHERE category2 = 'Best Sellers'")
            menus = cursor.fetchall()
            return render_template("bestsellers_public.html", menu_list=menus)
        
        
        @self.app.route("/newproducts_public")
        def newproducts_public(): 
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM menu WHERE category2 = 'New Products'")
            menus = cursor.fetchall()
            return render_template("newproducts_public.html", menu_list=menus)
        
        @self.app.route("/burger_public")
        def burger_public(): 
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM menu WHERE category = 'Burgers'")
            menus = cursor.fetchall()
            return render_template("burger_public.html", menu_list=menus)
        
        @self.app.route("/filipinofoods_public")
        def filipinofoods_public(): 
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM menu WHERE category2 = 'Filipino Foods'")
            menus = cursor.fetchall()
            return render_template("filipinofoods_public.html", menu_list=menus)
        
        
        
        @self.app.route("/meal_public")
        def meal_public(): 
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM menu WHERE category = 'Meal'")
            menus = cursor.fetchall()
            return render_template("meal_public.html", menu_list=menus)
        
        
        
        @self.app.route("/snack_public")
        def snack_public(): 
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM menu WHERE category = 'Snacks'")
            menus = cursor.fetchall()
            return render_template("snack_public.html", menu_list=menus)
        
        @self.app.route("/drinks_public")
        def drinks_public(): 
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM menu WHERE category = 'Drinks N Desserts'")
            menus = cursor.fetchall()
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

        def is_admin():
            return session.get('role') == 'admin'

        def is_user():
            return session.get('role') == 'user'
        
        @self.app.route("/login")
        def login():
            return render_template("login.html")
        
        
        @self.app.route("/login_process", methods=["POST", "GET"])
        def login_process():
            # Static admin check as requested
            if request.form.get("username") == "admin" and request.form.get("password") == "francis":
                session["role"] = "admin"
                session["user"] = "admin"
                return redirect("/admin")
            
            if request.method == "POST":
                user_textbox = request.form["username"]
                pass_textbox = request.form["password"]

                cursor = self.mysql.connection.cursor()
                # Check for user by username
                cursor.execute("SELECT id, Password, status FROM register WHERE Username=%s", (user_textbox,))
                account_found = cursor.fetchone()
                
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
            else:
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
                
                # Hash the password before storing it
                hashed_password = bcrypt.hashpw(std_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                cursor = self.mysql.connection.cursor()
                cursor.execute("INSERT INTO register (First_name, Last_name, Age, Address, Contact, Username, Password) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                               (std_first, std_last, std_age, std_address, std_contact, std_username, hashed_password))
                self.mysql.connection.commit()
                cursor.close()
                    
                return redirect(url_for('login'))
            else:
                return render_template("register.html")

######################
#Menus

        @self.app.route("/home")
        def home():
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu")
                menus = cursor.fetchall()
                
                cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
                cart_count = cursor.fetchone()[0]
                
                return render_template("home.html", menu_list=menus, cart_count=cart_count)
            else:
                return redirect("/login")
            
            
        @self.app.route("/search", methods=["GET", "POST"])
        def search():
            if "user" in session:
                search = request.form.get("search")
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu WHERE name LIKE %s", (search,))
                menus = cursor.fetchall()
                
                cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
                cart_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()
                
                
                return render_template("search.html", menu_list=menus, search=search, cart_count=cart_count, user_info=user_info)
            else:
                return redirect("/login")
            

        @self.app.route("/bestsellers")
        def bestsellers(): 
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu WHERE category2 = 'Best Sellers'")
                menus = cursor.fetchall()
                
                cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
                cart_count = cursor.fetchone()[0]
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()
                
                return render_template("bestsellers.html", menu_list=menus, cart_count=cart_count, user_info=user_info)
                
            else:
                return redirect('/login')
            
            
        @self.app.route("/newproducts")
        def newproducts(): 
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu WHERE category2 = 'New Products'")
                menus = cursor.fetchall()
                
                cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
                cart_count = cursor.fetchone()[0]
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()
                
                return render_template("newproducts.html", menu_list=menus, cart_count=cart_count, user_info=user_info)
                
            else:
                return redirect('/login')
            


        @self.app.route("/burger")
        def burger(): 
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu WHERE category = 'Burgers'")
                menus = cursor.fetchall()
                
                cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
                cart_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()
                
                return render_template("burger.html", menu_list=menus, cart_count=cart_count, user_info=user_info)
            else:
                return redirect('/login')
            
        
        @self.app.route("/filipinofoods")
        def filipinofoods(): 
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu WHERE category2 = 'Filipino Foods'")
                menus = cursor.fetchall()
                
                cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
                cart_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()
                
                return render_template("filipinofoods.html", menu_list=menus, cart_count=cart_count, user_info=user_info)
            else:
                return redirect('/login')
            

        @self.app.route("/meal")
        def meal(): 
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu WHERE category = 'Meal'")
                menus = cursor.fetchall()
                
                cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
                cart_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()
                
                return render_template("meal.html", menu_list=menus, cart_count=cart_count, user_info=user_info)
            else:
                return redirect('/login')
            

        @self.app.route("/snack")
        def snack():
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu WHERE category = 'Snacks'")
                menus = cursor.fetchall()
                
                cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
                cart_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()
                
                return render_template("snack.html", menu_list=menus, cart_count=cart_count, user_info=user_info)
            else:
                return redirect('/login')
            

        @self.app.route("/drinks")
        def drinks(): 
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu WHERE category = 'Drinks N Desserts'")
                menus = cursor.fetchall()
                cursor.execute("SELECT COUNT(*) FROM cart WHERE user_id = %s", (user_id,))
                cart_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()
                
                return render_template("drinks.html", menu_list=menus, cart_count=cart_count, user_info=user_info)
            else:
                return redirect("/login")
            
        
        
#########################
#Add to cart process           

        @self.app.route("/add_to_cart_search", methods=["POST"])
        def add_to_cart_search():
            if "user" in session:
                item_name = request.form['item_name']
                item_price = request.form['item_price']
                item_img = request.form['item_img'] 
                quantity = request.form['quantity']

                total_price = float(item_price) * int(quantity)


                cursor = self.mysql.connection.cursor()
                user_id = session["user"]
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", (item_name, quantity, item_price, item_img, total_price, user_id))
                self.mysql.connection.commit()

                return redirect(url_for('search'))
            else:
                return redirect("/login")

    
        @self.app.route("/add_to_cart", methods=["POST"])
        def add_to_cart():
            if "user" in session:
                item_name = request.form['item_name']
                item_price = request.form['item_price']
                item_img = request.form['item_img'] 
                quantity = request.form['quantity']

                total_price = float(item_price) * int(quantity)


                cursor = self.mysql.connection.cursor()
                user_id = session["user"]
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", (item_name, quantity, item_price, item_img, total_price, user_id))
                self.mysql.connection.commit()

                return redirect(url_for('home'))
            else:
                return redirect("/login")
            
        @self.app.route("/place_the_order", methods=["GET", "POST"])
        def place_the_order():
            if request.method == "POST":
                item_name = request.form['item_name']
                item_price = request.form['item_price']
                item_img = request.form['item_img'] 
                quantity = request.form['quantity']
                name = request.form['name']
                address = request.form['address']
                number = request.form['number']
                
                total_price = float(item_price) * int(quantity)
                cursor = self.mysql.connection.cursor()
                user_id = session["user"]
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()
                
                return render_template(
                    "place_the_order.html", 
                    item_name=item_name, 
                    item_price=item_price, 
                    item_img=item_img, 
                    quantity=quantity, total_price=total_price,
                    name=name, address=address, number=number, user_info=user_info
                )
            return render_template("cart.html")
            
        @self.app.route("/place_order", methods=["POST"])
        def place_order():
            if "user" in session:
                
                if request.method == "POST":
                    item_name = request.form['item_name']
                    item_price = request.form['item_price']
                    item_img = request.form['item_img'] 
                    quantity = request.form['quantity']
                    name = request.form['name']
                    address = request.form['address']
                    number = request.form['number']
                    payment_method = request.form['payment_method']
                    total_price = float(item_price) * int(quantity)


                    cursor = self.mysql.connection.cursor()
                    user_id = session["user"]
                    cursor.execute("INSERT INTO orders (item_name, item_price, item_img, quantity, name, address, number, payment_method, total, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                   (item_name, item_price, item_img, quantity, name, address, number, payment_method, total_price, user_id))
                    self.mysql.connection.commit()
                    

                return redirect(url_for('home'))
            else:
                return redirect("/login")

            

        @self.app.route("/add_to_cart_bestsellers", methods=["POST"])
        def add_to_cart_bestsellers():
            item_names = request.form['item_name']
            item_price = request.form['item_price']
            item_img = request.form['item_img']
            quantity = request.form['quantity']

            total_price = float(item_price) * int(quantity)

            cursor = self.mysql.connection.cursor()
            user_id = session["user"]

            cursor.execute("SELECT quantity, total_price FROM cart WHERE item_name = %s AND user_id = %s", (item_names, user_id))
            existing_item = cursor.fetchone()

            if existing_item:
      
                new_quantity = existing_item[0] + int(quantity)
                new_total_price = new_quantity * float(item_price)
                cursor.execute("UPDATE cart SET quantity = %s, total_price = %s WHERE item_name = %s AND user_id = %s", 
                       (new_quantity, new_total_price, item_names, user_id))
            else:
      
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (item_names, quantity, item_price, item_img, total_price, user_id))

            self.mysql.connection.commit()

            return redirect(url_for('bestsellers'))
        

        @self.app.route("/add_to_cart_newproducts", methods=["POST"])
        def add_to_cart_newproducts():
            item_name = request.form['item_name']
            item_price = request.form['item_price']
            item_img = request.form['item_img']
            quantity = request.form['quantity']

            total_price = float(item_price) * int(quantity)

            cursor = self.mysql.connection.cursor()
            user_id = session["user"]

            cursor.execute("SELECT quantity, total_price FROM cart WHERE item_name = %s AND user_id = %s", (item_name, user_id))
            existing_item = cursor.fetchone()

            if existing_item:
      
                new_quantity = existing_item[0] + int(quantity)
                new_total_price = new_quantity * float(item_price)
                cursor.execute("UPDATE cart SET quantity = %s, total_price = %s WHERE item_name = %s AND user_id = %s", 
                       (new_quantity, new_total_price, item_name, user_id))
            else:
      
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (item_name, quantity, item_price, item_img, total_price, user_id))

            self.mysql.connection.commit()

            return redirect(url_for('newproducts'))
        


        @self.app.route("/add_to_cart_burger", methods=["POST"])
        def add_to_cart_burger():
            item_name = request.form['item_name']
            item_price = request.form['item_price']
            item_img = request.form['item_img']
            quantity = request.form['quantity']

            total_price = float(item_price) * int(quantity)

            cursor = self.mysql.connection.cursor()
            user_id = session["user"]

            cursor.execute("SELECT quantity, total_price FROM cart WHERE item_name = %s AND user_id = %s", (item_name, user_id))
            existing_item = cursor.fetchone()

            if existing_item:
      
                new_quantity = existing_item[0] + int(quantity)
                new_total_price = new_quantity * float(item_price)
                cursor.execute("UPDATE cart SET quantity = %s, total_price = %s WHERE item_name = %s AND user_id = %s", 
                       (new_quantity, new_total_price, item_name, user_id))
            else:
      
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (item_name, quantity, item_price, item_img, total_price, user_id))

            self.mysql.connection.commit()

            return redirect(url_for('burger'))

        

        @self.app.route("/add_to_cart_filipinofoods", methods=["POST"])
        def add_to_cart_filipinofoods():
            item_name = request.form['item_name']
            item_price = request.form['item_price']
            item_img = request.form['item_img']
            quantity = request.form['quantity']

            total_price = float(item_price) * int(quantity)

            cursor = self.mysql.connection.cursor()
            user_id = session["user"]

            cursor.execute("SELECT quantity, total_price FROM cart WHERE item_name = %s AND user_id = %s", (item_name, user_id))
            existing_item = cursor.fetchone()

            if existing_item:
      
                new_quantity = existing_item[0] + int(quantity)
                new_total_price = new_quantity * float(item_price)
                cursor.execute("UPDATE cart SET quantity = %s, total_price = %s WHERE item_name = %s AND user_id = %s", 
                       (new_quantity, new_total_price, item_name, user_id))
            else:
      
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (item_name, quantity, item_price, item_img, total_price, user_id))

            self.mysql.connection.commit()

            return redirect(url_for('filipinofoods'))
        


        @self.app.route("/add_to_cart_snack", methods=["POST"])
        def add_to_cart_snack():
            item_name = request.form['item_name']
            item_price = request.form['item_price']
            item_img = request.form['item_img']
            quantity = request.form['quantity']

            total_price = float(item_price) * int(quantity)

            cursor = self.mysql.connection.cursor()
            user_id = session["user"]

            cursor.execute("SELECT quantity, total_price FROM cart WHERE item_name = %s AND user_id = %s", (item_name, user_id))
            existing_item = cursor.fetchone()

            if existing_item:
      
                new_quantity = existing_item[0] + int(quantity)
                new_total_price = new_quantity * float(item_price)
                cursor.execute("UPDATE cart SET quantity = %s, total_price = %s WHERE item_name = %s AND user_id = %s", 
                       (new_quantity, new_total_price, item_name, user_id))
            else:
      
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (item_name, quantity, item_price, item_img, total_price, user_id))

            self.mysql.connection.commit()

            return redirect(url_for('snack'))
        


        @self.app.route("/add_to_cart_drinks", methods=["POST"])
        def add_to_cart_drinks():
            item_name = request.form['item_name']
            item_price = request.form['item_price']
            item_img = request.form['item_img']
            quantity = request.form['quantity']

            total_price = float(item_price) * int(quantity)

            cursor = self.mysql.connection.cursor()
            user_id = session["user"]

            cursor.execute("SELECT quantity, total_price FROM cart WHERE item_name = %s AND user_id = %s", (item_name, user_id))
            existing_item = cursor.fetchone()

            if existing_item:
      
                new_quantity = existing_item[0] + int(quantity)
                new_total_price = new_quantity * float(item_price)
                cursor.execute("UPDATE cart SET quantity = %s, total_price = %s WHERE item_name = %s AND user_id = %s", 
                       (new_quantity, new_total_price, item_name, user_id))
            else:
      
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (item_name, quantity, item_price, item_img, total_price, user_id))

            self.mysql.connection.commit()

            return redirect(url_for('drinks'))
        
        @self.app.route("/add_to_cart_meal", methods=["POST"])
        def add_to_cart_meal():
            item_name = request.form['item_name']
            item_price = request.form['item_price']
            item_img = request.form['item_img']
            quantity = request.form['quantity']

            total_price = float(item_price) * int(quantity)

            cursor = self.mysql.connection.cursor()
            user_id = session["user"]

            cursor.execute("SELECT quantity, total_price FROM cart WHERE item_name = %s AND user_id = %s", (item_name, user_id))
            existing_item = cursor.fetchone()

            if existing_item:
      
                new_quantity = existing_item[0] + int(quantity)
                new_total_price = new_quantity * float(item_price)
                cursor.execute("UPDATE cart SET quantity = %s, total_price = %s WHERE item_name = %s AND user_id = %s", 
                       (new_quantity, new_total_price, item_name, user_id))
            else:
      
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (item_name, quantity, item_price, item_img, total_price, user_id))

            self.mysql.connection.commit()

            return redirect(url_for('meal'))
        



        @self.app.route("/add_to_cart_dessert", methods=["POST"])
        def add_to_cart_dessert():
            item_name = request.form['item_name']
            item_price = request.form['item_price']
            item_img = request.form['item_img']
            quantity = request.form['quantity']

            total_price = float(item_price) * int(quantity)

            cursor = self.mysql.connection.cursor()
            user_id = session["user"]

            cursor.execute("SELECT quantity, total_price FROM cart WHERE item_name = %s AND user_id = %s", (item_name, user_id))
            existing_item = cursor.fetchone()

            if existing_item:
      
                new_quantity = existing_item[0] + int(quantity)
                new_total_price = new_quantity * float(item_price)
                cursor.execute("UPDATE cart SET quantity = %s, total_price = %s WHERE item_name = %s AND user_id = %s", 
                       (new_quantity, new_total_price, item_name, user_id))
            else:
      
                cursor.execute("INSERT INTO cart (item_name, quantity, item_price, item_img, total_price, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (item_name, quantity, item_price, item_img, total_price, user_id))

            self.mysql.connection.commit()

            return redirect(url_for('dessert'))


########################

        @self.app.route("/cart")
        def cart():
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()

                cursor.execute("SELECT * FROM cart WHERE user_id=%s", (user_id,))
                cart_items = cursor.fetchall()

                total_price = sum(item[3] * item[2] for item in cart_items)
                
                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()

                return render_template("cart.html", cart_items=cart_items, total_price=total_price, user_info=user_info)
            else:
                return redirect("/login")
            
        @self.app.route("/confirmation", methods=["POST"])
        def confirmation():
            if "user" in session:
                user_id = session["user"]
                selected_items = request.form.getlist("selected_items")

                cursor = self.mysql.connection.cursor()
                
                items_for_order = []
                total_order_price = 0

                for item_id in selected_items:
                    cursor.execute("SELECT item_name, quantity, item_price, item_img FROM cart WHERE id=%s AND user_id=%s", (item_id, user_id))
                    item = cursor.fetchone()
                    if item:
                        item_name, quantity, item_price, item_img = item
                        total_price = item_price * quantity
                        total_order_price += total_price
                        items_for_order.append({
                            "item_id": item_id,
                            "item_name": item_name,
                            "quantity": quantity,
                            "item_price": item_price,
                            "total_price": total_price,
                            "item_img": item_img
                        })

                cursor.execute("SELECT First_name, Last_name, Address, Contact FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()

                return render_template("confirmation.html", items_for_order=items_for_order, total_order_price=total_order_price, user_info=user_info)
        
        
        @self.app.route("/confirm_order", methods=["POST"])
        def confirm_order():
            if "user" in session:
                user_id = session["user"]
                
                item_ids = request.form.getlist("item_id")
                item_names = request.form.getlist("item_name")
                item_prices = request.form.getlist("item_price")
                item_imgs = request.form.getlist("item_img")
                quantities = request.form.getlist("item_quantity")
                total_prices = request.form.getlist("item_total_price")
                
                name = request.form['user_name']
                address = request.form['address']
                number = request.form['number']
                payment_method = request.form['payment_method']

                cursor = self.mysql.connection.cursor()
                
                for item_id, item_name, item_price, item_img, quantity, total_price in zip(
                        item_ids, item_names, item_prices, item_imgs, quantities, total_prices):
                    
                    cursor.execute("""
                        INSERT INTO orders 
                        (item_name, item_price, item_img, quantity, name, address, number, payment_method, total, user_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (item_name, item_price, item_img, quantity, name, address, number, payment_method, total_price, user_id))

                    cursor.execute("DELETE FROM cart WHERE id=%s AND user_id=%s", (item_id, user_id))

                self.mysql.connection.commit()
                cursor.close()

                return redirect(url_for("cart"))

            return redirect(url_for("login"))




        
        @self.app.route("/history", methods=["POST"])
        def history(): 
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()

                cursor.execute("SELECT * FROM orders WHERE status ='order deliver' AND user_id=%s", (user_id,))
                orders_items = cursor.fetchall()

            return render_template("history.html", orders_items=orders_items)


        @self.app.route("/delete", methods=["POST"])
        def delete(): 
            delete = request.form["id"]

            cursor = self.mysql.connection.cursor()
            cursor.execute("DELETE FROM cart WHERE id=%s",(delete,))
            self.mysql.connection.commit()
            return redirect("/cart")    
        

        @self.app.route("/profile", methods=['GET', 'POST'])
        def profile():
            if "user" in session:
                user_id = session["user"]
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT First_name, Last_name, Age, Address, Contact, Username, Password, Profile FROM register WHERE ID=%s", (user_id,))
                user_info = cursor.fetchone()

                if request.method == 'POST':
      
                    if 'profile_picture' in request.files:
                        profile_picture = request.files['profile_picture']
                        if profile_picture and profile_picture.filename:
                   
                            filename = os.path.join(self.app.config["UPLOAD"], profile_picture.filename)
                            profile_picture.save(filename)
                            
                          
                            profile_path = "static/" + profile_picture.filename
                            cursor.execute("UPDATE register SET Profile=%s WHERE ID=%s", (profile_path, user_id))
                            self.mysql.connection.commit()

                    elif 'delete' in request.form:
                        cursor.execute("UPDATE register SET Profile=NULL WHERE ID=%s", (user_id,))
                        self.mysql.connection.commit()

                    cursor.close()
                    return redirect(url_for('profile'))

                cursor.close()
                return render_template("profile.html", user_info=user_info)
            else:
                return redirect("/login")

          
        @self.app.route('/logout', methods=['POST'])
        def logout():
            session.pop('user', None)
            return redirect('/login')

        @self.app.route("/update_profile", methods=["GET", "POST"])
        def update_profile():
            if "user" in session:
                user_id = session["user"]
                
                if request.method == "POST":
            
                    first_name = request.form["firstname"]
                    last_name = request.form["lastname"]
                    age = request.form["age"]
                    address = request.form["address"]
                    contact = request.form["contact"]
                    username = request.form["username"]
                    password = request.form["password"]
                    profile = request.files["profile"]
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    filename = os.path.join(self.app.config["UPLOAD"], profile.filename)
                    profile.save(filename)
                    
                    profile ="static/" + profile.filename
                    
                
                    cursor = self.mysql.connection.cursor()
                    cursor.execute("""
                        UPDATE register
                        SET First_name=%s, Last_name=%s, Age=%s, Address=%s, Contact=%s, Username=%s, Password=%s, Profile=%s
                        WHERE ID=%s
                    """, (first_name, last_name, age, address, contact, username, hashed_password, profile, user_id))
                    self.mysql.connection.commit()
                    cursor.close()
                    
                    return redirect(url_for('profile'))
                
                else:
                
                    cursor = self.mysql.connection.cursor()
                    cursor.execute("SELECT First_name, Last_name, Age, Address, Contact FROM register WHERE ID=%s", (user_id,))
                    user_info = cursor.fetchone()
                    cursor.close()
                    
                    return render_template("update_profile.html", user_info=user_info)
            
            else:
                return redirect("/login")
            

        @self.app.route("/admin")
        def admin():
            cursor = self.mysql.connection.cursor()
           
            cursor.execute("""
                SELECT item_name, DATE(date_order) as order_date, SUM(quantity) as total_quantity, item_price, SUM(quantity * item_price) as total_price
                FROM orders
                WHERE status = 'order deliver'
                GROUP BY item_name, DATE(date_order)
                ORDER BY order_date DESC
            """)
            sales_data = cursor.fetchall()
            cursor.close()

            
            overall_total_price = sum(record[4] for record in sales_data) 
            return render_template("admin.html", sales_data=sales_data, overall_total_price=overall_total_price)


        
        @self.app.route("/orders")
        def orders():
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM orders WHERE status IS NULL OR status = ''")
                cart_items = cursor.fetchall()
                return render_template("orders.html", cart_items=cart_items)
            
        @self.app.route("/success", methods=["POST"])
        def success(): 
             if request.method == "POST":
                id = request.form["id"]
                status = request.form["status"]
                cursor = self.mysql.connection.cursor()
                cursor.execute(
                    "UPDATE orders SET status=%s WHERE Id=%s", 
                    (status, id)
                )
                self.mysql.connection.commit()
                cursor.close()
                return redirect(url_for('orders'))
        
        @self.app.route("/accounts")
        def accounts():
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM register")
                user_info = cursor.fetchall()
                return render_template("accounts.html", user_info=user_info)
            
        @self.app.route("/restricted", methods=["GET", "POST"])
        def restricted():
            if request.method == "POST":
                id = request.form["Id"]
                status = request.form["status"]
            
                cursor = self.mysql.connection.cursor()
                cursor.execute(
                    "UPDATE register SET status=%s WHERE Id=%s", 
                    (status, id)
                )
                self.mysql.connection.commit()
                cursor.close()

                return redirect(url_for('accounts'))
            
        @self.app.route("/restricted_remove", methods=["GET", "POST"])
        def restricted_remove():
            if request.method == "POST":
                id = request.form["Id"]
                status = request.form["status"]
            

                cursor = self.mysql.connection.cursor()
                cursor.execute(
                    "UPDATE register SET status=%s WHERE Id=%s", 
                    (status, id)
                )
                self.mysql.connection.commit()
                cursor.close()

                return redirect(url_for('accounts'))

            
            
        @self.app.route("/admin_delete", methods=["POST"])
        def admin_delete(): 
            delete = request.form["Id"]

            cursor = self.mysql.connection.cursor()
            cursor.execute("DELETE FROM register WHERE Id=%s",(delete,))
            self.mysql.connection.commit()
            return redirect("/accounts")
        
        @self.app.route("/edit_menu", methods=["GET", "POST"])
        def edit_menu():
            if request.method == "POST":
                name = request.form["name"]
                price = request.form["price"]
                img = request.files["img"]
                category = request.form["category"]
                category2 = request.form["category2"]
                filename = os.path.join(self.app.config["UPLOAD"], img.filename)
                img.save(filename)
                
                img ="static/" + img.filename
            

                cursor = self.mysql.connection.cursor()
                cursor.execute(
                    "INSERT INTO menu (name, price, img, category, category2) VALUES (%s, %s, %s, %s, %s)", 
                    (name, price, img, category, category2)
                )
                self.mysql.connection.commit()
                cursor.close()

                return redirect(url_for('edit_menu'))

            return render_template("edit_menu.html")
        
        @self.app.route("/admin_menu")
        def admin_menu():
           
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM menu")
                menus = cursor.fetchall()
                return render_template("admin_menu.html", menu_list=menus)
           
            
        @self.app.route("/update_menu", methods=["GET", "POST"])
        def update_menu():
            if request.method =="POST":
                id = request.form["id"]
                name = request.form["name"]
                price = request.form["price"]
                img = request.form["img"]
                return render_template("update_menu.html", id=id, name=name, price=price, img=img)
            
        @self.app.route("/update_process", methods=["GET", "POST"])
        def update_process():
            if request.method =="POST":
                id = request.form["id"]
                name = request.form["name"]
                price = request.form["price"]
                img = request.files["img"]
                
                filename = os.path.join(self.app.config["UPLOAD"], img.filename)
                img.save(filename)
                
                img ="static/" + img.filename
                
                cursor = self.mysql.connection.cursor()
                cursor.execute("UPDATE menu SET name=%s, price=%s, img=%s WHERE id=%s", (name, price, img, id))
                self.mysql.connection.commit()
                return redirect("/admin_menu")
            
        @self.app.route("/deletes", methods=["POST"])
        def deletes(): 
            deletes = request.form["id"]

            cursor = self.mysql.connection.cursor()
            cursor.execute("DELETE FROM menu WHERE id=%s",(deletes,))
            self.mysql.connection.commit()
            return redirect("/admin_menu")
            
            
        @self.app.route("/aboutus")
        def aboutus():            
            return render_template("aboutus.html")
            
            
            
        @self.app.route("/termsandconditions")
        def terms(): 
            
            return render_template("terms.html")
           
            
        @self.app.route("/privacypolicy")
        def privacy(): 
        
            return render_template("privacy.html")
           
            
            
            
        @self.app.route('/contact', methods=["POST", "GET"])
        def contact():
            if request.method == "POST":
                name = request.form['name']
                email = request.form['email']
                message = request.form['message']

            
                cursor = self.mysql.connection.cursor()
                cursor.execute("INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
                self.mysql.connection.commit()
                cursor.close()

                return redirect("/contact")
            else:
                return render_template("contact.html")
        
        @self.app.route('/admin_contactus')
        def admin_contact():
           
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT name, email, message, timestamp FROM messages")
            messages = cursor.fetchall()  
            cursor.close()

            return render_template('admin_contact.html', messages=messages)
        
        
# 1. Initialize your class
x = OnlineDelivery(__name__)

# 2. Set up the routes
x.setup_routes()

# 3. EXPOSE the Flask instance for Gunicorn
app = x.app 

# --- ADD THIS PART HERE (This creates your tables on Render) ---
with app.app_context():
    x.db.create_all()

# 4. Only for local PC testing
if __name__ == "__main__":
    app.run(debug=True)
