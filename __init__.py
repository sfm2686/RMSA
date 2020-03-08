from flask import Flask, session
from sqlalchemy import create_engine
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
db_engine = create_engine('mysql+pymysql://root:@localhost')
db_engine.execute("USE RMSA") # select application db


import views
