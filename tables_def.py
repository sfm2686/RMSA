from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint

Base = declarative_base()

################################################################################
class Role(Base):
    """"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    role = Column(String(10))

    #---------------------------------------------------------------------------
    def __init__(self, id, role):
        """"""
        self.id = id
        self.role = role

################################################################################
class User(Base):
    """"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20))
    password = Column(String(60))
    role_id = Column(Integer, ForeignKey("roles.id"))

    __table_args__ = (
        UniqueConstraint('username'),
        )

    #---------------------------------------------------------------------------
    def __init__(self, username, password, role_id):
        """"""
        self.username = username
        self.password = password
        self.role_id  = role_id

    def __repr__(self):
        return "username: {}, role_id:{}".format(self.username, self.role_id)

################################################################################
# class User_role(Base):
#     """"""
#     __tablename__ = "user_roles"
#
#     role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
#
#     __table_args__ = (
#         UniqueConstraint('user_id'), # one role per user
#         )
#
#     #---------------------------------------------------------------------------
#     def __init__(self, role_id, user_id):
#         """"""
#         self.role_id = role_id
#         self.user_id = user_id

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
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    #---------------------------------------------------------------------------
    def __init__(self, group_id, user_id):
        """"""
        self.group_id = group_id
        self.user_id = user_id
