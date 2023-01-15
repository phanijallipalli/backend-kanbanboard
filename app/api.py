from flask_restful import Resource
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from flask_restful import Api
import datetime
from .database import db 
from flask import render_template,jsonify
from flask import current_app as app
from flask import request
from flask import abort
from .model import User,List,Tasks
from app import api
import jwt
from app import  app,bcrypt,sec_key
from datetime import date
from flask_security import auth_required, login_required, roles_accepted, roles_required, auth_token_required
import smtplib

def hash_password(password):
    pw_hash = bcrypt.generate_password_hash(password)
    return pw_hash

#---------------remainder api ---------------------------
create_remainder_parser = reqparse.RequestParser()
create_remainder_parser.add_argument("token")
create_remainder_parser.add_argument("email")

class RemainderAPI(Resource):
    def get(self):
        token = request.args.get("token",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                else:
                    return jsonify({"statuscode" : 200,"message": user.email})
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})
            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"})

    def post(self):
        args = create_remainder_parser.parse_args()
        email = args.get("email",None)
        token = args.get("token",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                elif (email == ""):
                    return jsonify({"statuscode" : 409,"message": "email cannot be empty"})
                else: 
                    user = db.session.query(User).filter((User.username == username )).first()
                    user.email = email
                    db.session.commit()
                    return jsonify({"statuscode" : 200,"message": "email created success"})      
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})
            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"})

    def put(self):
        args = create_remainder_parser.parse_args()
        token = args.get("token",None)  
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = db.session.query(User).filter((User.username == username )).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                else:
                    user.email = None
                    db.session.commit() 
                    return jsonify({"statuscode" : 200,"message": "Data deleted"})      
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"})

#---------------signup api ---------------------------

create_signup_parser = reqparse.RequestParser()
create_signup_parser.add_argument("username")
create_signup_parser.add_argument("password")
create_signup_parser.add_argument("favorite_food")



class SignupAPI(Resource):

    def post(self):
        args = create_signup_parser.parse_args()
        username = args.get("username",None)
        password = args.get("password",None)
        food =  args.get("favorite_food",None)     
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = User.query.filter_by(username = username).first()
            if user:
                return jsonify({"statuscode" : 200 ,"message": "username already exists"})

            else:
                user = User(username = username, password = hash_password(password),favorite_food = food)
                db.session.add(user)
                db.session.commit()
                user = User.query.filter_by(username = username)
                return jsonify({"statuscode" : 200, "message": "user created success"})
        else:
            return jsonify({"statuscode" : 500, "message" : "internal server error"})

class ForgotAPI(Resource):
    def post(self):
        args = create_signup_parser.parse_args()
        username = args.get("username",None)
        password = args.get("password",None)
        food =  args.get("favorite_food",None)     
        if (type(username) is str) and (username is not None) and (type(password) is str) and (password is not None) and (password != ""):
            user = db.session.query(User).filter(User.username==username).first()
            if user:
                if(user.favorite_food == food):
                    user.password = hash_password(password)
                    db.session.commit()
                    return jsonify({"statuscode" : 409, "message": "user updated success"})
                else:
                    return jsonify({"statuscode" : 200 ,"message": "user favorite food is incorrect"})
            else:
                return jsonify({"statuscode" : 200 ,"message": "username doesnot exists"})
        else:
            return jsonify({"statuscode" : 500, "message" : "internal server error"})

class LoginAPI(Resource):
    def post(self):
        args = create_signup_parser.parse_args()
        username = args.get("username",None)
        password = args.get("password",None)

        user = db.session.query(User).filter(User.username==username).first()
        if not user:
            return jsonify({"statuscode" : 409,"message": "user not found"})
        elif(bcrypt.check_password_hash(user.password,password)):
            token = jwt.encode({"user" : username, "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, sec_key )
            return jsonify({"statuscode" : 200,"message": "login success","token" : token,"user":username})
        else:
            return jsonify({"statuscode" : 409,"message": "incorrect password"})
    

#---------------------dashboardApi-------------------------- 


class DashboardAPI(Resource):
    def get(self):
        token = request.args.get("token",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                else: 
                    data = {}
                    lists = List.query.filter_by(username = username).all() 
                    for list in lists:
                        tasks = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.status == list.id))
                        list_data = []
                        for task in tasks:
                            task_data = {}
                            task_data["task-id"] = task.id
                            task_data["task-title"] = task.title
                            task_data["list-name"] = list.list_name
                            task_data["task-description"] = task.task
                            task_data["due-date"] = task.due_date
                            if (task.completed == 'true'):
                                task_data["status"] = "completed"
                            else:
                                task_data["status"] = "pending"
                            task_data["date-of-completion"] = task.date_of_completion 
                            list_data.append(task_data)
                        data[list.list_name] = list_data
                    return jsonify({"statuscode" : 200,"message": data})      
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})
            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"})

#---------------------add List Api-------------------------- 
create_addlist_parser = reqparse.RequestParser()
create_addlist_parser.add_argument("addlist")
create_addlist_parser.add_argument("token")

class AddlistsAPI(Resource):
    def post(self):
        args = create_addlist_parser.parse_args()
        addlist = args.get("addlist",None)
        token = args.get("token",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                elif (addlist == ""):
                    return jsonify({"statuscode" : 409,"message": "listname cannot be empty"})
                else: 
                    lists = db.session.query(List).filter((List.username == username ) & (List.list_name == addlist)).first()
                    if lists:
                        return jsonify({"statuscode" : 409,"message" : "list already exists"})
                    list = List(
                        username = username,
                        list_name = addlist
                        )
                    db.session.add(list)
                    db.session.commit()
                    return jsonify({"statuscode" : 200,"message": "list created success"})      
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})
            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"})

#---------------------add Task Api-------------------------- 
create_addtask_parser = reqparse.RequestParser()
create_addtask_parser.add_argument("list_name")
create_addtask_parser.add_argument("task_title")
create_addtask_parser.add_argument("task_description")
create_addtask_parser.add_argument("due_date")
create_addtask_parser.add_argument("mark_as_completed")
create_addtask_parser.add_argument("token")
class AddTaskAPI(Resource):
    def post(self):
        args = create_addtask_parser.parse_args()
        list_name = args.get("list_name",None)
        task_title = args.get("task_title",None)
        task_description = args.get("task_description",None)
        due_date = args.get("due_date",None)
        mark_as_completed = args.get("mark_as_completed",None)
        token = args.get("token",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                else: 
                    lists = db.session.query(List).filter((List.username == username ) & (List.list_name == list_name)).first() 
                    if lists: 
                        if (mark_as_completed == 'yes'):
                            completed_date = date.today().strftime('%Y-%m-%d')
                            completed = 'true'
                        else:
                            completed_date =  None
                            completed = 'false'
                        tasks = Tasks(
                                username = username,
                                task = task_description,
                                title = task_title,
                                status = lists.id,
                                due_date = due_date,
                                completed = completed,
                                date_of_completion = completed_date)    
                        db.session.add(tasks)
                        db.session.commit()
                        return jsonify({"statuscode" : 200,"message": "task created success"})      
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})
            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"})
#---------------------ListsApi-------------------------- 
class ListsAPI(Resource):
    def get(self):
        token = request.args.get("token",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                else: 
                    data = []
                    lists = List.query.filter_by(username = username).all() 
                    for list in lists:
                        data.append([list.list_name,list.id])
                    return jsonify({"statuscode" : 200,"message": data})      
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})
            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"})  
#---------------------ListApi-------------------------- 
create_list_parser = reqparse.RequestParser()
create_list_parser.add_argument("list_name")
create_list_parser.add_argument("token")
create_list_parser.add_argument("list_id")


class ListAPI(Resource):
    def put(self):
        args = create_list_parser.parse_args()
        list_name = args.get("list_name",None)
        token = args.get("token",None)
        list_id = args.get("list_id",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                else:
                    lists = db.session.query(List).filter((List.username == username ) & (List.id == list_id)).first()
                    list2 = List.query.filter_by(username = username ,list_name = list_name).all()
                    if list2:
                        return jsonify({"statuscode" : 409,"message" : "List already exists"})
                    if lists:
                        lists.list_name = list_name
                        db.session.commit()
                        return jsonify({"statuscode" : 200,"message" : "List edited success"})
                    return jsonify({"statuscode" : 409,"message" : "List not found"})
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})
        
    def delete(self):
        token = request.args.get("token",None)
        list_name = request.args.get("list_name",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                else:
                    list_name = db.session.query(List).filter((List.username == username) & (List.list_name == list_name)).first()
                    if list_name:
                        tasks = db.session.query(Tasks).filter((Tasks.username == username) & (Tasks.status == list_name.id)).all()
                        for task in tasks:
                            db.session.delete(task)
                        db.session.delete(list_name)
                        db.session.commit() 
                        return jsonify({"statuscode" : 200,"message": "Data deleted"})      
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"})

#---------------------TaskApi-------------------------- 
create_task_parser = reqparse.RequestParser()
create_task_parser.add_argument("list_name")
create_task_parser.add_argument("token")
create_task_parser.add_argument("task_title")
create_task_parser.add_argument("task_description")
create_task_parser.add_argument("due_date")
create_task_parser.add_argument("mark_as_completed")
create_task_parser.add_argument("task_id")


class TaskAPI(Resource):
    def put(self):
        args = create_task_parser.parse_args()
        list_name = args.get("list_name",None)
        token = args.get("token",None)
        task_title = args.get("task_title",None)
        task_description = args.get("task_description",None)
        due_date = args.get("due_date",None)
        mark_as_completed = args.get("mark_as_completed",None)
        task_id = args.get("task_id",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                else:
                    lists = db.session.query(List).filter((List.username == username ) & (List.list_name == list_name)).first()
                    task = db.session.query(Tasks).filter((Tasks.username == username ) & (Tasks.id == task_id)).first()
                    if lists and task:
                        if (mark_as_completed == 'yes'):
                            completed_date = date.today().strftime('%Y-%m-%d')
                            completed = 'true'
                        else:
                            completed_date =  None
                            completed = 'false'
                        task.task = task_description
                        task.title = task_title
                        task.status = lists.id
                        task.due_date = due_date
                        task.completed = completed
                        task.date_of_completion = completed_date
                        db.session.commit()
                        return jsonify({"statuscode" : 200,"message": "Task Edited success"})      
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"}) 

    
    def delete(self):
        token = request.args.get("token",None)
        task_id = request.args.get("task_id",None)
        if ((type(token) is str) and (token is not None) and (token != "")):
            try:
                decoded = jwt.decode(token, sec_key,algorithms=['HS256'])
                username = decoded['user']
                user = User.query.filter_by(username = username).first()
                if not user:
                    return jsonify({"statuscode" : 409,"message": "user not found"})
                else:
                    task = db.session.query(Tasks).filter((Tasks.username == username ) & (Tasks.id == task_id)).first()
                    if task:
                        db.session.delete(task)
                        db.session.commit()
                        return jsonify({"statuscode" : 200,"message": "Data deleted"})      
            except:
                return jsonify({"statuscode" : 500,"message" : "An exception occurred"})            
        else:
            return  jsonify({"statuscode" : 500,"message" : "An Internal server error"})


