from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Check_in(db.Model):
    check_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    check_in = db.Column(db.Time)
    date = db.Column(db.Date, default=func.now)

class Check_out(db.Model):
    check_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    check_out = db.Column(db.Time)
    date = db.Column(db.Date, default=func.now)
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(64), unique = True)
    password  = db.Column(db.String(64), unique = True)
    name = db.Column(db.String(64))
    home_adress = db.Column(db.String(64))
    phone_number = db.Column(db.String(15))
    contract_hours = db.Column(db.Integer)
    check_in = db.relationship('Check_in')
    check_out = db.relationship('Check_out')

