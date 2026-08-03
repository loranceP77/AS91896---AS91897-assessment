import datetime
import json
import sqlite3

from flask, import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app,secret_key = 'sanfrancisco'












if __name__ == '__main__':
    app.run(debug=True)