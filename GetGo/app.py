from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from datetime import datetime
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'GetGo'

bcrypt = Bcrypt(app)

# Function to get database connection
def get_db_connection(create_db=False):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="SQLfcalista09*"
    )
    cursor = conn.cursor()
    
    if create_db:
        cursor.execute("CREATE DATABASE IF NOT EXISTS get_go;")
    
    cursor.close()
    conn.close()

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="SQLfcalista09*",
        database="get_go"
    )

# Initialize Database
get_db_connection(create_db=True)
db = get_db_connection()
cursor = db.cursor()

cursor.execute("USE get_go;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    category ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    image VARCHAR(255)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    color VARCHAR(30) NOT NULL,
    plate VARCHAR(20) UNIQUE NOT NULL,
    rent_price DECIMAL(10,0) NOT NULL,
    capacity ENUM('2', '5', '7', '12', '16') NOT NULL,
    image VARCHAR(255)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rentals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    car_id INT NOT NULL,
    start_rent_date DATE NOT NULL,
    end_rent_date DATE NOT NULL,
    category ENUM('On Progress', 'Completed') NOT NULL,
    status ENUM('Requested', 'Active', 'Done') NOT NULL,
    sub_status ENUM('Pending', 'Denied', 'Active', 'Done') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE,
    UNIQUE(user_id, car_id, start_rent_date, end_rent_date)
);
""")

cursor.execute("""
INSERT IGNORE INTO users (name, email, password, category, image) VALUES 
('Alice Johnson', 'alice.johnson@example.com', 'hashed_password_1', 'user', 'Profile1.png'), 
('Bob Smith', 'bob.smith@example.com', 'hashed_password_2', 'user', 'Profile2.png'), 
('Charlie Davis', 'charlie.davis@example.com', 'hashed_password_3', 'user', 'Profile3.png'), 
('David Wilson', 'david.wilson@example.com', 'hashed_password_4', 'user', 'Profile4.png'), 
('Emma Brown', 'emma.brown@example.com', 'hashed_password_5', 'user','Profile5.png'), 
('Frank White', 'frank.white@example.com', 'hashed_password_6', 'user','Profile6.png'), 
('Grace Hall', 'grace.hall@example.com', 'hashed_password_7', 'user','Profile7.png'), 
('Henry Adams', 'henry.adams@example.com', 'hashed_password_8', 'admin', 'Profile8.png'), 
('Ivy Scott', 'ivy.scott@example.com', 'hashed_password_9', 'admin', 'Profile9.png'), 
('Jack Taylor', 'jack.taylor@example.com', 'hashed_password_10', 'user', 'Profile10.png'); 
""")

cursor.execute("""
INSERT IGNORE INTO cars (brand, type, color, plate, rent_price, capacity, image) VALUES 
('Mercedes-Benz', 'Sports', 'Black', 'B 9999 VIP', 2000000, '2', 'Benz.jpg'),
('Toyota', 'Van', 'Silver', 'B 5678 STU', 200000, '12', 'Van.jpg'),
('Scania', 'Bus', 'White', 'B 1234 EFG', 250000, '16', 'Scania.jpg'),
('Toyota', 'Sedan', 'Black', 'B 1234 ABC', 100000, '5', 'Toyota_Sedan.png'), 
('Honda', 'SUV', 'Blue', 'B 1357 RTY', 160000, '7', 'HondaSUV.jpg'), 
('Nissan', 'Sedan', 'Gray', 'B 9753 LKJ', 110000, '5', 'NissanSedan.jpg'),
('Tesla', 'Electric', 'White', 'B 2222 EV', 1500000, '5', 'TeslaElectric.png'),
('Ford', 'Pickup', 'Red', 'B 4567 FOR', 1800000, '5', 'FordPickUp.jpg'),
('BMW', 'Sedan', 'Black', 'B 7890 BMW', 200000, '5', 'BMWSedan.webp'),
('Hyundai', 'SUV', 'Silver', 'B 3333 HYN', 140000, '7', 'HyundaiSuv.jpg'),
('Mazda', 'Sedan', 'Blue', 'B 4444 MZD', 120000, '5', 'MazdaSedan.jpg'),
('Chevrolet', 'SUV', 'Green', 'B 5 555 CHV', 170000, '7', 'Chevrolet.jpg');
""")

cursor.execute("""
INSERT IGNORE INTO rentals (user_id, car_id, start_rent_date, end_rent_date, category, status, sub_status) VALUES
(1, 1, '2025-03-31', '2025-04-01', 'Completed', 'Done', 'Done'),
(2, 1, '2025-04-02', '2025-04-04', 'Completed', 'Done', 'Done'),
(1, 2, '2025-04-05', '2025-04-06', 'Completed', 'Done', 'Done');
""")

db.commit()
cursor.close()
db.close()

def update_rental_status():
    db = get_db_connection()
    cursor = db.cursor()

    update_query = """
        UPDATE rentals 
        SET category = 'Completed', status = 'Done', sub_status = 'Done' 
        WHERE end_rent_date < CURDATE() 
        AND (category != 'Completed' OR status != 'Done' OR sub_status != 'Done')
    """
    cursor.execute(update_query)
    db.commit()

    cursor.close()
    db.close()

update_rental_status()

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        category = 'user'  # Default category for new users

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("This email is already registered. Please log in.", "warning")
            return redirect(url_for('signup')) 

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        hashed_password = confirm_password

        cursor = db.cursor()

        try:
            sql = "INSERT INTO users (name, email, password, category) VALUES (%s, %s, %s, %s)"
            values = (name, email, hashed_password, category)
            cursor.execute(sql, values)
            db.commit()

            # Store email in session after successful signup
            session['user_id'] = cursor.lastrowid  # Get last inserted user ID
            session['user_name'] = name
            session['user_email'] = email
            session['user_category'] = category

            return redirect(url_for('welcome'))  # Redirect after storing session

        except mysql.connector.Error:
            return redirect(url_for('signup'))

        finally:
            cursor.close()
            db.close()

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if not user:
                flash("Email not found. Please register.", "warning")
                return redirect(url_for('login'))
            
            passw = user['password']  # This should be outside the 'if' check
            
            if password != passw:
                flash("Incorrect password. Please try again.", "danger")
                return redirect(url_for('login'))

            # Store email in session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']  # Store email in session
            session['user_category'] = user['category']

            return redirect(url_for('date'))
        
        except mysql.connector.Error:
            return redirect(url_for('login'))  # Use redirect instead of render_template
        
        finally:
            cursor.close()
            db.close()

    return render_template('login.html')

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM users WHERE email = %s AND category = 'admin'", (email,))
            admin = cursor.fetchone()
        finally:
            cursor.close()
            db.close()

        if admin:
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['name']
            session['admin_email'] = admin['email']  # Store admin email in session
            return redirect(url_for('admin_main_menu'))
        else:
            flash("Invalid admin credentials", "danger")
            return render_template('login_admin.html')

    return render_template('login_admin.html')

@app.route('/date', methods=['GET', 'POST'])
def date():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        session['start_date'] = start_date
        session['end_date'] = end_date

        # Connect to MySQL database
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Query to get available cars (cars that are NOT in rentals)
        query = """
        SELECT * FROM cars 
        WHERE id NOT IN (SELECT car_id FROM rentals)
        """
        cursor.execute(query)
        available_cars = cursor.fetchall()

        # Close database connection
        cursor.close()

        # Store available cars in session
        session['available_cars'] = available_cars

        # Redirect to main_menu page
        return redirect(url_for('main_menu'))

    return render_template('date.html')

@app.route('/admin_main_menu')
def admin_main_menu():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Query to get all cars and their status from rentals
    query = """
    SELECT 
        c.id, 
        c.brand, 
        c.type, 
        c.color, 
        c.plate, 
        c.rent_price, 
        c.capacity, 
        c.image,
        COALESCE(
            CASE 
                WHEN r.status = 'Done' THEN 'Available'
                ELSE r.status
            END, 
            'Available'
        ) AS status
    FROM cars c
    LEFT JOIN (
        SELECT r1.*
        FROM rentals r1
        INNER JOIN (
            SELECT car_id, MAX(id) as latest_rental_id
            FROM rentals
            WHERE sub_status != 'Denied'
            GROUP BY car_id
        ) r2 ON r1.id = r2.latest_rental_id
    ) r ON c.id = r.car_id

    """
    
    cursor.execute(query)
    cars = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_main_menu.html', cars=cars)

@app.route('/admin_available')
def admin_available():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT c.id, c.brand, c.type, c.color, c.plate, c.rent_price, c.capacity, c.image
    FROM cars c
    LEFT JOIN rentals r ON c.id = r.car_id
    WHERE r.car_id IS NULL OR r.sub_status = 'Denied' OR r.sub_status = 'Done'
    """

    cursor.execute(query)
    available_cars = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_available.html', cars=available_cars)

@app.route('/admin_requested', methods=['GET', 'POST'])
def admin_requested():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        # Handle the status update
        rental_id = request.form.get("rental_id")
        action = request.form.get("sub_status") 
        print(action)
        if rental_id and action:
            if action == "Denied":
                update_query = "UPDATE rentals SET sub_status = %s WHERE id = %s"
                cursor.execute(update_query, ('Denied', rental_id))
            else:  # Default action is Approve
                update_query = "UPDATE rentals SET sub_status = %s, status = %s WHERE id = %s"
                cursor.execute(update_query, ('Active', 'Active', rental_id))

            db.commit()

            return redirect(url_for('admin_active'))

    # Fetch updated rental data for GET request or after update
    query = """
    SELECT r.id AS rental_id, r.user_id, u.name AS user_name, c.brand, c.plate, 
           c.capacity, c.color, r.start_rent_date, r.end_rent_date, r.sub_status,
           c.rent_price, c.image
    FROM rentals r
    JOIN cars c ON r.car_id = c.id
    JOIN users u ON r.user_id = u.id
    WHERE r.sub_status = 'Pending'
    """

    cursor.execute(query)
    requested_rentals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_requested.html', rentals=requested_rentals)

@app.route('/admin_active')
def admin_active():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT r.user_id, c.brand, c.plate, u.name AS user_name, c.capacity, c.color, 
       r.start_rent_date, r.end_rent_date, c.rent_price, c.image
    FROM rentals r
    JOIN cars c ON r.car_id = c.id
    JOIN users u ON r.user_id = u.id
    WHERE r.status = 'Active'
    """
    
    cursor.execute(query)
    active_rentals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_active.html', rentals=active_rentals)

@app.route('/main_menu')
def main_menu():
    start_date = session.get('start_date')
    end_date = session.get('end_date')
    user_id = session.get('user_id')  # Assuming user_id is stored in the session

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Query to get available cars
    query_cars = """
    SELECT * FROM cars 
    WHERE id NOT IN (
        SELECT car_id FROM rentals 
        WHERE sub_status NOT IN ('Done', 'Denied') -- Exclude rentals where sub_status is NOT 'Done'
        AND (
            (start_rent_date BETWEEN %s AND %s) OR 
            (end_rent_date BETWEEN %s AND %s) OR 
            (start_rent_date <= %s AND end_rent_date >= %s) -- Fully overlapping range
        )
    )
    """
    cursor.execute(query_cars, (start_date, end_date, start_date, end_date, start_date, end_date))
    cars = cursor.fetchall()

    # Check if the current user has an active rental
    query_user_rental = """
    SELECT COUNT(*) AS count 
    FROM rentals 
    WHERE user_id = %s 
    AND end_rent_date >= CURDATE() 
    AND sub_status != 'Denied'
    """
    cursor.execute(query_user_rental, (user_id,))
    user_rental_status = cursor.fetchone()
    user_has_rental = user_rental_status['count'] > 0  # True if user has an active rental

    cursor.close()
    db.close()

    return render_template('main_menu.html', cars=cars, user_has_rental=user_has_rental)


@app.route('/brand_page')
def brand_page():
    brand_name = request.args.get('brand_name', '').strip()

    # Retrieve start_date and end_date from session (handle None values)
    start_date = session.get('start_date') 
    end_date = session.get('end_date') 
    user_id = session.get('user_id')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT * FROM cars 
    WHERE brand LIKE %s 
    AND id NOT IN (
        SELECT car_id FROM rentals 
        WHERE sub_status NOT IN ('Done', 'Denied') -- Exclude rentals where sub_status is NOT 'Done'
        AND (
            (start_rent_date BETWEEN %s AND %s) OR 
            (end_rent_date BETWEEN %s AND %s) OR 
            (start_rent_date <= %s AND end_rent_date >= %s) -- Fully overlapping range
        )
    )
    """

    cursor.execute(query, ('%' + brand_name + '%', start_date, end_date, start_date, end_date, start_date, end_date))
    cars = cursor.fetchall()

    # Check if the current user has an active rental
    query_user_rental = """
    SELECT COUNT(*) AS count 
    FROM rentals 
    WHERE user_id = %s 
    AND end_rent_date >= CURDATE() 
    AND sub_status != 'Denied'
    """
    cursor.execute(query_user_rental, (user_id,))
    user_rental_status = cursor.fetchone()
    user_has_rental = user_rental_status['count'] > 0  # True if user has an active rental

    cursor.close()
    db.close()

    return render_template('brand_page.html', brand_name=brand_name, cars=cars, user_has_rental=user_has_rental)

@app.route('/price_page')
def price_page():
    user_id = session.get('user_id')
    start_date = session.get('start_date') 
    end_date = session.get('end_date')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    query = """
    SELECT * FROM cars 
    WHERE id NOT IN (
        SELECT car_id FROM rentals 
        WHERE sub_status NOT IN ('Done', 'Denied') -- Exclude rentals where sub_status is NOT 'Done'
        AND (
            (start_rent_date BETWEEN %s AND %s) OR 
            (end_rent_date BETWEEN %s AND %s) OR 
            (start_rent_date <= %s AND end_rent_date >= %s) -- Fully overlapping range
        )
    )
    """

    cursor.execute(query, (start_date, end_date, start_date, end_date, start_date, end_date))

    cars = cursor.fetchall()

    # Check if the current user has an active rental
    query_user_rental = """
    SELECT COUNT(*) AS count 
    FROM rentals 
    WHERE user_id = %s 
    AND end_rent_date >= CURDATE() 
    AND sub_status != 'Denied'
    """
    cursor.execute(query_user_rental, (user_id,))
    user_rental_status = cursor.fetchone()
    user_has_rental = user_rental_status['count'] > 0  # True if user has an active rental

    cursor.close()
    db.close()
    
    return render_template("price_page.html", cars=cars, user_has_rental=user_has_rental)

@app.route('/filter_price')
def filter_price():
    user_id = session.get('user_id')
    start_date = session.get('start_date') 
    end_date = session.get('end_date')
    price_range = request.args.get("price_range")
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    query = """
    SELECT * FROM cars 
    WHERE id NOT IN (
        SELECT car_id FROM rentals 
        WHERE sub_status NOT IN ('Done', 'Denied') -- Exclude rentals where sub_status is NOT 'Done'
        AND (
            (start_rent_date BETWEEN %s AND %s) OR 
            (end_rent_date BETWEEN %s AND %s) OR 
            (start_rent_date <= %s AND end_rent_date >= %s) -- Fully overlapping range
        )
    )
    """

    cursor.execute(query, (start_date, end_date, start_date, end_date, start_date, end_date))

    cars = cursor.fetchall()

    # Check if the current user has an active rental
    query_user_rental = """
    SELECT COUNT(*) AS count 
    FROM rentals 
    WHERE user_id = %s 
    AND end_rent_date >= CURDATE() 
    AND sub_status != 'Denied'
    """
    cursor.execute(query_user_rental, (user_id,))
    user_rental_status = cursor.fetchone()
    user_has_rental = user_rental_status['count'] > 0  # True if user has an active rental

    # Apply filtering logic based on price range
    filtered_cars = []
    if price_range == "under_500k":
        filtered_cars = [car for car in cars if car["rent_price"] < 500000]
    elif price_range == "500k_1m":
        filtered_cars = [car for car in cars if 500000 <= car["rent_price"] <= 1000000]
    elif price_range == "1m_2m":
        filtered_cars = [car for car in cars if 1000000 <= car["rent_price"] <= 2000000]
    elif price_range == "above_2m":
        filtered_cars = [car for car in cars if car["rent_price"] > 2000000]

    cursor.close()
    db.close()

    # Return filtered cars along with rental status
    return jsonify({
        "cars": filtered_cars,
        "user_has_rental": user_has_rental
    })


@app.route('/capacity_page')
def capacity_page():
    user_id = session.get('user_id')
    start_date = session.get('start_date') 
    end_date = session.get('end_date')
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    query = """
    SELECT * FROM cars 
    WHERE id NOT IN (
        SELECT car_id FROM rentals 
        WHERE sub_status NOT IN ('Done', 'Denied') -- Exclude rentals where sub_status is NOT 'Done'
        AND (
            (start_rent_date BETWEEN %s AND %s) OR 
            (end_rent_date BETWEEN %s AND %s) OR 
            (start_rent_date <= %s AND end_rent_date >= %s) -- Fully overlapping range
        )
    )
    """

    cursor.execute(query, (start_date, end_date, start_date, end_date, start_date, end_date))
    cars = cursor.fetchall()

    # Check if the current user has an active rental
    query_user_rental = """
    SELECT COUNT(*) AS count 
    FROM rentals 
    WHERE user_id = %s 
    AND end_rent_date >= CURDATE() 
    AND sub_status != 'Denied'
    """
    cursor.execute(query_user_rental, (user_id,))
    user_rental_status = cursor.fetchone()
    user_has_rental = user_rental_status['count'] > 0  # True if user has an active rental

    cursor.close()
    db.close()
    
    return render_template("capacity_page.html", cars=cars, user_has_rental=user_has_rental)

@app.route('/filter_capacity')
def filter_capacity():
    user_id = session.get('user_id')
    start_date = session.get('start_date') 
    end_date = session.get('end_date')
    capacity = request.args.get("capacity")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Query all cars
    query = """
    SELECT * FROM cars 
    WHERE id NOT IN (
        SELECT car_id FROM rentals 
        WHERE sub_status NOT IN ('Done', 'Denied') -- Exclude rentals where sub_status is NOT 'Done'
        AND (
            (start_rent_date BETWEEN %s AND %s) OR 
            (end_rent_date BETWEEN %s AND %s) OR 
            (start_rent_date <= %s AND end_rent_date >= %s) -- Fully overlapping range
        )
    )"""
    cursor.execute(query, (start_date, end_date, start_date, end_date, start_date, end_date))
    cars = cursor.fetchall()

    # Check if the user has an active rental
    query_user_rental = """
    SELECT COUNT(*) AS count 
    FROM rentals 
    WHERE user_id = %s 
    AND end_rent_date >= CURDATE() 
    AND sub_status != 'Denied'
    """
    cursor.execute(query_user_rental, (user_id,))
    user_rental_status = cursor.fetchone()
    user_has_rental = user_rental_status['count'] > 0  # True if user has an active rental

    # Filter cars based on capacity
    filtered_cars = []
    if capacity:
        filtered_cars = [car for car in cars if str(car["capacity"]) == capacity]

    cursor.close()
    db.close()

    # Return filtered cars along with rental status
    return jsonify({
        "cars": filtered_cars,
        "user_has_rental": user_has_rental
    })

@app.route('/details/<int:car_id>')
def details_page(car_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, brand, type, image, color, capacity, plate, rent_price
        FROM cars WHERE id = %s
    """, (car_id,))
    
    car = cursor.fetchone()
    conn.close()

    if not car:
        return "Car not found", 404

    # Retrieve start_date and end_date from session
    start_date = session.get('start_date')
    end_date = session.get('end_date')

    return render_template('details_page.html', car=car, start_date=start_date, end_date=end_date)


@app.route('/rental_tracking')
def rental_tracking():
    user_id = session['user_id']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT r.id, r.start_rent_date, r.end_rent_date, r.category, 
           c.brand, c.type, c.color, c.plate, c.rent_price, c.capacity, c.image
    FROM rentals r
    JOIN cars c ON r.car_id = c.id
    WHERE r.user_id = %s
    ORDER BY r.start_rent_date DESC
    """
    
    cursor.execute(query, (user_id,))
    rentals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('rental_tracking.html', rentals=rentals)

@app.route('/my_orders')
def my_orders():
    user_email = session.get('user_email')  # Retrieve email from session

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT cars.*, rentals.start_rent_date, rentals.end_rent_date, 
               rentals.category, rentals.status, rentals.sub_status 
        FROM rentals 
        JOIN cars ON rentals.car_id = cars.id 
        JOIN users ON rentals.user_id = users.id
        WHERE users.email = %s AND rentals.category = 'On Progress'
    """, (user_email,))
    
    orders = cursor.fetchall()
    cursor.close()

    return render_template('rental_tracking_on_progress.html', rentals=orders)

@app.route('/orders_completed')
def orders_completed():
    user_email = session.get('user_email')  # Retrieve email from session

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT cars.*, rentals.start_rent_date, rentals.end_rent_date, 
               rentals.category, rentals.status, rentals.sub_status 
        FROM rentals 
        JOIN cars ON rentals.car_id = cars.id 
        JOIN users ON rentals.user_id = users.id
        WHERE users.email = %s AND rentals.category = 'Completed'
    """, (user_email,))
    
    orders = cursor.fetchall()
    cursor.close()

    return render_template('rental_tracking_completed.html', rentals=orders)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    user_email = session['user_email']
    car_id = request.form.get('car_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get user ID from email
    cursor.execute("SELECT id FROM users WHERE email = %s", (user_email,))
    user = cursor.fetchone()

    user_id = user['id']
    # Insert into rentals table
    try:
        cursor.execute("""
            INSERT INTO rentals (user_id, car_id, start_rent_date, end_rent_date, category, status, sub_status)
            VALUES (%s, %s, %s, %s, 'On Progress', 'Requested', 'Pending')
        """, (user_id, car_id, start_date, end_date))
        db.commit()

        flash("Payment successful! Your rental request has been submitted.", "success")
    except mysql.connector.Error as err:
        db.rollback()

    cursor.close()
    db.close()

    return redirect(url_for('my_orders'))

@app.route('/admin_car_type')
def admin_car_type():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT 
    c.brand,
    COUNT(DISTINCT c.id) AS total_cars,  -- Count unique cars per brand
    SUM(CASE WHEN r.status = 'Active' THEN 1 ELSE 0 END) AS active_rentals,
    SUM(CASE 
        WHEN r.category = 'Completed' 
        THEN (DATEDIFF(r.end_rent_date, r.start_rent_date) + 1) * c.rent_price 
        ELSE 0 
    END) AS total_active_rent_price,
    COUNT(DISTINCT CASE 
        WHEN r.id IS NULL OR r.sub_status = 'Denied' OR r.sub_status = 'Done' 
        THEN c.id  -- Count unique available cars
        ELSE NULL 
    END) AS available_cars
    FROM cars c
    LEFT JOIN rentals r ON c.id = r.car_id
    GROUP BY c.brand
    ORDER BY c.brand;


    """
    cursor.execute(query)
    car_types = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_car_type.html', car_types=car_types)

@app.route('/admin_cars_name')
def admin_cars_name():
    brand = request.args.get('brand')  # Get brand from URL parameter

    if not brand:
        return "Brand not specified", 400  # Handle missing brand case

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT 
    c.id, c.brand, c.type, c.color, 
    c.plate, c.rent_price, c.capacity, c.image,
    r.start_rent_date, r.end_rent_date,
    u.name AS user_name,  -- Get user name from users table
    COALESCE(SUM((DATEDIFF(r.end_rent_date, r.start_rent_date) + 1) * c.rent_price), 0) AS total_rent_price
    FROM cars c
    JOIN rentals r ON c.id = r.car_id
    JOIN users u ON r.user_id = u.id  -- Join users table to get user name
    WHERE r.category = 'Completed' AND c.brand = %s
    GROUP BY c.id, c.brand, c.type, c.color, c.plate, c.rent_price, 
            c.capacity, c.image, r.start_rent_date, r.end_rent_date, u.name
    ORDER BY c.type ASC;
    """
    
    cursor.execute(query, (brand,))
    cars = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_cars_name.html', cars=cars, brand=brand)


@app.route('/admin_user_id')
def admin_user_id():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT 
    u.id,
    u.name,
    u.email,
    u.image,
    COUNT(r.car_id) AS total_rentals,
    COALESCE(SUM(
        CASE 
            WHEN r.sub_status != 'Denied' 
            THEN c.rent_price * (DATEDIFF(r.end_rent_date, r.start_rent_date) + 1)
            ELSE 0 
        END
    ), 0) AS total_rent_price
    FROM users u
    LEFT JOIN rentals r ON u.id = r.user_id 
        AND r.sub_status != 'Denied' 
    LEFT JOIN cars c ON r.car_id = c.id
    WHERE u.category = 'user'
    GROUP BY u.id, u.name, u.email, u.image
    ORDER BY u.id;

    """
    cursor.execute(query)
    users = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_user_id.html', users=users)

@app.route('/user_car')
def user_car():
    user_id = request.args.get('user_id', None)
    user_name = request.args.get('user_name', 'Unknown')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT 
    u.name AS user_name, 
    r.id AS rental_id, 
    r.start_rent_date, 
    r.end_rent_date, 
    c.brand, 
    c.type, 
    c.color, 
    c.plate, 
    c.rent_price, 
    c.capacity, 
    c.image, 
    (c.rent_price * (DATEDIFF(r.end_rent_date, r.start_rent_date) + 1)) AS total_rent_price
    FROM rentals r
    JOIN cars c ON r.car_id = c.id
    JOIN users u ON r.user_id = u.id
    WHERE r.user_id = %s 
        AND r.sub_status != 'Denied'
    ORDER BY r.start_rent_date DESC;

    """

    cursor.execute(query, (user_id,))
    rentals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('user_car.html', rentals=rentals, user_name=user_name, user_id=user_id)


@app.route('/admin_date', methods=['GET', 'POST'])
def admin_date():
    if request.method == 'POST':
        date = request.form.get('start_date')  # Fix: Match input name in form
        session['date'] = date

        # Connect to MySQL database
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Fix: Correct query to get only available cars
        query = """
        SELECT c.* FROM cars c
        WHERE NOT EXISTS (
            SELECT 1 FROM rentals r
            WHERE c.id = r.car_id
            AND %s BETWEEN r.start_rent_date AND r.end_rent_date
        );
        """
        
        cursor.execute(query, (date,))
        available_cars = cursor.fetchall()
        cursor.close()
        db.close()

        session['available_cars'] = available_cars

        # Redirect to date_show
        return redirect(url_for('date_show'))

    return render_template('admin_date.html')


@app.route('/date_show')
def date_show():
    date = session.get('date')
    if not date:
        return redirect(url_for('admin_date'))  # Redirect if no date is set

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT 
    r.id, 
    r.start_rent_date, 
    r.end_rent_date, 
    r.user_id, 
    u.name AS user_name, 
    c.brand, 
    c.type, 
    c.color, 
    c.plate, 
    c.rent_price, 
    c.capacity, 
    c.image, 
    (c.rent_price * (DATEDIFF(r.end_rent_date, r.start_rent_date) + 1)) AS total_price_spent
    FROM rentals r
    JOIN cars c ON r.car_id = c.id
    JOIN users u ON r.user_id = u.id
    WHERE %s BETWEEN r.start_rent_date AND r.end_rent_date
    AND r.category = 'Completed'
    ORDER BY r.start_rent_date DESC;
    """
    
    cursor.execute(query, (date,))
    rentals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('date_show.html', date=date, rentals=rentals)

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data (if using Flask session)
    return redirect(url_for('welcome'))  # Redirect to the welcome page

if __name__ == '__main__':
    app.run(debug=True)
