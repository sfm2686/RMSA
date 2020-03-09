from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, create_engine

db_engine = create_engine('mysql+pymysql://root:@localhost')
db_engine.execute("DROP DATABASE IF EXISTS RMSA") #drop db if exists
db_engine.execute("CREATE DATABASE IF NOT EXISTS RMSA") #create db again
db_engine.execute("USE RMSA") # select new db

Base = declarative_base()

################################################################################
class User(Base):
    """"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20))
    password = Column(String(60))

    __table_args__ = (
        UniqueConstraint('username'),
        )

    #---------------------------------------------------------------------------
    def __init__(self, username, password):
        """"""
        self.username = username
        self.password = password

    def __repr__(self):
        return (self.username)

################################################################################
class Role(Base):
    """"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(10))

    #---------------------------------------------------------------------------
    def __init__(self, role):
        """"""
        self.role = role

################################################################################
class User_role(Base):
    """"""
    __tablename__ = "user_roles"

    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    __table_args__ = (
        UniqueConstraint('user_id'),
        )

    #---------------------------------------------------------------------------
    def __init__(self, role_id, user_id):
        """"""
        self.role_id = role_id
        self.user_id = user_id

################################################################################
class Group(Base):
    """"""
    __tablename__ = "groups_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String(20))

    #---------------------------------------------------------------------------
    def __init__(self, group_name):
        """"""
        self.group_name = group_name

################################################################################
class User_groups(Base):
    """"""
    __tablename__ = "user_groups"

    group_id = Column(Integer, ForeignKey("groups_table.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    #---------------------------------------------------------------------------
    def __init__(self, group_id, user_id):
        """"""
        self.group_id = group_id
        self.user_id = user_id


# create tables
Base.metadata.create_all(db_engine)

import seed
