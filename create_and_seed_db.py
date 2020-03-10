from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables_def import *
from enums import *
import tables_def
import bcrypt
import random

db_engine = create_engine('mysql+pymysql://root:@localhost')
db_engine.execute("DROP DATABASE IF EXISTS RMSA") #drop db if exists
db_engine.execute("CREATE DATABASE IF NOT EXISTS RMSA") #create db again
db_engine.execute("USE RMSA") # select new db

tables_def.Base.metadata.create_all(db_engine)

Session = sessionmaker(bind=db_engine)
sess = Session()

################################################################################
# seed roles data

admins_role = Role(id=Roles_enum.ADMIN.value, role=Roles_enum.ADMIN.name)
sess.add(admins_role)

users_role = Role(id=Roles_enum.USER.value, role=Roles_enum.USER.name)
sess.add(users_role)

sess.commit()
################################################################################
# seed users data

user = User("sultanmira", bcrypt.hashpw(b"admin", bcrypt.gensalt()), admins_role.id)
sess.add(user)
sess.commit()

users_list = [user]
for userinfo in ["elonmusk", "timcook"]:
    user = User(userinfo, bcrypt.hashpw(userinfo.encode("utf-8"), bcrypt.gensalt()), users_role.id)
    sess.add(user)
    sess.commit()
    users_list.append(user)

sess.commit()
################################################################################
# seed groups data

for g in ["Saudi Arabia", "Germany", "UK", "General"]:
    group = Group(g)
    sess.add(group)
    sess.commit()

    for user in users_list:
        if random.choice([True, False]):
            sess.add(User_groups(group.id, user.id))

sess.commit()
################################################################################
