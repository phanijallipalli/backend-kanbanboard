from app import app
from app import api

from app.api import SignupAPI,DashboardAPI,ListsAPI,ListAPI,AddlistsAPI,AddTaskAPI,TaskAPI,LoginAPI,RemainderAPI,ForgotAPI
api.add_resource(SignupAPI, "/api/signup") 
api.add_resource(LoginAPI, "/api/login") 
api.add_resource(DashboardAPI, "/api/dashboard") 
api.add_resource(ListsAPI, "/api/lists")
api.add_resource(ListAPI, "/api/list")
api.add_resource(AddlistsAPI, "/api/addlist")
api.add_resource(AddTaskAPI, "/api/addtask")
api.add_resource(TaskAPI, "/api/task")
api.add_resource(RemainderAPI, "/api/remainders")
api.add_resource(ForgotAPI, "/api/forgotpassword")


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)