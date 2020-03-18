from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from datetime import timedelta
import os
import tables_def

csrf = CSRFProtect()

app = Flask(__name__)
csrf.init_app(app)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)

db_url = os.environ['DATABASE_URL']
db_name = os.environ['DATABASE_NAME']

db_engine = create_engine(db_url)
# if database_exists("{}/{}".format(db_url, db_name)):
#     db_engine.execute("USE {}".format(db_name)) # select application db
# else:
#     raise SystemExit("Please make sure your create and seed the database before running the application.")
db_engine.execute("USE {}".format(db_name)) # select application db

tables_def.Base.metadata.create_all(db_engine)

import views
