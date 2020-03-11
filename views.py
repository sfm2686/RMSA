from __init__ import app, db_engine
from flask import render_template, request, url_for, session, flash, redirect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
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

################################## Helpers #####################################
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

def load_group(group_id):
    return (db_sess.query(Group)
        .filter(Group.id == group_id)
        .first())

################################################################################
################################ Endpoints #####################################
################################################################################
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
        return redirect(url_for('groups'))

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

################################## Groups ######################################
@app.route('/groups')
@require_admin_access
@require_login
def groups():
    return render_template("groups.html", groups=load_all_groups())

@app.route('/group', methods=['GET'])
@require_admin_access
@require_login
def show_group():
    group = load_group(request.args.get('id'))
    if not group:
        flash("Group not found", "alert alert-danger")
        return redirect(url_for('groups'))
    return render_template("group.html", group=group)

@app.route('/group', methods=['POST'])
@require_admin_access
@require_login
def update_group():
    if not request.form['id']:
        flash("Group not found", "alert alert-danger")
        return redirect(url_for('groups'))
    if not request.form['name'] or not is_group_name_valid(request.form['name']):
        flash("Invalid input", "alert alert-danger")
        return redirect(url_for('show_group', id=request.form['id']))
    group = load_group(request.form['id'])
    group.group_name = request.form['name']
    try:
        db_sess.commit()
    except IntegrityError:
        db_sess.rollback()
        flash("Group name is already taken", "alert alert-danger")
        return redirect(url_for('show_group', id=request.form['id']))
    flash("Group updated successfully", "alert alert-success")
    return redirect(url_for('groups'))

@app.route('/add_group', methods=['GET', 'POST'])
@require_admin_access
@require_login
def add_group():
    if request.method == 'POST':
        if (not request.form['name'] or not is_group_name_valid(request.form['name'])):
            flash("Invalid input", "alert alert-danger")
            return render_template("add_group.html")
        new_group = Group(request.form['name'])
        try:
            db_sess.add(new_group)
            db_sess.commit()
        except IntegrityError:
            db_sess.rollback()
            flash("Group name already taken", "alert alert-danger")
            return render_template("add_group.html")
        flash("Group saved successfully", "alert alert-success")
        return redirect(url_for('groups'))
    return render_template("add_group.html") # method == GET

@app.route('/delete_group', methods=['GET'])
@require_admin_access
@require_login
def delete_group():
    group = load_group(request.args.get('id'))
    if not group:
        flash("Group not found", "alert alert-danger")
        return redirect(url_for('groups'))
    db_sess.delete(group)
    db_sess.commit()
    flash("Group deleted successfully", "alert alert-success")
    return redirect(url_for('groups'))

################################### Users ######################################
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

# needs to be tested more
@app.route('/add_user', methods=['GET', 'POST'])
@require_admin_access
@require_login
def add_user():
    data = {}
    data['roles'] = Roles_enum
    groups = []
    for group in load_all_groups():
        user_in_group = False
        groups.append((group.id, group.group_name, user_in_group))
    data['groups'] = groups
    if request.method == 'POST':
        if (not request.form['username'] or not is_username_valid(request.form['username'])
            or not is_password_valid(request.form['password1'])):
            flash("Invalid input", "alert alert-danger")
            return render_template("add_user.html", data=data)
        if request.form["password1"] != request.form['password2']:
            flash("Passwords must match", "alert alert-danger")
            return render_template("add_user.html", data=data)
        new_user = (User(request.form['username']
                    ,bcrypt.hashpw(request.form['password1'].encode("utf-8"), bcrypt.gensalt())
                    ,request.form['role']))
        db_sess.add(new_user)
        try:
            db_sess.commit()
        except IntegrityError:
            db_sess.rollback()
            flash("Username is already taken", "alert alert-danger")
            return render_template("add_user.html", data=data)
        for posted_g_id in request.form.getlist('group'):
            try:
                db_sess.add(User_groups(posted_g_id, new_user.id))  # add user to this group
            except Exception as e:
                print(e)
                flash("Invalid group input", "alert alert-danger")
                return render_template("add_user.html", data=data)
        db_sess.commit() # add new user to groups in db
        flash("User saved successfully", "alert alert-success")
        return redirect(url_for('users'))
    return render_template("add_user.html", data=data)

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
            flash("Invalid group input", "alert alert-danger")
            return redirect(url_for('show_user', id=request.form['id']))
    for group in all_groups_results:
        if not str(group.id) in request.form.getlist('group'): # remove user from this group
            (db_sess.query(User_groups)
                .filter(User_groups.user_id == user_id)
                .filter(User_groups.group_id == group.id)
                .delete())
    result.User.username = request.form['username']
    result.User.role_id = request.form['role']
    try:
        db_sess.commit()
    except IntegrityError:
        db_sess.rollback()
        flash("Username is already taken", "alert alert-danger")
        return redirect(url_for('show_user', id=user_id))
    flash("User updated successfully", "alert alert-success")
    return redirect(url_for('users'))

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
    flash("User deleted successfully", "alert alert-success")
    return redirect(url_for('users'))

############################# Error Handlers ###################################
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")
