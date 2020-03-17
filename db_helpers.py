from tables_def import *
from sqlalchemy import or_

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

def load_user_reports(db_sess, uid, page_size, page=0):
    q = (db_sess.query(User_groups, Report)
        .filter(Report.group_id == User_groups.group_id)
        .filter(uid == User_groups.user_id))
    q = q.limit(page_size)
    q = q.offset(page * page_size)
    return q.all()

def load_user_report(db_sess, uid, rid):
    return (db_sess.query(User_groups, Report)
            .filter(Report.group_id == User_groups.group_id)
            .filter(uid == User_groups.user_id)
            .filter(rid == Report.id)
            .first())

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

def load_search_results(db_sess, uid, q, page_size, page=0):
    search_query = (db_sess.query(Report, User, User_groups, Group, Tag, Report_tags)
                        .filter(Group.id == Report.group_id)
                        .filter(Report_tags.tag_id == Tag.id)
                        .filter(Report_tags.report_id == Report.id)
                        .filter(User.id == Report.creator_id)
                        .filter(User_groups.user_id == uid)
                        .filter(User_groups.group_id == Group.id)
                        .filter(or_(Report.name.like("%{}%".format(q)),
                                    Report.desc.like("%{}%".format(q)),
                                    Tag.tag.like("%{}%".format(q)),
                                    Group.group_name.like("%{}%".format(q)),
                                    User.username.like("%{}%".format(q)))))
    search_query = search_query.limit(page_size)
    search_query = search_query.offset(page * page_size)
    return search_query.all()
