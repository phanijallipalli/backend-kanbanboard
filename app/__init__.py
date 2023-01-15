from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_restful import  Api
from flask_cors import CORS


app = Flask(__name__)
path_db = os.path.join(os.path.dirname(__file__),'kanban-board.sqlite3')
URI = 'sqlite:///{}'.format(path_db)
app.config['SQLALCHEMY_DATABASE_URI'] = URI
app.config['DEBUG'] = True
sec_key = app.config['SECRET_KEY'] = 'ejhk52@34ry'



app.app_context().push()
CORS(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
api = Api(app)




