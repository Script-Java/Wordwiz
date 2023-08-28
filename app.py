from flask import Flask
import pretty_errors
from newsapi import get_news
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SECRET_KEY'] = 'SECRET_KEY'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(55), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    blogs = db.relationship('Blog', backref='author', lazy=True)
# blog db    
class Blog(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    
# create the db    
#with app.app_context():
#    db.create_all()

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(),Length(max=100),Email()])
    password = StringField('Password', validators=[DataRequired(),Length(min=10, max=50)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Must match password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])  
    submit = SubmitField('Login')

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Create Post')
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to access this page")
    return redirect(url_for('login'))

    
news = get_news('API_KEY_REMOVED_FOR_GIT_HUB')

@app.route('/')
def index():
    return render_template('index.html', news=news)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blogs')
def blogs():
    blogs = Blog.query.all()
    return render_template('blogs.html', blogs=blogs)

@app.route('/signup', methods=['POST','GET'])
def signup():
    form = RegisterForm()
    try:
        if form.validate_on_submit():
            hashed_pass = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_pass, email=form.email.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Account has been created successfully")
            return redirect(url_for('login'))
        
    except Exception as e:
        return render_template('error.html', error=e)
    
    return render_template('signup.html', form=form)

@app.route('/login', methods=['POST','GET'])
def login():
    form = LoginForm()
    try:
        if form.validate_on_submit():
            username = form.username.data
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('aindex'))
            
    except Exception as e:
        return render_template('error.html',error=e)
    
    return render_template('login.html', form=form)


@app.route('/aindex')
@login_required
def aindex():
    return render_template('aindex.html', news=news)

@app.route('/ablogs')
@login_required
def ablogs():
    blogs = Blog.query.all()
    myblogs = Blog.query.filter_by(user_id=current_user.id).all()
    return render_template('ablogs.html', blogs=blogs, myblogs=myblogs)

@app.route('/create', methods=['POST','GET'])
@login_required
def create():
    form = BlogForm()
    return render_template('create.html', form=form)

@app.route('/add', methods=['POST','GET'])
@login_required
def add():
    try:
        blog_title = request.form.get('form_title')
        blog_content = request.form.get('form_content')
        new_blog = Blog(title=blog_title,content=blog_content)
        current_user.blogs.append(new_blog)
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('ablogs'))
    
    except Exception as e:
        return render_template('error.html',error=e)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
