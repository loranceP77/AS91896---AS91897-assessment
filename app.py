import datetime
import json
import random
import sqlite3
import string
from flask import Flask, flash, redirect, render_template, request, session, url_for

# Initialize the Flask application and set a secret key for session management
app = Flask(__name__)
app.secret_key = 'sanfrancisco'


# --- DATA LOADING HELPERS ---

def load_drink_data():
    """Loads drink menu options from the local JSON file."""
    try:
        with open('data/drink.json') as file:
            drink = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading drink data: {e}")
        drink = []
    return drink


def load_pizza_data():
    """Loads pizza menu options from the local JSON file."""
    try:
        with open('data/pizza.json') as file:
            pizza = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading pizza data: {e}")
        pizza = []
    return pizza


def load_sides_data():
    """Loads sides menu options from the local JSON file."""
    try:
        with open('data/sides.json') as file:
            sides = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading sides data: {e}")
        sides = []
    return sides


# --- DATABASE SETUP ---

def initialise_database():
    """Creates the SQLite database and orders table if they don't already exist."""
    with sqlite3.connect('order.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT,
                customer_name TEXT,
                pizza TEXT,
                drink TEXT,
                sides TEXT,  
                total REAL,
                address TEXT,
                phone TEXT,
                invoice_date TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            '''
        )
        conn.commit()

# --- FLASK ROUTES ---

@app.route('/')
def index():
    """Renders the homepage."""
    return render_template('index.html')


@app.route('/base')
def base():
    """Renders the base layout template."""
    return render_template('base.html')

@app.route('/display_orders')
def display_orders():
    initialise_database()  
    with sqlite3.connect('order.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY date DESC')
        rows = cursor.fetchall()
        orders = []
        for row in rows:
            orders.append({
                'order_id': row['order_id'],
                'invoice_number': row['invoice_number'],
                'customer_name': row['customer_name'],
                'phone': row['phone'],
                'address': row['address'],
                'pizza': json.loads(row['pizza'] or '{}'),
                'drink': json.loads(row['drink'] or '{}'),
                'sides': json.loads(row['sides'] or '{}'),
                'total': row['total'],
                'invoice_date': row['invoice_date']
            })

    return render_template("display_orders.html", orders=orders)

@app.route('/menu')
def menu():
    """Loads all menu items and current cart contents to display on the menu page."""
    drink = load_drink_data()
    pizza = load_pizza_data()
    sides = load_sides_data()
    cart_pizza = session.get('cart_pizza', {})
    cart_drink = session.get('cart_drink', {})
    cart_sides = session.get('cart_sides', {})

    return render_template(
        'menu.html',
        drink=drink,
        pizza=pizza,
        sides=sides,
        cart_drink=cart_drink,
        cart_pizza=cart_pizza,
        cart_sides=cart_sides,
    )


@app.route('/order')
def order():
    """Displays the current shopping cart summary page."""
    cart_pizza = session.get('cart_pizza', {})
    cart_drink = session.get('cart_drink', {})
    cart_sides = session.get('cart_sides', {})

    return render_template(
        'order.html',
        cart_pizza=cart_pizza,
        cart_drink=cart_drink,
        cart_sides=cart_sides,
    )


@app.route('/add_drink', methods=['POST'])
def add_drink():
    """Handles adding drinks to the session cart."""
    drink_info = request.form.get('drink_id')
    quantity = int(request.form.get('quantity', 1))

    cart_drink = session.get('cart_drink', {})

    if drink_info:
        name, size, price = drink_info.split('_', 2)
        item_key = f'{name} ({size})'

        # If item is already in cart, increment quantity; otherwise, add it as a new entry
        if item_key in cart_drink:
            cart_drink[item_key]['quantity'] += quantity
        else:
            cart_drink[item_key] = {
                'name': name,
                'size': size,
                'price': float(price),
                'quantity': quantity,
            }

        session['cart_drink'] = cart_drink
        session.modified = True
        flash(f'{quantity} {item_key}(s) added to order')
    return redirect(url_for('menu'))


@app.route('/add_sides', methods=['POST'])
def add_sides():
    """Handles adding side dishes to the session cart."""
    sides_info = request.form.get('sides_id')
    quantity = int(request.form.get('quantity', 1))

    cart_sides = session.get('cart_sides', {})

    if sides_info:
        name, price = sides_info.split('_', 1)
        item_key = f'{name}'

        if item_key in cart_sides:
            cart_sides[item_key]['quantity'] += quantity
        else:
            cart_sides[item_key] = {
                'name': name,
                'price': float(price),
                'quantity': quantity,
            }

        session['cart_sides'] = cart_sides
        session.modified = True
        flash(f'{quantity} {item_key}(s) added to order')

    return redirect(url_for('menu'))


@app.route('/add_pizza', methods=['POST'])
def add_pizza():
    """Handles adding pizzas to the session cart."""
    pizza_info = request.form.get('pizza_id')
    quantity = int(request.form.get('quantity', 5))

    cart_pizza = session.get('cart_pizza', {})

    if pizza_info:
        parts = pizza_info.split('_', 2)

        if len(parts) != 3:
            flash('Invalid pizza selection.')
            return redirect(url_for('menu'))

        name, size, price = parts
        item_key = f'{name} ({size})'

        if item_key in cart_pizza:
            cart_pizza[item_key]['quantity'] += quantity
        else:
            cart_pizza[item_key] = {
                'name': name,
                'size': size,
                'price': float(price),
                'quantity': quantity,
            }

        session['cart_pizza'] = cart_pizza
        session.modified = True

        flash(f'{quantity} {item_key} added to order')

    return redirect(url_for('menu'))


@app.route('/remove_from_cart/<category>/<item>')
def remove_from_cart(category, item):
    """Removes a specific item completely from the session cart based on category and item name."""
    cart_key = f'cart_{category}'
    cart = session.get(cart_key, {})

    if item in cart:
        del cart[item]
        session[cart_key] = cart
        session.modified = True
        flash('Item removed from cart.')

    return redirect(url_for('order'))

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_saved_order(order_id):
    """Deletes an order from the database based on its order_id."""
    initialise_database()
    with sqlite3.connect('order.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
        conn.commit()

    flash('Order successfully cancelled.')
    return redirect(url_for('display_orders'))

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    """Calculates totals, handles checkout submissions, saves orders to the database, and clears the cart."""
    cart_pizza = session.get('cart_pizza', {})
    cart_drink = session.get('cart_drink', {})
    cart_sides = session.get('cart_sides', {})
    
    # Fixed datetime method and strftime spelling
    invoice_date = datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S')

    # Calculate subtotal across all cart categories
    subtotal = sum(
        item['quantity'] * item['price'] for item in cart_pizza.values()
    )
    subtotal += sum(
        item['quantity'] * item['price'] for item in cart_drink.values()
    )
    subtotal += sum(
        item['quantity'] * item['price'] for item in cart_sides.values()
    )

    if request.method == 'POST':
        order_type = request.form.get('order_type')
        customer_name = request.form.get('customer_name')
        
        # Fixed request.form.get syntax from brackets [] to parentheses ()
        address = request.form.get('address', '').title()
        phone = request.form.get('phone')

        total = subtotal
        if order_type == 'delivery':
            total += 3.00  # Add a $3 delivery fee
   
    # Calculate subtotal across all cart categories
    subtotal = sum(
        item['quantity'] * item['price'] for item in cart_pizza.values()
    )
    subtotal += sum(
        item['quantity'] * item['price'] for item in cart_drink.values()
    )
    subtotal += sum(
        item['quantity'] * item['price'] for item in cart_sides.values()
    )

    if request.method == 'POST':
        order_type = request.form.get('order_type')
        customer_name = request.form.get('customer_name')
        address = request.form.get('address').title()
        phone = request.form.get('phone').title()

        total = subtotal
        if order_type == 'delivery':
            total += 3.00  # Add a $3 delivery fee
    
    
    
    
        # Format cart dictionaries into readable strings for database storage
        pizza_str = ', '.join(
            [f"{item['quantity']}x {key}" for key, item in cart_pizza.items()]
        )
        drink_str = ', '.join(
            [f"{item['quantity']}x {key}" for key, item in cart_drink.items()]
        )
        side_str = ', '.join(
            [f"{item['quantity']}x {key}" for key, item in cart_sides.items()]
        )

        # Generate a random unique invoice number
        invoice_number = 'INV-' + ''.join(
            random.choices(string.digits, k=6)
        )

        # Initialize DB and save completed order details into SQLite
        initialise_database()
        with sqlite3.connect('order.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO orders (invoice_number, customer_name, pizza, drink, sides, total, address, phone, invoice_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
                (
                    invoice_number,
                    customer_name,
                    json.dumps(cart_pizza),
                    json.dumps(cart_drink),
                    json.dumps(cart_sides),
                    total,
                    address,
                    phone,
                    invoice_date,
                ),
            )
            conn.commit() 
        # Clear out the user's shopping cart session after a successful order
        session.pop('cart_pizza', None)
        session.pop('cart_drink', None)
        session.pop('cart_sides', None)
        session.modified = True

        flash('Order successful!')
        return redirect(url_for('menu'))

    return render_template(
        'buy.html',
        cart_pizza=cart_pizza,
        cart_drink=cart_drink,
        cart_sides=cart_sides,
        subtotal=subtotal,
    )


if __name__ == '__main__':
    app.run(debug=True)