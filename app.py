import datetime
import json
import sqlite3

from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app,secret_key = 'sanfrancisco'



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
    
@app.route('/')
def index():
    drink = load_drink_data()
    pizza = load_pizza_data()
    return render_template("index.html", drink=drink, pizza=pizza)
    
@app.route('/base')
def base():
    return render_template("base.html")




        
    

    
    
    








if __name__ == '__main__':
    app.run(debug=True)