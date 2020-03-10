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
    return (db_sess.query(User, Role)
        .filter(User.id == user_id)
        .filter(User.role_id == Role.id)
        .first())

def load_user_groups(user_id):
    return (db_sess.query(Group, User_groups)
        .filter(User_groups.user_id == user_id)
        .filter(User_groups.group_id == Group.id)
        .all())

def load_all_groups():
    return (db_sess.query(Group)
        .all())

################################ Endpoints ####################################
# TODO add csrf token
# @app.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         if not request.form['username'] or not request.form['password']:
#             flash("Please enter your username and password", "alert alert-danger")
#             return render_template("login.html")
#         post_username = request.form['username']
#         post_password = request.form['password']
#         user = db_sess.query(User).filter_by(username=post_username).first()
#         if user and bcrypt.checkpw(post_password.encode("utf-8"), user.password.encode("utf-8")):
#             session["loggedin"] = True
#             session["has_admin_access"] = Roles_enum.ADMIN.value == user.role_id
#             return redirect(url_for('reports'))
#         else:
#             flash("Invalid username or password", "alert alert-danger")
#             return render_template("login.html")
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
    results = (db_sess.query(User, Role)
        .filter(User.role_id == Role.id)
        .all())

    users = []
    for col in results:
        user_dict = {}
        user_dict['user_id'] = col.User.id
        user_dict['username'] = col.User.username
        user_dict['user_role'] = col.Role.role
        user_dict['group_count'] = len(load_user_groups(col.User.id))
        users.append(user_dict)
    return render_template("users.html", users=users)

@app.route('/user', methods=['GET'])
@require_admin_access
@require_login
def show_user():
    user_id = request.args.get('id')
    user = load_user(user_id)
    if not user:
        flash("User not found", "alert alert-danger")
        return redirect(url_for('users'))
    user_groups = load_user_groups(user_id)
    group_results = load_all_groups()
    if not group_results:
        flash("No groups found", "alert alert-warning")
    data = {}
    data['user'] = user
    data['roles'] = Roles_enum
    groups = []
    # flag the groups that the user belongs to
    for group in group_results:
        user_in_group = False
        for user_group in user_groups:
            if group.id == user_group.Group.id:
                user_in_group = True
                break
        groups.append((group.id, group.group_name, user_in_group))
    data['groups'] = groups
    return render_template("user.html", data=data)

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
    user_groups = load_user_groups(user_id)
    user_groups_list = []
    for group in user_groups: # create a list of group ids that the user belongs to
        user_groups_list.append(group.Group.id)
    all_groups_results = load_all_groups()

    for posted_g_id in request.form.getlist('group'):
        try:
            if not int(posted_g_id) in user_groups_list: # add user to this group
                db_sess.add(User_groups(posted_g_id, user_id))
        except:
            flash("Invalid input", "alert alert-danger")
            return redirect(url_for('show_user', id=request.form['id']))
    for group in all_groups_results:
        if not str(group.id) in request.form.getlist('group'): # remove user from this group
            (db_sess.query(User_groups)
                .filter(User_groups.user_id == user_id)
                .filter(User_groups.group_id == group.id)
                .delete())

    result.User.username = request.form['username']
    result.User.role_id = request.form['role']
    db_sess.commit()
    flash("User updated successfully", "alert alert-success")
    return redirect(url_for('show_user', id=user_id))

@app.route('/delete_user', methods=['GET'])
@require_admin_access
@require_login
def delete_user():
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
