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
        drink = {}
        
    return drink

def load_pizza_data():
    try:
        with open('data/pizza.json') as file:
            pizza = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading pizza data: {e}")
        pizza = {}
        
    return pizza
    
def load_sides_data():
    try:
        with open('data/sides.json') as file:
            sides = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading sides data: {e}")
        sides = {}
        
    return sides
    
    
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
    
    

if __name__ == '__main__':
    app.run(debug=True)