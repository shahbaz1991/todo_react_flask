from flask import Flask,jsonify,url_for,request,make_response,session
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_restful import Api,Resource
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_cors import CORS


app=Flask(__name__,static_folder='./build',static_url_path='/')
app.debug=True
manager = Manager(app)
cors = CORS(app, origin=['http://localhost:3000','https://flask-todo-initial.herokuapp.com/'])
#basedir=os.path.abspath(os.path.dirname(__file__))
# os.environ.get('SECRET_KEY')
app.config['SECRET_KEY']=os.environ.get('SECRET_KEY') or \
                        b'\xcf\x1c\xaa\xfb\x91\x92\x95q\xb7\xa7\xd4\xc4\x9e\xe9\xe0\x89'
#b'\xcf\x1c\xaa\xfb\x91\x92\x95q\xb7\xa7\xd4\xc4\x9e\xe9\xe0\x89'
app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL') or \
                                    'mysql+pymysql://root:rootpassword@localhost/newtodo_db'

#'mysql+pymysql://sql12356392:HS1jA6Eysv@ sql12.freemysqlhosting.net:3306/sql12356392'
# 'mysql+pymysql://root:rootpassword@localhost/newtodo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
ma=Marshmallow(app)
api=Api(app)
migrate=Migrate(app,db)
manager.add_command('db',MigrateCommand)


"""@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/'])
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  response.headers.add('Access-Control-Allow-Credentials', 'true')
  return response"""

app.route('/')
def start():
    return app.send_static_file('index.html')
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False, unique=True)
    email=db.Column(db.String(100),nullable=False, unique=True)
    password_hash=db.Column(db.String(500),nullable=False)
    todo=db.relationship('Todo',backref='user')   

class Todo(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    task=db.Column(db.String(500),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)   

class TodoSchema(ma.Schema):
    class Meta:
        fields=('id','title','task')
todo_schema=TodoSchema()
todos_schema=TodoSchema(many=True)

class UserDetails(Resource):
    def options(self):
        res=make_response()
        # res.headers.add('Access-Control-Allow-Origin',['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/'])
        # res.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        res.headers.add('Access-Control-Allow-Methods', 'GET')
        res.headers['Access-Control-Allow-Credentials']= 'true'
        return res

    def post(self):
        password=request.json['password']
        pass_hashed=generate_password_hash(password)
        new_user=User(name=request.json['name'],email=request.json['email'],password_hash=pass_hashed)
        db.session.add(new_user)
        db.session.commit() 

        newuser=User.query.filter_by(email=new_user.email).first()
        res=make_response('Registration Successful',200)
        # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
        res.headers['Access-Control-Allow-Credentials']= 'true'
        return res

api.add_resource(UserDetails,'/register') 

class Login(Resource):

    def options(self):
        res=make_response()
        # res.headers.add('Access-Control-Allow-Origin',['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/'])
        # res.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        res.headers.add('Access-Control-Allow-Methods', 'POST')
        res.headers['Access-Control-Allow-Credentials']= 'true'
        return res
        
    def post(self):
        login_email=request.json['email']
        login_password=request.json['password']
        user=User.query.filter_by(email=login_email).first()        
        if (user and check_password_hash(user.password_hash,login_password)):
            session['user_id']=user.id  
            res=make_response({'user_name':user.name},200) 
            # res.headers.add('Access-Control-Allow-Origin', ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/'])
            res.headers.add('Access-Control-Allow-Credentials', 'true')
            
            return res
        else:
            res=make_response('Invalid user',401)
            return res
api.add_resource(Login,'/login')

class Details(Resource):
    def get(self):
        if 'user_id' in session:
            uid=session.get('user_id')
            obj=User.query.get(uid)
            res=make_response({'user_name':obj.name},200)
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'
            return res   
api.add_resource(Details,'/details')


class Logout(Resource):

    def options(self):
        res=make_response()
        # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
        # res.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        res.headers.add('Access-Control-Allow-Methods', 'GET')
        return res

    def get(self):
        if 'user_id' in session:
            session.pop('user_id',None)
            res=make_response('Deleted session',200)
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'
            return res    
        else:
            res=make_response('Not Authorized',401)
            return res    
api.add_resource(Logout,'/logout')

class Form(Resource):   

    def options(self):
        res=make_response()
        # res.headers.add('Access-Control-Allow-Origin',['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/'])
        # res.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        res.headers.add('Access-Control-Allow-Methods', 'GET,POST')
        res.headers['Access-Control-Allow-Credentials']= 'true'
        return res

    def get(self):
        if 'user_id' in session:
            uid=session.get('user_id')
            obj=User.query.get(uid)
            data=obj.todo          
            body=todos_schema.dumps(data)     
            res=make_response(body,200)  
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'
            return res
        else:
            res=make_response('Not Authorized',401)
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'
            return res

    def post(self):
        if "user_id" in session:
            obj=User.query.get(session["user_id"])        
            new_todo=Todo(title=request.json['title'],task=request.json['task'],user=obj)
            db.session.add(new_todo)
            db.session.commit()
            body=todo_schema.dumps(new_todo)
            res=make_response(body,200)  
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'
            return res
        else:
            res=make_response('Not Authorized',401)
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'
            return res
    
api.add_resource(Form,'/todo')

class FormId(Resource):

    def options(self,todo_id):
        res=make_response()
        # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
        # res.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        res.headers.add('Access-Control-Allow-Methods', 'GET,PUT,DELETE')
        res.headers['Access-Control-Allow-Credentials']= 'true'
        return res

    def get(self,todo_id):
        if "user_id" in session:
            todo=Todo.query.get_or_404(todo_id)
            body= todo_schema.dumps(todo)
            res=make_response(body,200)  
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'
        else:
            res=make_response('Not Authorized',401)
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'        
            return res

    def put(self,todo_id):
        if "user_id" in session:
            todo=Todo.query.get_or_404(todo_id)
            if 'task' in request.json:
                todo.task=request.json['task']
            db.session.commit()
            body= todo_schema.dumps(todo)
            res=make_response(body,200)  
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'
            return res
        else:
            res=make_response('Not Authorized',401)
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'        
            return res

    def delete(self,todo_id):
        if "user_id" in session:
            todo=Todo.query.get_or_404(todo_id)
            db.session.delete(todo)
            db.session.commit()
            res=make_response('Data Deleted',204)
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'
            return res
        else:
            res=make_response('Not Authorized',401)
            # res.headers['Access-Control-Allow-Origin']= ['http://localhost:3000','https://git.heroku.com/flask-todo-initial.git/']
            res.headers['Access-Control-Allow-Credentials']= 'true'        
            return res

api.add_resource(FormId,'/todo/<int:todo_id>')

if __name__ == "__main__":
    manager.run()
