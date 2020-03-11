from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint

Base = declarative_base()

################################################################################
class Role(Base):
    """"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    role = Column(String(10))

    __table_args__ = (
        UniqueConstraint('role'),
        )

    #---------------------------------------------------------------------------
    def __init__(self, id, role):
        """"""
        self.id   = id
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
class Group(Base):
    """"""
    __tablename__ = "groups_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String(20))

    __table_args__ = (
        UniqueConstraint('group_name'),
        )

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
        self.user_id  = user_id

################################################################################
class Media_type(Base):
    """"""
    __tablename__ = "media_types"

    type = Column(String(20), primary_key=True)

    #---------------------------------------------------------------------------
    def __init__(self, type):
        """"""
        self.type = type

################################################################################
class Tag(Base):
    """"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(20))

    __table_args__ = (
        UniqueConstraint('tag'),
        )

    #---------------------------------------------------------------------------
    def __init__(self, tag):
        """"""
        self.tag = tag

################################################################################
class Report(Base):
    """"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    desc = Column(String(200))
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    last_editor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    group_id = Column(Integer, ForeignKey("groups_table.id", ondelete="CASCADE"))

    #---------------------------------------------------------------------------
    def __init__(self, name, desc, creator_id, last_editor_id, group_id):
        """"""
        self.name           = name
        self.desc           = desc
        self.creator_id     = creator_id
        self.last_editor_id = last_editor_id
        self.group_id       = group_id

################################################################################
class File(Base):
    """"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String(40))
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"))
    media_type = Column(String(4), ForeignKey("media_types.type"))

    #---------------------------------------------------------------------------
    def __init__(self, file_path, report_id, media_type):
        """"""
        self.file_path  = file_path
        self.report_id  = report_id
        self.media_type = media_type
