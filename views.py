from flask import render_template
from __init__ import app

@app.route('/')
def login():
    return render_template("login.html")
