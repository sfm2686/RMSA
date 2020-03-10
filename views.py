from __init__ import app, db_engine
from flask import render_template, request, url_for, session, flash, redirect
from sqlalchemy.orm import sessionmaker
from tables_def import *
from functools import wraps
from validators import *
from enums import *
import bcrypt

db_session = sessionmaker(bind=db_engine)
db_sess = db_session()

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

################################# Helpers ####################################
def load_user(user_id):
    return (db_sess.query(User, Role, User_role)
        .filter(User.id == user_id)
        .filter(User.id == User_role.user_id)
        .filter(Role.id == User_role.role_id)
        .first())

################################ Endpoints ####################################
# TODO add csrf token
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash("Please enter your username and password", "alert alert-danger")
            return render_template("login.html")
        post_username = request.form['username']
        post_password = request.form['password']
        user = db_sess.query(User).filter_by(username=post_username).first()
        if user and bcrypt.checkpw(post_password.encode("utf-8"), user.password.encode("utf-8")):
            session["loggedin"] = True
            user_role = db_sess.query(User_role).filter_by(user_id=user.id).first()
            session["has_admin_access"] = Roles_enum.ADMIN.value == user_role.role_id
            return redirect(url_for('reports'))
        else:
            flash("Invalid username or password", "alert alert-danger")
            return render_template("login.html")

    return render_template("login.html")

# @app.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session["loggedin"] = True
#         session["has_admin_access"] = True
#         return redirect(url_for('users'))
#
#     return render_template("login.html")

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
    results = (db_sess.query(User, User_role, Role)
        .filter(User.id == User_role.user_id)
        .filter(Role.id == User_role.role_id)
        # .filter(User.id == User_groups.user_id)
        # .filter(Group.id == User_groups.group_id)
        .all())
    users = []
    for col in results:
        user_dict = {}
        user_dict['user_id'] = col.User.id
        user_dict['username'] = col.User.username
        user_dict['user_role'] = col.Role.role
        users.append(user_dict)
    return render_template("users.html", users=users)

@app.route('/user', methods=['GET'])
@require_admin_access
@require_login
def show_user():
    # TODO: include groups once they are added to the DB
    user_id = request.args.get('id')
    result = load_user(user_id)
    if not result:
        flash("User not found", "alert alert-danger")
        return redirect(url_for('users'))
    return render_template("user.html", data=result, roles=Roles_enum)

@app.route('/user', methods=['POST'])
@require_admin_access
@require_login
def update_user():
    if not request.form['id']:
        flash("User not found", "alert alert-danger")
        return redirect(url_for('users'))
    if not request.form['username'] or not is_username_valid(request.form['username']):
        flash("Invalid input", "alert alert-danger")
        return redirect(url_for('show_user', id=request.form['id']))
    user_id = request.form['id']
    result = load_user(user_id)
    if not result:
        flash("User not found", "alert alert-danger")
        return redirect(url_for('users'))
    flash("User updated successfully", "alert alert-success")
    result.User.username = request.form['username']
    result.User_role.role_id = request.form['role']
    db_sess.commit()
    # return render_template("user.html", data=result, roles=Roles_enum)
    return redirect(url_for('show_user', id=user_id))

@app.route('/delete_user', methods=['GET'])
@require_admin_access
@require_login
def delete_user():
    print("gonna delete {}".format(request.args.get('id')))
    result = load_user(request.args.get('id'))
    if not result:
        flash("User not found", "alert alert-danger")
        return redirect(url_for('users'))
    db_sess.delete(result.User)
    db_sess.commit()
    return redirect(url_for('users'))

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")
