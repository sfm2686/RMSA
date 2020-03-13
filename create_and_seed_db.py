from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables_def import *
from enums import *
from shutil import copyfile
import tables_def
import bcrypt
import random
import os
import time
import glob

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

users_ids = [user.id]
for userinfo in ["elonmusk", "timcook", "mohammedali", "stevewozniak", "dennisritchie", "royfielding"]:
    user = User(userinfo, bcrypt.hashpw(userinfo.encode("utf-8"), bcrypt.gensalt()), users_role.id)
    sess.add(user)
    sess.commit()
    users_ids.append(user.id)

sess.commit()
################################################################################
# seed groups data

groups_ids = []
for g in ["Saudi Arabia", "Germany", "UK", "Brazil", "Hungary", "Russia", "Turkey", "Greece", "India", "General"]:
    group = Group(g)
    sess.add(group)
    sess.commit()
    groups_ids.append(group.id)

    for uid in users_ids:
        if random.choice([True, False]):
            sess.add(User_groups(group.id, uid))

sess.commit()
################################################################################
# seed media types data

for mt in Media_types_enum:
    media_type = Media_type(mt.value, mt.name)
    sess.add(media_type)

sess.commit()
################################################################################
# seed tags data

tag_ids = []
for tag in Tags_enum:
    tag = Tag(tag.value, tag.name)
    sess.add(tag)
    tag_ids.append(tag.id)

sess.commit()
################################################################################
# seed dummy reports

sample_names = ["19-NCOV", "Jupiter Landing!", "Mohammed Ali vs Mike Tyson", "Albaik Goes International",
                "One Piece Airs Last Episode", "Blizzard Releases TBC", "Stackoverflow Goes Mobile!"]
sample_desc = "Lorem ipsum dolor sit amet." * 6

report_ids = []
for i in range(0, 20):
    name = random.choice(sample_names)
    creator_id = random.choice(users_ids)
    last_editor_id = random.choice(users_ids)
    group_id = random.choice(groups_ids)
    report = Report(name, sample_desc, creator_id, last_editor_id, group_id)
    sess.add(report)
    sess.commit()
    for tid in tag_ids:
        if random.choice([True, False]):
            report_tags = Report_tags(report.id, tid)
            sess.add(report_tags)
    sess.commit()
    report_ids.append(report.id)

################################################################################
# seed dummy files

sample_data_dir = "generation-storage"
data_storage_path = "media-storage"


# clean old data samples
for mt in Media_types_enum:
    for file in glob.glob("{}/*.{}".format(os.path.join(data_storage_path, mt.name), mt.name)):
        os.remove(file)

# generate dummy files and associate them with randdomly selected reports
sample_files = [(os.path.join(sample_data_dir, "txt-file.txt"), Media_types_enum.txt)
                ,(os.path.join(sample_data_dir, "png-file.png"), Media_types_enum.png)
                ,(os.path.join(sample_data_dir, "mp3-file.mp3"), Media_types_enum.mp3)
                ,(os.path.join(sample_data_dir, "mp4-file.mp4"), Media_types_enum.mp4)]

new_files = []
for i in range(0, 40):
    file = random.choice(sample_files)
    file_path = file[0]
    mt = file[1] # media type
    new_file_name = "{}.{}".format(time.time(), mt.name)
    dest = os.path.join(data_storage_path, os.path.join(mt.name, new_file_name))
    copyfile(file_path, dest)
    new_files.append((dest, mt))

sample_file_names = ["Jupiter landing video", "Albaik's Best Meal", "Best Place to Visit",
                    "Blizzard Ent.", "One Piece", "Best Webapp", "19-NCOV Shocking Facts!",
                    "Stackoverflow", "Clean Code Example", "Super Classified", "Eyes Only!"]

for nf in new_files:
    file = File(random.choice(sample_file_names), nf[0], random.choice(report_ids), nf[1].value)
    sess.add(file)

sess.commit()
