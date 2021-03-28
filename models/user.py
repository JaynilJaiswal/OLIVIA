import os
from sqla_wrapper import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///db.sqlite"))  # this connects to a database either on Heroku or on localhost

class User(UserMixin, db.Model):
    __tablename__ = 'user_base'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    uname = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    gender = db.Column(db.String(100))


class User_location(UserMixin,db.Model):
    __tablename__ = 'user_location'
    id = db.Column(db.Integer, primary_key=True) 
    user_base_id = db.Column(db.Integer, db.ForeignKey('user_base.id')) 
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timezone = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state_district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postcode = db.Column(db.String(100))
    country = db.Column(db.String(100))
    country_code = db.Column(db.String(100))
    user_base = db.relationship("User",backref=db.backref("user_base", uselist=False))


class User_command_history(UserMixin,db.Model):
    __tablename__ = 'user_command_history'
    id = db.Column(db.Integer, primary_key=True)
    user_base_id = db.Column(db.Integer, db.ForeignKey('user_base.id'))
    command_time = db.Column('dateTime_created', db.DateTime, nullable=False, default=datetime.datetime.utcnow)   
    command_input_text = db.Column(db.String(500))
    command_input_filepath = db.Column(db.String(150))
    command_feature_selected = db.Column(db.String(30))
    command_output_text = db.Column(db.String(300))
    user_base = db.relationship("User",backref=db.backref("user_base_ch", uselist=False))


    

