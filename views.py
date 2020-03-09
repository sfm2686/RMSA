from __init__ import app, db_engine
from flask import render_template, request, url_for, session, flash, redirect
from sqlalchemy.orm import sessionmaker
from tables_def import *
from functools import wraps
import bcrypt
from validators import *

db_session = sessionmaker(bind=db_engine)
db_sess = db_session()

ROLES = {'ADMIN': 1, 'USER': 2}

################################ Decorators ####################################
def require_admin_access(endpoint):
    @wraps(endpoint)
    def check_access():
        if session.get("has_admin_access"):
            return endpoint()
        else:
            return redirect(url_for('reports'))
    return check_access

def require_login(endpoint):
    @wraps(endpoint)
    def check_login():
        if session.get("loggedin"):
            return endpoint()
        else:
            return redirect(url_for('login'))
    return check_login

################################# Endpoints ####################################

# @app.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         if not request.form['username'] or not request.form['password']:
#             flash("Please enter your username and password")
#             return render_template("login.html")
#         post_username = request.form['username']
#         post_password = request.form['password']
#         user = db_sess.query(User).filter_by(username=post_username).first()
#         if user and bcrypt.checkpw(post_password.encode("utf-8"), user.password.encode("utf-8")):
#             session["loggedin"] = True
#             user_role = db_sess.query(User_role).filter_by(user_id=user.id).first()
#             session["has_admin_access"] = ROLES['ADMIN'] == user_role.role_id
#             return redirect(url_for('reports'))
#         else:
#             flash("Invalid username or password")
#             return render_template("login.html", ROLES=ROLES)
#
#     return render_template("login.html")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session["loggedin"] = True
        session["has_admin_access"] = True
        return redirect(url_for('users'))

    return render_template("login.html")

@app.route('/logout')
@require_login
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/reports')
@require_login
def reports():
    return render_template("reports.html")

@app.route('/users')
@require_admin_access
@require_login
def users():
    # TODO: include groups once they are added to the DB
    q_results = (db_sess.query(User, User_role, Role)
        .filter(User.id == User_role.user_id)
        .filter(Role.id == User_role.role_id)
        # .filter(User.id == User_groups.user_id)
        # .filter(Group.id == User_groups.group_id)
        .all())
    users = []
    for col in q_results:
        user_dict = {}
        user_dict['user_id'] = col.User.id
        user_dict['username'] = col.User.username
        user_dict['user_role'] = col.Role.role
        users.append(user_dict)
    return render_template("users.html", users=users)

@app.route('/user', methods=['GET', 'POST'])
@require_admin_access
@require_login
def user():
    # TODO: include groups once they are added to the DB
    if request.method == 'GET':
        user_id = request.args.get('id')
        user = db_sess.query(User).filter_by(id=user_id).first()
        if not user:
            flash("User not found", "alert alert-danger")
            return redirect(url_for('users'))
        user_info = {}
        user_info["id"] = user.id
        user_info["username"] = user.username
    elif request.method == 'POST':
        #save user
        if request.form['id'] and request.form['username'] and is_username_valid(request.form['username']):
            user_id = request.form['id']
            user = db_sess.query(User).filter_by(id=user_id).first()
            user.username = request.form['username']
            flash("User updated successfully", "alert alert-success")
            if not user:
                flash("User not found", "alert alert-danger")
                return redirect(url_for('users'))
            user_info = {}
            user_info["id"] = user.id
            user_info["username"] = user.username
    return render_template("user.html", user=user_info)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")
