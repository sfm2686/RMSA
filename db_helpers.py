from tables_def import *

def load_user(db_sess, user_id):
    return (db_sess.query(User, Role)
        .filter(User.id == user_id)
        .filter(User.role_id == Role.id)
        .first())

def load_user_groups(db_sess, user_id):
    return (db_sess.query(Group, User_groups)
        .filter(User_groups.user_id == user_id)
        .filter(User_groups.group_id == Group.id)
        .all())

def load_all_groups(db_sess):
    return (db_sess.query(Group).all())

def load_group(db_sess, group_id):
    return (db_sess.query(Group)
        .filter(Group.id == group_id)
        .first())

def load_user_reports(db_sess, uid):
    return (db_sess.query(User_groups, Report)
        .filter(Report.group_id == User_groups.group_id)
        .filter(uid == User_groups.user_id)
        .all())

def load_report_files(db_sess, rid):
    return (db_sess.query(File)
        .filter(File.report_id == rid)
        .all())

def load_report_tags(db_sess, rid):
    return (db_sess.query(Tag, Report_tags)
        .filter(Report_tags.report_id == rid)
        .filter(Report_tags.tag_id == Tag.id)
        .all())

def load_all_tags(db_sess):
    return (db_sess.query(Tag).all())
