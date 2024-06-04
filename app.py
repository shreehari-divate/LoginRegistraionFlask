from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
load_dotenv()
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logreg.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db=SQLAlchemy(app)
migrate=Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)

#Model
class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20),nullable=False,unique=False)
    email = db.Column(db.String(20),nullable=False,unique=True)
    password = db.Column(db.String(20),nullable=False)

#in command line:
#flask db init; flask db migrate -m "Initial migration" ; flask db upgrade

# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)

@app.route("/",methods=['GET','POST'])
def login():
    if request.method=='POST':
        name = request.form.get('name')
        password=request.form.get('password')
        user = User.query.filter_by(email=name).first()
        message = 'Invalid credentials'


        if user is None:
            return render_template('login.html',message=message)
        if user.password==password:
            login_user(user)
            return redirect(url_for('index',name=user.name))
        else:
            return render_template('login.html',message=message)

    return render_template("login.html")

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if name and email and password:
            user_exists = User.query.filter_by(email=email).first()
            if user_exists:
                msg = "Email is already registered"
                return render_template("register.html",msg=msg)
            
            hash_password = generate_password_hash(password)

            user = User(name=name, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            message="Successfully Regitered"
            return render_template("register.html",message=message)
        else:
            msg = 'Please fill out all the fields'
            return render_template('register.html',msg=msg)
    return render_template("register.html")

@app.route("/index")
def index():
    name = request.args.get('name')
    return render_template("index.html",name=name)

#driver code:
if __name__=='__main__':
    app.run(debug=True)