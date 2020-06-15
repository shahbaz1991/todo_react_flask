from flask import Flask,url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api,Resource
from flask_marshmallow import Marshmallow

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:rootpassword@localhost/newtodo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
ma=Marshmallow(app)
api=Api(app)

class Todo(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    task=db.Column(db.String(500),nullable=False)
    
    def __init__(self,title,task):
        self.title=title
        self.task=task

class TodoSchema(ma.Schema):
    class Meta:
        fields=('id','title','task')
todo_schema=TodoSchema()
todos_schema=TodoSchema(many=True)

class Form(Resource):
    def get(self):
        data=db.session.query(Todo).all()
        return todos_schema.dump(data)

    def post(self):
        new_todo=Todo(title=request.json['title'],task=request.json['task'])
        db.session.add(new_todo)
        db.session.commit()
        return todo_schema.dump(new_todo)
api.add_resource(Form,'/todo')

class FormId(Resource):
    def get(self,todo_id):
        todo=Todo.query.get_or_404(todo_id)
        return todo_schema.dump(todo)
    def put(self,todo_id):
        todo=Todo.query.get_or_404(todo_id)
        if 'task' in request.json:
            todo.task=request.json['task']
        db.session.commit()
        return todo_schema.dump(todo)
    def delete(self,todo_id):
        todo=Todo.query.get_or_404(todo_id)
        db.session.delete(todo)
        db.session.commit()
        return 'data deleted',204
api.add_resource(FormId,'/todo/<int:todo_id>')

if __name__ == "__main__":
    app.run(debug=True)
