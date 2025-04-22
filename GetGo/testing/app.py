from flask import Flask, render_template, request, redirect, url_for, flash, session
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
    category ENUM('user', 'admin') NOT NULL DEFAULT 'user'
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
    status ENUM('Requested', 'Active') NOT NULL,
    sub_status ENUM('Pending', 'Denied', 'Active', 'Approved') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
);
""")

cursor.execute("""
INSERT IGNORE INTO users (name, email, password, category) VALUES 
('Alice Johnson', 'alice.johnson@example.com', 'hashed_password_1', 'user'), 
('Bob Smith', 'bob.smith@example.com', 'hashed_password_2', 'user'), 
('Charlie Davis', 'charlie.davis@example.com', 'hashed_password_3', 'user'), 
('David Wilson', 'david.wilson@example.com', 'hashed_password_4', 'user'), 
('Emma Brown', 'emma.brown@example.com', 'hashed_password_5', 'user'), 
('Frank White', 'frank.white@example.com', 'hashed_password_6', 'user'), 
('Grace Hall', 'grace.hall@example.com', 'hashed_password_7', 'user'), 
('Henry Adams', 'henry.adams@example.com', 'hashed_password_8', 'admin'), 
('Ivy Scott', 'ivy.scott@example.com', 'hashed_password_9', 'admin'), 
('Jack Taylor', 'jack.taylor@example.com', 'hashed_password_10', 'user'); 
""")

cursor.execute("""
INSERT IGNORE INTO cars (brand, type, color, plate, rent_price, capacity, image) VALUES 
('Mercedes-Benz', 'Sports', 'Black', 'B 9999 VIP', 500000, '2', 'Benz.jpg'),
('Toyota', 'Van', 'Silver', 'B 5678 STU', 200000, '12', 'Van.jpg'),
('Scania', 'Bus', 'White', 'B 1234 EFG', 250000, '16', 'Scania.jpg'),
('Toyota', 'Sedan', 'Black', 'B 1234 ABC', 100000, '5', 'Toyota_Sedan.png'), 
('Honda', 'SUV', 'Blue', 'B 1357 RTY', 160000, '7', 'HondaSUV.jpg'), 
('Nissan', 'Sedan', 'Gray', 'B 9753 LKJ', 110000, '5', 'NissanSedan.jpg'),
('Tesla', 'Electric', 'White', 'B 2222 EV', 300000, '5', 'TeslaElectric.png'),
('Ford', 'Pickup', 'Red', 'B 4567 FOR', 180000, '5', 'FordPickUp.jpg'),
('BMW', 'Sedan', 'Black', 'B 7890 BMW', 200000, '5', 'BMWSedan.webp'),
('Hyundai', 'SUV', 'Silver', 'B 3333 HYN', 140000, '7', 'HyundaiSuv.jpg'),
('Mazda', 'Sedan', 'Blue', 'B 4444 MZD', 120000, '5', 'MazdaSedan.jpg'),
('Chevrolet', 'SUV', 'Green', 'B 5555 CHV', 170000, '7', 'Chevrolet.jpg');
""")


db.commit()
cursor.close()
db.close()

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
        category = 'user'  

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("This email is already registered. Please log in.", "warning") 

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        db = get_db_connection()
        cursor = db.cursor()

        try:
            sql = "INSERT INTO users (name, email, password, category) VALUES (%s, %s, %s, %s)"
            values = (name, email, hashed_password, category)
            cursor.execute(sql, values)
            db.commit()
            return redirect(url_for('welcome'))
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
            passw = user['password']

            if not user:
                flash("Email not found. Please register.", "warning")
                return redirect(url_for('login'))
            
            if password != passw:
                flash("Incorrect password. Please try again.", "danger")
                return redirect(url_for('login'))

            # Set session variables
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_category'] = user['category']

            return redirect(url_for('date'))
        
        except mysql.connector.Error:
            flash("An error occurred. Please try again.", "danger")
            return render_template(url_for('login'))
        
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
            return redirect(url_for('admin_main_menu'))
        else:
            return render_template('login_admin.html', error="Invalid admin credentials")

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
    SELECT c.id, c.brand, c.type, c.color, c.plate, c.rent_price, c.capacity, c.image,
           COALESCE(r.status, 'Available') AS status
    FROM cars c
    LEFT JOIN rentals r ON c.id = r.car_id
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
    SELECT c.id, c.brand, c.type, c.color, c.plate, c.rent_price, c.capacity, c.image,
           COALESCE(r.status, 'Available') AS status
    FROM cars c
    LEFT JOIN rentals r ON c.id = r.car_id
    WHERE r.status IS NULL OR r.status = 'Available'
    """
    
    cursor.execute(query)
    available_cars = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_available.html', cars=available_cars)

@app.route('/admin_requested')
def admin_requested():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT r.id, r.user_id, u.name AS user_name, r.car_id, c.brand, c.type, c.plate, 
           r.start_rent_date, r.end_rent_date, r.status, r.sub_status
    FROM rentals r
    JOIN users u ON r.user_id = u.id
    JOIN cars c ON r.car_id = c.id
    WHERE r.status = 'Requested'
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
    SELECT r.id, r.user_id, u.name AS user_name, r.car_id, c.brand, c.type, c.color, c.plate, 
           r.start_rent_date, r.end_rent_date, c.rent_price, c.capacity, c.image
    FROM rentals r
    JOIN users u ON r.user_id = u.id
    JOIN cars c ON r.car_id = c.id
    WHERE r.status = 'Active'
    """
    
    cursor.execute(query)
    active_rentals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_active.html', rentals=active_rentals)

@app.route('/main_menu')
def main_menu():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, brand, type, color, plate, rent_price, capacity, image FROM cars")  
    cars = cursor.fetchall()

    cursor.execute("SELECT DISTINCT brand FROM cars")
    brands = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('main_menu.html', cars=cars)

@app.route('/brand_page/<brand_name>')
def brand_page(brand_name):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM cars WHERE brand = %s"
    cursor.execute(query, (brand_name,))
    cars = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('brand_page.html', brand=brand_name, cars=cars)

@app.route('/price_page/<price_range>')
def price_page(price_range):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if price_range == 'under_500k':
        query = "SELECT * FROM cars WHERE rent_price < 500000"
    elif price_range == '500k_1m':
        query = "SELECT * FROM cars WHERE rent_price BETWEEN 500000 AND 1000000"
    elif price_range == '1m_2m':
        query = "SELECT * FROM cars WHERE rent_price BETWEEN 1000000 AND 2000000"
    else:
        query = "SELECT * FROM cars WHERE rent_price > 2000000"

    cursor.execute(query)
    cars = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('price_page.html', price_range=price_range, cars=cars)

@app.route('/rental_tracking')
def rental_tracking():
    if 'user_id' not in session:
        flash("Please log in to track your rentals.", "warning")
        return redirect(url_for('login'))

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

if __name__ == '__main__':
    app.run(debug=True)
