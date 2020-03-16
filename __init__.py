from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
import os
import tables_def

csrf = CSRFProtect()

app = Flask(__name__)
csrf.init_app(app)
app.config['SECRET_KEY'] = os.urandom(12).hex()

db_engine = create_engine('mysql+pymysql://root:@localhost')
if database_exists('mysql+pymysql://root:@localhost/RMSA'):
    db_engine.execute("USE RMSA") # select application db
else:
    raise SystemExit("Please make sure your create and seed the database before running the application.")

tables_def.Base.metadata.create_all(db_engine)

import views
