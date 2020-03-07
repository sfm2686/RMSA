from flask import Flask, session
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config.from_pyfile('app.cfg')

import views
