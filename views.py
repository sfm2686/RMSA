from __init__ import app, db_engine
from flask import render_template, request, url_for, session, flash, redirect, send_file
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from functools import wraps
from tables_def import *
from validators import *
from enums import *
from db_helpers import *
import bcrypt
import os
import time

UPLOAD_FILES_BASE_DIR = 'media-storage'
REPORT_PAGE_SIZE      = 20

db_session = sessionmaker(bind=db_engine)
db_sess = db_session()

################################## Helpers #####################################
def flash_and_redirect(msg, cat, dest):
    flash(msg, cat)
    return redirect(url_for(dest))

def delete_file_helper(file):
    os.remove(file.file_path)
    db_sess.delete(file)
    db_sess.commit()

################################ Decorators ####################################
def require_admin_access(endpoint):
    @wraps(endpoint)
    def check_access():
        if session.get("has_admin_access"):
            return endpoint()
        else:
            return redirect(url_for('index'))
    return check_access

def require_login(endpoint):
    @wraps(endpoint)
    def check_login():
        if session.get("loggedin"):
            return endpoint()
        else:
            return redirect(url_for('login'))
    return check_login

################################################################################
################################ Endpoints #####################################
################################################################################
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            return flash_and_redirect("Please enter your username and password", "alert alert-danger", "login")
        post_username = request.form['username']
        post_password = request.form['password']
        user = db_sess.query(User).filter_by(username=post_username).first()
        if user and bcrypt.checkpw(post_password.encode("utf-8"), user.password.encode("utf-8")):
            session["loggedin"] = True
            session["has_admin_access"] = Roles_enum.ADMIN.value == user.role_id
            session["uid"] = user.id
            return redirect(url_for('index'))
        else:
            return flash_and_redirect("Invalid username or password", "alert alert-danger", "login")
    return render_template("login.html")

# dev login
# @app.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session["loggedin"] = True
#         session["has_admin_access"] = True
#         session["uid"] = 1
#         return redirect(url_for('reports'))
#     return render_template("login.html")

@app.route('/logout')
@require_login
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/index')
@require_login
def index():
    user = load_user(db_sess, session.get("uid")).User
    data = {'username': user.username}
    user_role = "Admin" if user.role_id == Roles_enum.ADMIN.value else "User"
    data['role'] = user_role
    data['groups'] = [col.Group.group_name for col in load_user_groups(db_sess, session.get("uid"))]
    return render_template("index.html", data=data)

@app.route('/search', methods=['POST', 'GET'])
@require_login
def search():
    if request.method == 'POST':
        q = request.form['search']
        search_results = load_search_results(db_sess, session.get("uid"), q)
        reports = []
        ids_set = set()
        for col in search_results:
            if col.Report.id in ids_set:
                continue
            ids_set.add(col.Report.id)
            report_dict = {}
            report_dict['id'] = col.Report.id
            report_dict['name'] = col.Report.name
            col_limit = 10
            if len(col.Report.desc) >= col_limit:
                report_dict['desc'] = "{}...".format(col.Report.desc[:col_limit])
            else:
                report_dict['desc'] = col.Report.desc
            user = load_user(db_sess, col.Report.creator_id)
            if user:
                report_dict['creatid'] = user.User.username
            else:
                report_dict['creatid'] = "Deleted"
            report_dict['group'] = col.Group.group_name
            report_dict['nfiles'] = len(load_report_files(db_sess, col.Report.id))
            rtags = ""
            for t in load_report_tags(db_sess, col.Report.id):
                rtags = rtags + t.Tag.tag + " "
            if len(rtags) >= col_limit:
                report_dict['tags'] = "{}...".format(rtags[:col_limit])
            else:
                report_dict['tags'] = rtags
            reports.append(report_dict)
        return render_template("search.html", submitted=True, reports=reports)
    return render_template("search.html", submitted=False)

################################### FILES ######################################

@app.route('/download-file')
@require_login
def download_file():
    try: # missing or wrong data type input
        rid = int(request.args.get("report_id"))
        fid = int(request.args.get("file_id"))
    except (ValueError, TypeError):
        return flash_and_redirect("Invalid input", "alert alert-danger", "reports")
    # ensure user has permission to access report content
    report = load_user_report(db_sess, session.get("uid"), rid)
    if not report:
        return flash_and_redirect("Invalid input", "alert alert-danger", "reports")
    # ensure file belongs to correct report
    report_file_ids = [f.id for f in load_report_files(db_sess, rid)]
    if fid not in report_file_ids:
        return flash_and_redirect("Invalid input", "alert alert-danger", "reports")
    file = db_sess.query(File).filter(File.id == fid).first()
    if not file:
        flash("File not found", "alert alert-danger")
        return redirect(url_for("show_report", id=rid))
    try: # if phyiscal file was missing
        return send_file(file.file_path, as_attachment=True)
    except FileNotFoundError:
        flash("File not found", "alert alert-danger")
        return redirect(url_for("show_report", id=rid))

@app.route('/delete-file')
@require_login
def delete_file():
    try: # missing or wrong data type input
        rid = int(request.args.get("report_id"))
        fid = int(request.args.get("file_id"))
    except (ValueError, TypeError):
        return flash_and_redirect("Invalid input", "alert alert-danger", "reports")
    # ensure user has permission to access report content
    report = load_user_report(db_sess, session.get("uid"), rid)
    if not report:
        return flash_and_redirect("Invalid input", "alert alert-danger", "reports")
    # ensure file belongs to correct report
    report_file_ids = [f.id for f in load_report_files(db_sess, rid)]
    if fid not in report_file_ids:
        return flash_and_redirect("Invalid input", "alert alert-danger", "reports")
    file = db_sess.query(File).filter(File.id == fid).first()
    if not file:
        flash("File not found", "alert alert-danger")
        return redirect(url_for("show_report", id=rid))
    try: # if phyiscal file was missing
        delete_file_helper(file)
        flash("File deleted successfully", "alert alert-success")
        return redirect(url_for("show_report", id=rid))
    except FileNotFoundError:
        flash("File not found", "alert alert-danger")
        return redirect(url_for("show_report", id=rid))

################################## Reports #####################################
@app.route('/reports')
@require_login
def reports():
    page = request.args.get('page')
    if page:
        try:
            page = int(page)
            reports = load_user_reports(db_sess, session.get("uid"), REPORT_PAGE_SIZE, page)
        except ValueError:
            return flash_and_redirect("Invalid page input", "alert alert-danger", "reports")
    else:
        reports = load_user_reports(db_sess, session.get("uid"), REPORT_PAGE_SIZE)
        page = 0
    page = abs(page) # ensure number is positive
    data = []
    for col in reports:
        report_dict = {}
        report_dict['id'] = col.Report.id
        report_dict['name'] = col.Report.name
        col_limit = 10
        if len(col.Report.desc) >= col_limit:
            report_dict['desc'] = "{}...".format(col.Report.desc[:col_limit])
        else:
            report_dict['desc'] = col.Report.desc
        user = load_user(db_sess, col.Report.creator_id)
        if user:
            report_dict['creatid'] = user.User.username
        else:
            report_dict['creatid'] = "Deleted"
        report_dict['group'] = load_group(db_sess, col.Report.group_id).group_name
        report_dict['nfiles'] = len(load_report_files(db_sess, col.Report.id))
        rtags = ""
        for t in load_report_tags(db_sess, col.Report.id):
            rtags = rtags + t.Tag.tag + " "
        if len(rtags) >= col_limit:
            report_dict['tags'] = "{}...".format(rtags[:col_limit])
        else:
            report_dict['tags'] = rtags
        data.append(report_dict)
    prev_url = url_for('reports', page=page-1) if page > 0 else None
    next_reports = load_user_reports(db_sess, session.get("uid"), REPORT_PAGE_SIZE, page + 1)
    next_url = url_for('reports', page=page+1) if next_reports else None
    return render_template("reports.html", reports=data, prev=prev_url, next=next_url)

@app.route('/report', methods=['GET'])
@require_login
def show_report():
    try:
        rid = int(request.args.get('id'))
    except ValueError:
        return flash_and_redirect("Report not found", "alert alert-danger", "reports")
    # search through user specific reports to ensure proper permission
    report = load_user_report(db_sess, session.get("uid"), rid)
    if not report:
        return flash_and_redirect("Report not found", "alert alert-danger", "reports")
    report = report.Report
    report_dict = {}
    report_dict['id'] = report.id
    report_dict['name'] = report.name
    report_dict['desc'] = report.desc
    user = load_user(db_sess, report.creator_id)
    if user:
        report_dict['creatid'] = user.User.username
    else:
        report_dict['creatid'] = "Deleted"
    report_dict['group_id'] = report.group_id
    report_dict['group'] = load_group(db_sess, report.group_id).group_name
    report_dict['files'] = [(file.id, os.path.basename(file.file_path)) for file in load_report_files(db_sess, report.id)]
    report_dict['tags'] = []
    for t in load_report_tags(db_sess, report.id):
        report_dict['tags'].append(t.Tag)
    groups = [r.Group for r in load_user_groups(db_sess, session.get("uid"))]
    # flag the tags that the report belongs to
    tags = []
    for tag in load_all_tags(db_sess):
        belongs_to = False
        for rtag in load_report_tags(db_sess, report.id):
            if tag.id == rtag.Tag.id:
                belongs_to = True
                break
        tags.append((tag.id, tag.tag, belongs_to))
    return render_template("report.html", report=report_dict, groups=groups, tags=tags)

@app.route('/report', methods=['POST'])
@require_login
def update_report():
    if not request.form['id']:
        return flash_and_redirect("Report not found", "alert alert-danger", "reports")
    # search through user specific reports to ensure proper permission
    try:
        rid = int(request.args.get('id', type=int))
    except ValueError:
        return flash_and_redirect("Report not found", "alert alert-danger", "reports")
    report = load_user_report(db_sess, session.get("uid"), rid)
    if not report:
        return flash_and_redirect("Report not found", "alert alert-danger", "reports")
    report = report.Report
    allowed_groups = [str(col.Group.id) for col in load_user_groups(db_sess, session.get("uid"))]
    if request.form['group'] not in allowed_groups:
        flash("Invalid group input", "alert alert-danger")
        return redirect(url_for("show_report", id=request.form["id"]))
    if not is_report_name_valid(request.form['name']) or not is_report_desc_valid(request.form['desc']):
        flash("Invalid name/description input", "alert alert-danger")
        return redirect(url_for("show_report", id=request.form["id"]))
    report.name = request.form['name']
    report.desc = request.form['desc']
    report.group_id = request.form['group']
    db_sess.commit() # save updated report
    # handling files
    files = request.files.to_dict(flat=False)['file']
    for file in files:
        if not file:
            continue
        if not is_filename_valid(file.filename):
            flash("Invalid file name or extension", "alert alert-danger")
            return redirect(url_for("show_report", id=request.form["id"]))
        else:
            filename = secure_filename(file.filename)
            mt = filename.split(".").pop() # media type
            upload_path = os.path.join(UPLOAD_FILES_BASE_DIR, mt)
            # inserting timestamp before file's extension
            filename = "{}-{}{}".format(filename[:len(filename) - 4], time.time(), filename[len(filename) - 4:])
            full_file_path = os.path.join(upload_path, filename)
            if is_file_path_valid(full_file_path):
                file.save(full_file_path)
                db_sess.add(File(full_file_path, report.id))
            else:
                flash("File name/s too long", "alert alert-danger")
                return redirect(url_for("show_report", id=request.form['id']))
    # handling tags
    report_tag_ids = [col.Tag.id for col in load_report_tags(db_sess, request.form['id'])]
    all_tag_ids = [t.id for t in load_all_tags(db_sess)]
    for posted_tag in request.form.getlist("tags"): # check tags to be added
        try:
            posted_tag = int(posted_tag)
            if posted_tag in all_tag_ids and not posted_tag in report_tag_ids:
                    db_sess.add(Report_tags(report.id, posted_tag))
        except ValueError:
            flash("Invalid tag input", "alert alert-danger")
            return redirect(url_for('show_report', id=request.form['id']))
    for tag_id in all_tag_ids: # check tags to be removed
        if not str(tag_id) in request.form.getlist("tags") and tag_id in report_tag_ids:
            report_tag = (db_sess.query(Report_tags)
                        .filter(Report_tags.report_id == request.form['id'])
                        .filter(Report_tags.tag_id == tag_id)
                        .first())
            db_sess.delete(report_tag)
    db_sess.commit()
    return flash_and_redirect("Report updated successfully", "alert alert-success", "reports")

@app.route('/add_report', methods=['GET', 'POST'])
@require_login
def add_report():
    page_tags = []
    all_tags = load_all_tags(db_sess)
    for tag in all_tags:
        belongs_to = False
        page_tags.append((tag.id, tag.tag, belongs_to))
    allowed_groups = [r.Group for r in load_user_groups(db_sess, session.get("uid"))]
    if request.method == 'POST':
        if not is_report_name_valid(request.form['name']) or not is_report_desc_valid(request.form['desc']):
            return flash_and_redirect("Invalid name/desc input", "alert alert-danger", "add_report")
        try:
            posted_g = int(request.form['group'])
        except ValueError: # incase the group value couldnt be casted into an int
            return flash_and_redirect("Invalid group input", "alert alert-danger", "add_report")
        if not posted_g or not posted_g in [g.id for g in allowed_groups]:
            return flash_and_redirect("Invalid group input", "alert alert-danger", "add_report")
        all_tag_ids = [str(t.id) for t in all_tags]
        for tag in request.form.getlist("tags"):
            if tag not in all_tag_ids:
                return flash_and_redirect("Invalid tags input", "alert alert-danger", "add_report")
        report = Report(request.form['name'], request.form['desc'], session.get("uid"), request.form['group'])
        db_sess.add(report)
        db_sess.commit()
        # handling tags
        for tag in request.form.getlist('tags'):
            db_sess.add(Report_tags(report.id, tag))
        db_sess.commit()
        # handling files
        files = request.files.to_dict(flat=False)['file']
        for file in files:
            if not file:
                continue
            if not is_filename_valid(file.filename):
                return flash_and_redirect("Invalid file name or extension", "alert alert-danger", "add_report")
            filename = secure_filename(file.filename)
            mt = filename.split(".").pop() # media type
            upload_path = os.path.join(UPLOAD_FILES_BASE_DIR, mt)
            # inserting timestamp before file's extension
            filename = "{}-{}{}".format(filename[:len(filename) - 4], time.time(), filename[len(filename) - 4:])
            full_file_path = os.path.join(upload_path, filename)
            if not is_file_path_valid(full_file_path):
                return flash_and_redirect("File name/s too long", "alert alert-danger", "add_report")
            file.save(full_file_path)
            db_sess.add(File(full_file_path, report.id))
        return flash_and_redirect("Report added successfully", "alert alert-success", "reports")
    return render_template("add_report.html", groups=allowed_groups, tags=page_tags)

@app.route('/delete_report', methods=['GET'])
@require_login
def delete_report():
    try:
        rid = int(request.args.get('id'))
    except ValueError:
        return flash_and_redirect("Report not found", "alert alert-danger", "reports")
    report = load_user_report(db_sess, session.get("uid"), rid)
    if not report:
        return flash_and_redirect("Report not found", "alert alert-danger", "reports")
    report = report.Report
    report_files = load_report_files(db_sess, report.id)
    for file in report_files:
        delete_file_helper(file)
    db_sess.delete(report)
    db_sess.commit()
    return flash_and_redirect("Report deleted successfully", "alert alert-success", "reports")

################################## Groups ######################################
@app.route('/groups')
@require_admin_access
@require_login
def groups():
    group_records = load_all_groups(db_sess)
    groups = []
    for group in group_records:
        group_dict = {}
        group_dict['id'] = group.id
        group_dict['name'] = group.group_name
        group_dict['user_count'] = db_sess.query(User_groups).filter(User_groups.group_id == group.id).count()
        group_dict['report_count'] = db_sess.query(Report).filter(Report.group_id == group.id).count()
        groups.append(group_dict)
    return render_template("groups.html", groups=groups)

@app.route('/group', methods=['GET'])
@require_admin_access
@require_login
def show_group():
    group = load_group(db_sess, request.args.get('id'))
    if not group:
        return flash_and_redirect("Group not found", "alert alert-danger", "groups")
    return render_template("group.html", group=group)

@app.route('/group', methods=['POST'])
@require_admin_access
@require_login
def update_group():
    if not request.form['id']:
        return flash_and_redirect("Group not found", "alert alert-danger", "groups")
    if not is_group_name_valid(request.form['name']):
        flash("Invalid input", "alert alert-danger")
        return redirect(url_for('show_group', id=request.form['id']))
    group = load_group(db_sess, request.form['id'])
    group.group_name = request.form['name']
    try:
        db_sess.commit()
    except IntegrityError:
        db_sess.rollback()
        flash("Group name is already taken", "alert alert-danger")
        return redirect(url_for('show_group', id=request.form['id']))
    return flash_and_redirect("Group updated successfully", "alert alert-success", "groups")

@app.route('/add_group', methods=['GET', 'POST'])
@require_admin_access
@require_login
def add_group():
    if request.method == 'POST':
        if (not request.form['name'] or not is_group_name_valid(request.form['name'])):
            return flash_and_redirect("Invalid input", "alert alert-danger", "add_group")
        new_group = Group(request.form['name'])
        try:
            db_sess.add(new_group)
            db_sess.commit()
        except IntegrityError:
            db_sess.rollback()
            return flash_and_redirect("Group name already taken", "alert alert-danger", "add_group")
        return flash_and_redirect("Group saved successfully", "alert alert-success", "groups")
    return render_template("add_group.html") # method == GET

@app.route('/delete_group', methods=['GET'])
@require_admin_access
@require_login
def delete_group():
    group = load_group(db_sess, request.args.get('id'))
    if not group:
        return flash_and_redirect("Group not found", "alert alert-danger", "groups")
    try:
        db_sess.delete(group)
        db_sess.commit()
    except IntegrityError:
        db_sess.rollback()
        flash("Please ensure no users belong to the group before attempting to delete it", "alert alert-danger")
        return redirect(url_for('show_group', id=request.args.get('id')))
    return flash_and_redirect("Group deleted successfully", "alert alert-success", "groups")

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
        user_dict['group_count'] = len(load_user_groups(db_sess, col.User.id))
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
    for group in load_all_groups(db_sess):
        user_in_group = False
        groups.append((group.id, group.group_name, user_in_group))
    data['groups'] = groups
    if request.method == 'POST':
        if (not is_username_valid(request.form['username']) or not is_password_valid(request.form['password1'])):
            flash("Invalid input", "alert alert-danger")
            return render_template("add_user.html", data=data)
        if request.form["password1"] != request.form['password2']:
            flash("Passwords must match", "alert alert-danger")
            return render_template("add_user.html", data=data)
        if len(request.form.getlist('group')) == 0:
            flash("User must be added to at least one group", "alert alert-danger")
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
            except ValueError:
                flash("Invalid group input", "alert alert-danger")
                return render_template("add_user.html", data=data)
        db_sess.commit() # add new user to groups in db
        return flash_and_redirect("User saved successfully", "alert alert-success", "users")
    return render_template("add_user.html", data=data)

@app.route('/user', methods=['GET'])
@require_admin_access
@require_login
def show_user():
    user_id = request.args.get('id')
    user = load_user(db_sess, user_id)
    if not user:
        return flash_and_redirect("User not found", "alert alert-danger", "users")
    user_groups = load_user_groups(db_sess, user_id)
    group_results = load_all_groups(db_sess)
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
        return flash_and_redirect("User not found", "alert alert-danger", "users")
    if  not is_username_valid(request.form['username']):
        flash("Invalid input", "alert alert-danger")
        return redirect(url_for('show_user', id=request.form['id']))
    user_id = request.form['id']
    result = load_user(db_sess, user_id)
    if not result:
        return flash_and_redirect("User not found", "alert alert-danger", "users")
    # create a list of group ids that the user belongs to
    user_groups_list = [col.Group.id for col in load_user_groups(db_sess, user_id)]

    for posted_g_id in request.form.getlist('group'): # check groups to be added
        try:
            if not int(posted_g_id) in user_groups_list: # add user to this group
                db_sess.add(User_groups(posted_g_id, user_id))
        except ValueError:
            flash("Invalid group input", "alert alert-danger")
            return redirect(url_for('show_user', id=request.form['id']))
    user_groups = load_user_groups(db_sess, user_id) # get updated user groups
    for group in load_all_groups(db_sess): # check groups to be removed
        if not str(group.id) in request.form.getlist('group'):
            group_to_delete = (db_sess.query(User_groups)
                .filter(User_groups.user_id == user_id)
                .filter(User_groups.group_id == group.id)
                .first())
            if not group_to_delete:
                continue
            if len(user_groups) <= 1:
                flash("User must belong to at least one group", "alert alert-danger")
                return redirect(url_for('show_user', id=user_id))
            elif len(user_groups) > 1:  # remove user from this group
                db_sess.delete(group_to_delete)
                user_groups = load_user_groups(db_sess, user_id) # get updated user groups
    result.User.username = request.form['username']
    result.User.role_id = request.form['role']
    try:
        db_sess.commit()
    except IntegrityError:
        db_sess.rollback()
        flash("Username is already taken", "alert alert-danger")
        return redirect(url_for('show_user', id=user_id))
    return flash_and_redirect("User updated successfully", "alert alert-success", "users")

@app.route('/delete_user', methods=['GET'])
@require_admin_access
@require_login
def delete_user():
    result = load_user(db_sess, request.args.get('id'))
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

@app.errorhandler(500)
def not_found(e):
    return render_template("500.html")
