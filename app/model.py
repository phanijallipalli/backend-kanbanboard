from enum import unique
from app import db

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String,primary_key = True, nullable = False, unique = True)
    password = db.Column(db.String,nullable = False)
    email = db.Column(db.String)
    favorite_food = db.Column(db.String,nullable = False)

class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer,primary_key = True, nullable = False, unique = True ,autoincrement=True)
    list_name = db.Column(db.String,nullable = False,unique = False)
    username = db.Column(db.String, db.ForeignKey('users.username'),nullable = False)

class Tasks(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key = True,nullable=False,autoincrement=True,unique = True)
    username = db.Column(db.String, db.ForeignKey('users.username'),nullable = False)
    task = db.Column(db.String,nullable = False)
    title = db.Column(db.String,nullable = False)
    status = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable = False) #list name
    due_date = db.Column(db.String, nullable = False)
    completed = db.Column(db.String)
    date_of_completion = db.Column(db.String)


db.create_all()
db.session.commit()