from __init__ import app, db_engine
from flask import render_template, request, url_for, session, flash, redirect
from sqlalchemy.orm import sessionmaker
from tables_def import *
import bcrypt

db_session = sessionmaker(bind=db_engine)
db_sess = db_session()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash("Please enter your username and password")
            return render_template("login.html")
        post_username = request.form['username']
        post_password = request.form['password']
        user = db_sess.query(User).filter_by(username=post_username).first()
        if user and bcrypt.checkpw(post_password.encode("utf-8"), user.password.encode("utf-8")):
            session["loggedin"] = True
            user_role = db_sess.query(User_role).filter_by(user_id=user.id).first()
            session["role"] = user_role.role_id
            print(session["role"])
            return redirect(url_for('reports'))
        else:
            flash("Invalid username or password")
            return render_template("login.html")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/reports')
def reports():
    if not session.get("loggedin"):
        return redirect(url_for('login'))
    return render_template("reports.html")

@app.route('/users')
def users():
    if not session.get("loggedin"):
        return redirect(url_for('login'))
    return render_template("users.html")
