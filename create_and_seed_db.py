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
sample_groups = ["Saudi Arabia", "Germany", "UK", "Brazil", "Hungary", "Russia", "Turkey",
                "Greece", "India", "Spain", "United States", "Egypt", "Sudan", "Libya",
                "Morocco", "Romania", "Portugal", "France", "Czechia", "Denmark", "Latvia",
                "Belgium", "Ireland", "Tunisia", "Ukraine", "Estonia", "Georgia", "General"]
for g in sample_groups:
    group = Group(g)
    sess.add(group)
    sess.commit()
    groups_ids.append(group.id)

    for uid in users_ids:
        if random.choice([True, False]):
            sess.add(User_groups(group.id, uid))

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

sample_names = ["COVID-19", "Jupiter Landing!", "Mohammed Ali vs Mike Tyson", "Albaik Goes International",
                "One Piece Airs Last Episode", "Blizzard Releases TBC", "Stackoverflow Goes Mobile!",
                "Europe is in Lockdown", "Classic WOW Seeing Large Numbers", "World Shortage of Hand Sanitizers",
                "Apple Releases iPhone 1!", "Samsung Market Value Crashes", "RMSA is to be Released March 18th 2020"]
sample_desc = "Lorem ipsum dolor sit amet." * 6

report_ids = []
for i in range(0, 1000):
    name = random.choice(sample_names)
    creator_id = random.choice(users_ids)
    group_id = random.choice(groups_ids)
    report = Report(name, sample_desc, creator_id, group_id)
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

# generate new ummy files and associate them with randdomly selected reports
sample_files = [(os.path.join(sample_data_dir, "pdf-file.pdf"), Media_types_enum.pdf)
                ,(os.path.join(sample_data_dir, "txt-file.txt"), Media_types_enum.txt)
                ,(os.path.join(sample_data_dir, "png-file.png"), Media_types_enum.png)
                ,(os.path.join(sample_data_dir, "mp3-file.mp3"), Media_types_enum.mp3)
                ,(os.path.join(sample_data_dir, "mp4-file.mp4"), Media_types_enum.mp4)]

sample_file_names = ["Jupiter landing", "Albaik's Best Meal", "Best Place to Visit",
                    "Blizzard Ent.", "One Piece", "Best Webapp", "19-NCOV Shocking Facts!",
                    "Stackoverflow", "Clean Code Example", "Super Classified", "Eyes Only!"]
new_files = []
for i in range(0, 2000):
    file = random.choice(sample_files)
    file_path = file[0]
    mt = file[1] # media type
    new_file_name = "{}-{}.{}".format(random.choice(sample_file_names), time.time(), mt.name)
    dest = os.path.join(data_storage_path, os.path.join(mt.name, new_file_name))
    copyfile(file_path, dest)
    new_files.append((dest, mt))


for file_path, media_type in new_files:
    file = File(file_path, random.choice(report_ids))
    sess.add(file)

sess.commit()
