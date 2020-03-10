from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables_def import *
from enums import *
import tables_def
import bcrypt

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
