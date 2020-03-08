from sqlalchemy.orm import sessionmaker
from tables_def import *
import bcrypt

Session = sessionmaker(bind=db_engine)
sess = Session()

################################################################################
# seed roles data

admins_role = Role("Admin")
sess.add(admins_role)

users_role = Role("User")
sess.add(users_role)

sess.commit()
################################################################################
# seed users data

user = User("sultanmira", bcrypt.hashpw(b"admin", bcrypt.gensalt()))
sess.add(user)
sess.commit()

associated_role = User_role(admins_role.id, user.id)
sess.add(associated_role)


for userinfo in ["elonmusk", "timcook"]:
    user = User(userinfo, bcrypt.hashpw(userinfo.encode("utf-8"), bcrypt.gensalt()))
    sess.add(user)
    sess.commit()

    associated_role = User_role(users_role.id, user.id)
    sess.add(associated_role)

sess.commit()
################################################################################
# seed groups data

################################################################################
