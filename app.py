from flask import Flask , render_template,request,redirect,url_for,jsonify,abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:1234@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db= SQLAlchemy(app)

migrate=Migrate(app,db)



      

class Todo(db.Model):
    __tablename__='todos'
    id= db.Column(db.Integer , primary_key=True )
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=True, default=False)
    list_id=db.Column(db.Integer,db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo{self.id} {self.description}>'

class TodoList(db.Model):
    __tablename__='todolists'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(),nullable=False)
    todos =db.relationship('Todo', backref='list', lazy=True)
    def __repr__(self):
        return f'<TodoList {self.id} {self.name}>'
  
#db.create_all()

@app.route('/todos/create',methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo=Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description

    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
    finally:
        db.session.close() 
        if not error:
            return(jsonify(body))
        else:
            abort(400)

@app.route('/todos/<todo_id>set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:      
        completed= request.get_json()['completed']
        todo=Todo.query.get(todo_id)
        todo.completed=completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

    

@app.route('/')
def index():
    return render_template('index.html',data =Todo.query.order_by('id').all())

if __name__ == '__main__':
    app.debug=True
    app.run(host="0.0.0.0", port=3000)
    