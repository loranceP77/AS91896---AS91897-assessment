import datetime
import json
import sqlite3

from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'sanfrancisco'



def load_drink_data():
    try:
        with open('data/drink.json') as file:
            drink = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading drink data: {e}")
        drink = []
        
    return drink

def load_pizza_data():
    try:
        with open('data/pizza.json') as file:
            pizza = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading pizza data: {e}")
        pizza = []
        
    return pizza
    
def load_sides_data():
    try:
        with open('data/sides.json') as file:
            sides = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading sides data: {e}")
        sides = []
        
    return sides
    
def initialise_database():
    with sqlite3.connect('order.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            customer_name,
            pizza TEXT,
            drink TEXT,
            side TEXT,
            total REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
                       ''')
        conn.commit()
    
    
@app.route("/")
def index():
    return render_template("index.html")
    
@app.route('/base')
def base():
    return render_template("base.html")

@app.route('/menu')
def menu():
    drink = load_drink_data()
    pizza = load_pizza_data()
    sides = load_sides_data()
    cart_pizza = session.get('cart_pizza', {})
    cart_drink = session.get('cart_drink', {})
    cart_sides = session.get('cart_sides', {})
    
    
    return render_template("menu.html",
                           drink = drink,
                           pizza = pizza,
                           sides = sides,
                           cart_drink = cart_drink,
                           cart_pizza = cart_pizza,
                           cart_sides = cart_sides
                           )


@app.route('/order')
def order():
    return render_template("order.html")        



@app.route('/add_drink', methods=["POST"])
def add_drink():
    drink_info = request.form.get('drink_id')
    quantity = int(request.form.get('quantity', 1))
    
    cart_drink = session.get('cart_drink', {})
    
    if drink_info:
        name, size, price = drink_info.split('_', 2)
        item_key = f"{name} ({size})"
        
        if item_key in cart_drink:
            cart_drink[item_key]['quantity'] += quantity
        else: 
            cart_drink[item_key] = {
                'name': name,
                'size': size,
                'price': float(price),
                'quantity': quantity
                }
            
        session['cart_drink'] = cart_drink
        session.modified = True
        flash(f"{quantity} {item_key}(s) added to order")
    return redirect(url_for('menu'))         
            
            
@app.route('/add_sides', methods=["POST"])  
def add_sides():
    sides_info = request.form.get('sides_id')
    quantity = int(request.form.get('quantity', 1))
    
    cart_sides = session.get('cart_sides', {})
    
    if sides_info:
        name, price = sides_info.split('_', 1)
        item_key = f"{name}"
        
        if item_key in cart_sides:
            cart_sides[item_key]['quantity'] += quantity
        else: 
            cart_sides[item_key] = {
                'name': name,
                'price': float(price),
                'quantity': quantity
                }
            
        session['cart_sides'] = cart_sides
        session.modified = True
        flash(f"{quantity} {item_key}(s) added to order")
        
        
    return redirect(url_for('menu'))  
    



@app.route('/add_pizza', methods=["POST"])
def add_pizza():
    pizza_info = request.form.get('pizza_id')
    quantity = int(request.form.get('quantity', 1))

    cart_pizza = session.get('cart_pizza', {})

    if pizza_info:
        parts = pizza_info.split('_', 2)

        if len(parts) != 3:
            flash("Invalid pizza selection.")
            return redirect(url_for('menu'))

        name, size, price = parts
        item_key = f"{name} ({size})"

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

        flash(f"{quantity} {item_key} added to order")

    return redirect(url_for('menu'))


if __name__ == '__main__':
    app.run(debug=True)
