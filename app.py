'''
Handles startup and configuration of the application.
'''

from flask import Flask
from __init__ import app

if __name__ == "__main__":
    app.run(debug=True)
