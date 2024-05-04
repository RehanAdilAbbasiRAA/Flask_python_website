from flask import Flask,render_template,request,session,redirect,url_for #we use to import our template folder,
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json,os,math
from flask_mail import Mail,Message
from werkzeug.utils import secure_filename#to upload file securly 

# import os
# from werkzeug import secure_filename

with open("config.json","r") as c:
    params1=json.load(c)["params"]

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = params1['upload_location']

app.config.update(
    SECRET_KEY="Rehan031357",
    MAIL_SERVER = "smtp.googlemail.com",
    MAIL_PORT =587,
    # MAIL_USE_SSL = True,
    MAIL_USE_TLS= True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = params1["gmail_username"],
    MAIL_PASSWORD = params1["gmail_password"])
    # MAIL_USE_TLS : default False 
    # MAIL_DEBUG : default app.debug
    # MAIL_DEFAULT_SENDER : default None
    # MAIL_MAX_EMAILS : default None
    # MAIL_SUPPRESS_SEND : default app.testing
    # MAIL_ASCII_ATTACHMENTS : default False
mail=Mail(app)
# app.conf
# ig['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
# how we can change the uri using json file
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/blogdata'
app.config['SQLALCHEMY_DATABASE_URI'] = params1["local_uri"]
db = SQLAlchemy(app)


class Contact_us(db.Model):#table name
    customer_ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30), unique=False, nullable=False)
    Email = db.Column(db.String(30), unique=False, nullable=False)
    Phone_no = db.Column(db.String(12), unique=False, nullable=False)
    Message = db.Column(db.String(1100), unique=False, nullable=False)
    Date = db.Column(db.DateTime(), nullable=True)

class Posts(db.Model):#table name
    sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255), unique=False, nullable=False)
    slug= db.Column(db.String(30), unique=False, nullable=False)
    Content = db.Column(db.String(255), unique=False, nullable=False)
    Author = db.Column(db.String(255), unique=False, nullable=False)
    Img_file = db.Column(db.String(20), unique=False, nullable=False)
    Date = db.Column(db.DateTime(), nullable=True)

class User(db.Model):#table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)

@app.route("/")#open when R
def home():#this is our 2nd app
    #here we have used limit start from 0 to variable in .json file  this line will fetch all the data from databse,and now you can use it in templates
    # posts=Posts.query.filter_by().all()[0:params1["number_of_posts"]]
    posts=Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params1["number_of_posts"]))
    page=request.args.get("page")
    if(not str(page).isnumeric()):#if its not anumber then make it a number
        page=1
    page=int(page)
    posts=posts[int(page-1)*int(params1["number_of_posts"]) : int(page-1)*int(params1["number_of_posts"])+int(params1["number_of_posts"])]

    if page==1:
        next1="/?page="+str(page+1)
        prev="#"
    elif page==last:
        prev="/?page="+str(page-1)
        next1="#"
    else:
        next1="/?page="+str(page+1)
        prev="/?page="+str(page-1)
    #pagination start from here

    return render_template('home.html',params=params1,posts=posts ,prev=prev,next1=next1) #we are passing the json paramter to every template
# we have to write posts = posts to fetch data from database
@app.route("/contact",methods =['GET','POST'])#open when R
def contact():#this is our 2nd app
    if request.method == 'POST':# this is is post reqsuest for data entry in databse
        # add entry to the database so take it from contact.html 
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        # Date=request.form.get('message')
        print(name, email, phone, message)
        # =request.form.get('name')

        entry=Contact_us(Name=name,Email=email, Phone_no=phone, Message=message,Date=datetime.now())
        #saving data in class varibles

        db.session.add(entry)
        db.session.commit()# save changes
        mail.send_message(f"New message from BLOG User {name}",sender="RAA@app.com",recipients=[params1["gmail_username"]],body=message +"\n" + f"Contact No:- {phone} \n Contact Email:- {email}",
                        )
        # flash("you submitted sucessfully","sucess")
        # return redirect('/contact')
    return render_template('contact.html',params=params1)

@app.route("/about",methods =['GET','POST'])#open when Rs
def about():
    if request.method == 'POST':
        name = request.form.get('name')
        print("Name received from form:", name)  # Print out the name received from the form
        try:
            entry = User(name=name)
            db.session.add(entry)
            db.session.commit()
            print("User entry added successfully.")
        except Exception as e:
            print("Error occurred while adding user entry:", e)  # Print out any error that occurred during database operation
    return render_template('about.html',params=params1)

@app.route("/post/<string:post_slug>", methods=["GET"])#now we have pass a slug so we have to pass it in function aslo to acess it
def post(post_slug):#this is our 2nd app
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params1,post=post)
# post = post (this line allow your data to now use in templates post file )

@app.route("/dashboard",methods=["GET","POST"])
def dashboard():#this is our 2nd app
    if 'user' in session and session['user']==params1["admin_username"]:
        posts=Posts.query.filter_by().all()
        return render_template('dashboard.html',params=params1,posts=posts)
    if request.method=="POST":
        username=request.form.get("uname")
        userpass=request.form.get("pass")
        if (username==params1["admin_username"] and userpass==params1["admin_password"]):
            session['user']=username #we can use any name inside session["ANY"]
            posts=Posts.query.filter_by().all()
            return render_template('dashboard.html',params=params1,posts=posts)
    
    return render_template('login.html',params=params1)

@app.route("/edit/<string:sno>",methods=["GET","POST"])
def edit(sno):#this is our 2nd app
    if "user" in session and session["user"]==params1["admin_username"]: 
        if request.method == "POST":
            Btitle=request.form.get("btitle")
            Bslug=request.form.get("bslug")
            Bcontent=request.form.get("bcontent")
            Bauthor=request.form.get("bauthor")
            Bimg_file=request.form.get("bimg_file")
            date = datetime.now()

            if sno=="0":
                post=Posts(Title=Btitle,slug=Bslug, Content=Bcontent, Author=Bauthor,Img_file=Bimg_file,Date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.Title=Btitle
                post.slug=Bslug
                post.Content=Bcontent
                post.Author=Bauthor
                post.Img_file=Bimg_file
                post.Date=date
                db.session.commit()
                return redirect("/edit/"+sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params1,post=post,sno=sno)#we are passing the params1 paramter into our new template



@app.route("/logout")
def logout():#this is our 2nd appsssssssss
    session.pop('user')
    return redirect('/dashboard')

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params1['admin_username']):
        if (request.method == 'POST'):
            f= request.files['file1']
            try:
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
                return redirect('/dashboard')
            except:
                return "please select a file first"

@app.route("/delete/<string:sno>",methods=["GET","POST"])
def delete(sno):#this is our 2nd app
    if "user" in session and session["user"]==params1["admin_username"]: 
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        posts=Posts.query.filter_by().all()
        return render_template('dashboard.html',params=params1,posts=posts)

app.run(debug=True)
