import os
from sqla_wrapper import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///db.sqlite"))  # this connects to a database either on Heroku or on localhost

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    uname = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    gender = db.Column(db.String(100))
    # latitude = db.Column(db.Float)
    # longitude = db.Column(db.Float)
    # timezone = db.Column(db.String(100))
    # address = db.Column(db.String(100))
