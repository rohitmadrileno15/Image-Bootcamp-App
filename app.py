from password_generator import PasswordGenerator

from flask import Flask,redirect, url_for,render_template, request,session,flash,request
import os
import datetime
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField , FileAllowed
from wtforms import StringField , PasswordField,SubmitField , SelectField
from wtforms.validators import DataRequired,Length, Email , EqualTo, ValidationError
from flask_login import LoginManager, UserMixin, login_user,current_user,logout_user,login_required
from save_pic import save_picture , save_picture_student
from datetime import date
import gunicorn

app = Flask(__name__)

app.config['SECRET_KEY'] = '450933c08c5ab75e79619102eddf47dee813a9d6'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

app.jinja_env.filters['zip'] = zip

db = SQLAlchemy(app)

login_manager = LoginManager(app)



class User(db.Model , UserMixin):
    id = db.Column(db.Integer,primary_key= True)
    username = db.Column(db.String(15), unique= True, nullable = False)
    email = db.Column(db.String(120), unique= True, nullable = False)
    password = db.Column(db.String(60), nullable = False)
    info_user = db.Column(db.String(20) , nullable = False)  
    #Student or User
    info_type_student  =   db.Column(db.String(20) , nullable = True )

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.info_type_student}')"


class Tasks(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    instructor_username = db.Column(db.String(15), nullable = False)
    track = db.Column(db.String(12), nullable = False)
    status = db.Column(db.String(20), nullable = True)  
    file_name = db.Column(db.String(200), nullable = False)  
    Title  =   db.Column(db.String(100) , nullable = True )
    message  =   db.Column(db.String(800) , nullable = True )
    date_time = db.Column(db.String(20) , nullable = False)

    def __repr__(self):
        return f"Tasks('{self.instructor_username}','{self.track}')"


class Studentsdidtasks(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    student_username = db.Column(db.String(15), nullable = False)
    student_track = db.Column(db.String(15), nullable = False)
    assigned_instructor =  db.Column(db.String(30), nullable = False)
    task_no = db.Column(db.String(12), nullable = False)
    submitted = db.Column(db.String(20), nullable = True)  
    file_name = db.Column(db.String(200), nullable = False)  
    note  =   db.Column(db.String(800) , nullable = True )
    date_time = db.Column(db.String(20) , nullable = False)
    grade = db.Column(db.String(10) , nullable = True)
    

    def __repr__(self):
        return f"Tasks('{self.student_username}')"



@login_manager.user_loader
def load_user(user_id):
    return (User.query.get(int(user_id)))



class RegistrationForm(FlaskForm):    
    username = StringField('UserName' , validators = [DataRequired() , Length(min = 3, max = 14)])
    email = StringField('Email' , validators = [DataRequired() , Email()])
    password = PasswordField('Password' , validators = [DataRequired()])
    Confirm_password = PasswordField('Confirm Password' , validators = [DataRequired() , EqualTo('password')])
    submit = SubmitField('Sign Up!')



class StudentRegistrationForm(FlaskForm):    
    username = StringField('UserName' , validators = [DataRequired() , Length(min = 3, max = 14)])
    email = StringField('Email' , validators = [DataRequired() , Email()])
    track = SelectField(        
        'Select a track',
        choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')]
        )
    password = PasswordField('Password' , validators = [DataRequired()])
    Confirm_password = PasswordField('Confirm Password' , validators = [DataRequired() , EqualTo('password')])
    submit = SubmitField('Sign Up!')
    

class LoginForm(FlaskForm):
    email = StringField('Email' , validators = [DataRequired() , Email()])
    password = PasswordField('Password' , validators = [DataRequired()])
    submit = SubmitField('Log in.')

class AdminForm(FlaskForm):
    secret_key = StringField('Secret Key' , validators = [DataRequired()])
    submit = SubmitField('Get Access')



@app.route("/"  )
def home():
    
    return render_template('home.html' )
    

@login_required
@app.route("/instructor_homepage", )
def instructor_homepage():
    if (current_user.is_authenticated):
        var_info_user = (current_user.info_user)
        print(var_info_user)
        if(var_info_user != "STUDENT"):
            return render_template('instructor_homepage.html' , username = current_user.username , task_record = Tasks.query.filter_by(instructor_username = current_user.username))
    return ("<h3> You are not authorised here without logging in </h3>")

@login_required
@app.route("/index", methods = ['GET'] )
def index():
    if (current_user.is_authenticated):
        var_info_user = (current_user.info_user)
        print(var_info_user)
        if(var_info_user == "STUDENT"):
            obj_2 = Studentsdidtasks.query.filter_by(student_username = current_user.username)
            obj_1  = Tasks.query.filter_by(track = current_user.info_type_student)
            return render_template('index.html' , username = current_user.username , user_type = current_user.info_type_student ,  data = obj_1 , data2= obj_2 )
    return ("<h3> You are not authorised here without logging in </h3>")

 
@app.route("/instructor_register", methods = ['GET' , "POST"] )
def instructor_register():

    form = RegistrationForm()

    if (form.validate_on_submit()):

        hashed_pwd = form.password.data
        user = User(username = form.username.data ,email = form.email.data, password = hashed_pwd , info_user = "INSTRUCTOR" )       
        u = form.username.data
        e = form.email.data
        user1 = User.query.filter_by(username =  u ).first()
        user2 = User.query.filter_by(email = e).first()

        if (user1 or user2):
            return ("<h1> Credentials already taken!  </h1>")
        else:
            db.session.add(user)
            db.session.commit()
            flash(f'Your account has been created, Login!' , 'success')
            return redirect(url_for('login'))
   

    else:
        return render_template('instructor_register.html' ,  form = form )


@app.route("/student_register", methods = ['GET' , "POST"] )
def student_register():

    form = StudentRegistrationForm()

    if (form.validate_on_submit()):
        track_form = form.track.data
        hashed_pwd = form.password.data
        user = User(username = form.username.data ,email = form.email.data, password = hashed_pwd , info_type_student = track_form ,  info_user = "STUDENT" )       
        u = form.username.data
        e = form.email.data
        user1 = User.query.filter_by(username =  u ).first()
        user2 = User.query.filter_by(email = e).first()

        if (user1 or user2):
            return ("<h1> Credentials already taken!  </h1>")
        else:
            db.session.add(user)
            db.session.commit()
            flash(f'Your account has been created, Login!' , 'success')
            return redirect(url_for('login'))
             

    else:
        return render_template('student_registration.html' ,  form = form )




@app.route("/login" , methods = ['GET' , "POST"])
def login():
    if (current_user.is_authenticated):
        var_info_user = (current_user.info_user)
        print(var_info_user)
        if(var_info_user == "STUDENT"):
            return redirect(url_for('index' , username = current_user.username))
        else:
            return redirect(url_for('instructor_homepage' , username = current_user.username))

    form = LoginForm()
    if (form.validate_on_submit() ):
        print(form.email.data , form.password.data)
        user = User.query.filter_by(email = form.email.data).first()
        
        if(user and (user.password == form.password.data)):
            login_user(user , remember = False)
            next_page = request.args.get('next')
            if(user.info_user == "STUDENT"):
                return redirect(next_page) if (next_page) else (redirect(url_for('index' , username = current_user.username)))
            else:
                return redirect(next_page) if (next_page) else (redirect(url_for('instructor_homepage' , username = current_user.username)))
        else:
            return ("<br> <h1>You have entered wrong credentials for Logging in.</h1><br> <p>Go back and Log in Again! </p>")

    else:
        return render_template('login.html' , form = form )


#putting this here because login is just above it

login_manager.login_view  = 'login'
login_manager.login_message_category = 'info'


@app.route("/loggedout" )

def logout():
    logout_user()
    return redirect(url_for('login'))



@login_required
@app.route("/instructor_homepage/tasks", methods = ['GET' , 'POST'] )
def instructor_tasks():
    if (current_user.is_authenticated):
        var_info_user = (current_user.info_user)
        print(var_info_user)
        if(var_info_user != "STUDENT"):
            return render_template('instructor_tasks.html' , username = current_user.username)
    return ("<h3> You are not authorised here without logging in </h3>")

@login_required
@app.route("/instructor_homepage/tasks/post_task", methods = ['GET' , 'POST'] )
def instructor_post_task():
    from datetime import date
    if (current_user.is_authenticated):
        var_info_user = (current_user.info_user)
        print(var_info_user)
        if(var_info_user != "STUDENT"):
            if(request.method == "POST"):
                print("Got Req")
                category = request.form.get('category')
                title = request.form.get('title')
                msg = request.form.get('message')
                file_name = save_picture(app.root_path , request.files['myfile'])
                print(file_name)
                if(file_name == 0):
                    return "Upload a picture file or a .psd or a .ai file"
                print( category , title ,file_name ,  msg)
                date_ = date.today()
                print(date_)
                tasks_req = Tasks(instructor_username = current_user.username ,track = category, status = "YES" , Title = title , message = msg , file_name = file_name , date_time = date_)
                db.session.add(tasks_req)
                db.session.commit()
                return redirect(url_for('instructor_tasks' , script_info ="Task has been set"))

                

    return ("<h3> You are not authorised here without logging in </h3>")


@login_required
@app.route("/student_get_tasks", methods = ['GET'] )
def student_get_tasks():
    if (current_user.is_authenticated):
        var_info_user = (current_user.info_user)
        print(var_info_user)
        if(var_info_user == "STUDENT"):
            
            obj_1  = Tasks.query.filter_by(track = current_user.info_type_student)
            return render_template('student_tasks.html' , data = obj_1 )
    return ("<h3> You are not authorised here without logging in </h3>")

@login_required
@app.route("/student_get_tasks/post_task", methods = ['GET' , 'POST'] )
def student_get_tasks_post_task():
    if (current_user.is_authenticated):
        var_info_user = (current_user.info_user)
        print(var_info_user)
        if(var_info_user == "STUDENT"):
            if(request.method == "POST"):
                task_no = request.form.get('upldtext')
                inst_name = request.form.get('assigned_instructor')
                msg = request.form.get('message')
                file_name = save_picture_student(app.root_path , request.files['myfile'])
                print(task_no ,file_name ,  msg)
                if(file_name == 0):
                    return "Upload a picture file or a .psd or a .ai file"
                date_ = date.today()
                print(date_)
                user1 = Studentsdidtasks.query.filter_by(student_username = current_user.username , task_no = task_no ).first()
                if(user1):
                    return "Already Submitted"

                students_tasks_req = Studentsdidtasks(student_username = current_user.username ,task_no = task_no, student_track = current_user.info_type_student ,  submitted = "YES" ,   note = msg , file_name = file_name , date_time = date_ , assigned_instructor = inst_name)
                db.session.add(students_tasks_req)
                db.session.commit()
                return "Submitted!"
            else:
                return "error, please try again"
                
    return ("<h3> You are not authorised here without logging in </h3>")


@app.route("/admin", methods = ['GET' , 'POST'] )
def admin():
    form = AdminForm()
    if (form.validate_on_submit()):
        if(form.secret_key.data == app.config['SECRET_KEY']):
            people_no = len(User.query.all())
            instructor_no = User.query.filter_by(info_user = "INSTRUCTOR").count()
            student_no  =  User.query.filter_by(info_user = "STUDENT").count() 
            
            all_vals = User.query.filter_by(info_user = "STUDENT")
            
            student_beginner = 0
            student_intermediate = 0
            student_advanced = 0
            for row in all_vals:
        
                if(row.info_type_student == "Beginner"):
                    student_beginner +=1
                if(row.info_type_student == "Intermediate"):
                    student_intermediate +=1
                if(row.info_type_student == "Advanced"):
                    student_advanced +=1
            
            tasks_begin = Tasks.query.filter_by(track = "Beginner").count()
            tasks_int = Tasks.query.filter_by(track = "Intermediate").count()
            tasks_adv = Tasks.query.filter_by(track = "Advanced").count()
            list_of_tasks = [tasks_begin, tasks_int , tasks_adv]

            list_of_done_tasks = [Studentsdidtasks.query.filter_by(student_track = "Beginner").count() , Studentsdidtasks.query.filter_by(student_track = "Intermediate").count() ,Studentsdidtasks.query.filter_by(student_track = "Advanced").count() ]

            return render_template('student-graphs.html' , people_no = people_no , instructor_no = instructor_no ,student_no = student_no , student_advanced = student_advanced , student_intermediate = student_intermediate , student_beginner = student_beginner , list_of_tasks = list_of_tasks , list_of_done_tasks = list_of_done_tasks  )
        else:
            return ("YOU DON'T HAVE ACCESS TO THIS URL")
    return render_template('admin-panel-form.html' , form = form  )


@login_required
@app.route("/instructor_homepage/grade_tasks", methods = ['GET' , 'POST'] )
def instructor_grade_tasks():
    import re
    if (current_user.is_authenticated):
        var_info_user = (current_user.info_user)
        print(var_info_user)
        if(var_info_user != "STUDENT"):
            submitted_tasks = Studentsdidtasks.query.filter_by(assigned_instructor = current_user.username)
            if(request.method == "POST"):
                data_graph = request.form.to_dict(flat=False)
                for key in data_graph:
                    
     
                    if(re.search("grades", key) ):
                        get_grade = (str(data_graph[key][0]).strip()) 
                    if(re.search("rowid", key) ):
                        id_row = (str(data_graph[key][0]).strip())      
                         

                grader = Studentsdidtasks.query.filter_by(id=int(id_row)).first()
                setattr(grader, 'grade', get_grade)
                db.session.commit()
            return render_template('instructor_tasks_check.html' , username = current_user.username , submitted_tasks = submitted_tasks)
    return ("<h3> You are not authorised here without logging in </h3>")

@app.errorhandler(404)

def not_found(e):

  return ("<h1>404 Error</h1>")




if __name__ == '__main__':
    app.run(debug= True)