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
    with sqlite3.connect(order.db) as conn:
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
    return render_template("menu.html")


@app.route('/order')
def order():
    return render_template("order.html")        
    
    
    
@app.route('/checkout')

@app.route('/add_drink', methods=["POST"])
def add_drink():
    
@app.route('/add_sides', methods=["POST"])   
    
@
app.route('/add_pizza', methods=["POST"])
    

if __name__ == '__main__':
    app.run(debug=True)