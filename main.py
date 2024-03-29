from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y3568nwhbu8'


class BlogPost(db.Model):                                       #This is creating a table that will store the blog info
    id = db.Column(db.Integer, primary_key=True)                #This is setting up the id column and setting it as a primary key??
    title = db.Column(db.String(120))                           #This is setting a column in the table named title which will store the title for the blog post
    post = db.Column(db.String(5000))                              #This is setting up a Column which will store the content in the blogpost
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, post, owner):                         #Not really sure what this does, but it initalizes the table I guess?
        self.title = title
        self.post = post
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('BlogPost', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/')
def home():
    users = User.query.all()
    return render_template('home.html', users=users)


@app.route('/blog', methods=['GET', 'POST'])                        #This is setting up the main page for the web application
def index():

    blog_id = request.args.get('id')
    user_id = request.args.get('userid')
    posts = BlogPost.query.all()
    # Recent blog posts order to top.


    if blog_id:
        post = BlogPost.query.filter_by(id=blog_id).first()
        return render_template("post.html", title=post.title, post=post.post, user=post.owner.username, user_id=post.owner_id)
    if user_id:
        entries = BlogPost.query.filter_by(owner_id=user_id).all()
        return render_template('singleuser.html', entries=entries)

    return render_template('index.html', posts=posts)

    # post_id = str(request.args.get('id'))  
    # mypost =  BlogPost.query.get(post_id)                                                 #This is setting a function so that the page works?
    # posts = BlogPost.query.all()                              #I think this line pulls the info from the SQL table?

    # if mypost:
    #     entries = BlogPost.query.filter_by(owner_id=mypost).all()
    #     return render_template('post.html', entries=entries)


    # return render_template('index.html', posts=posts, mypost=mypost)       #This will render the html template set for the index


@app.route('/newpost', methods=['POST','GET'])                #This is another page, which is where the user will input their blog
def newpost():
    return render_template('newpost.html')


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST','GET'])
def login():
    username_error = ""
    password_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        users_password = User.query.filter_by(password=password).first()
        
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')
        if not user:
            return render_template('login.html', username_error="Username does not exist.")
        if not users_password:
            return render_template('login.html', password_error="Incorrect password.")
        else:
            flash('User password incorrect or user does not exist', 'error')

    return render_template('login.html')

@app.route("/signup", methods=['POST', 'GET'])                   # this second page is a registration page, using the "POST" method so info doesn't appear in URL
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        username_error = ""                                         # here you're creating an empty string for the username error to make it a variable
        password_error = ""
        verify_error = ""
    

        
        if not existing_user:
    #THIS IS FOR THE USERNAME ERROR
            if not 20 >= len(username) >= 3 or " " in username:         # if the username is greater than 20 characters or less than three, or there is a space                
                username_error = "Please enter a valid username. Username should be between 3-20 characters and cannot contain any spaces or periods."       # it will produce an error message

        #THIS IS FOR THE PASSWORD ERROR
            if not 20 >= len(password) >= 3 or " " in password:
                password_error = "Please enter a valid password. Password should be between 3-20 characters and cannot contain any spaces or periods."       

        #THIS IS FOR VERIFYING THE PASSWORD
            if verify != password:                                  
                verify_error = "Password does not match."
        #THIS IS IF USERNAME ALREADY EXISTS


            if not username_error and not password_error and not verify_error:
                existing_user = User.query.filter_by(username=username).first()
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                                                                                                    
                return redirect("/newpost?username={0}".format(username))                               
            else:

                return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error)   #otherwise, give the user the form with the username in tact
        else:
            username_error = "Username already taken."
            return render_template('signup.html',username_error=username_error)

    return render_template('signup.html')



@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/add-post', methods=['POST', 'GET'])                      #I am trying to get this to actually post the blogposts to the page, but no idea...
def addpost():
    if request.method == "POST":
        title = request.form['title']
        post = request.form['post']
        title_error = ''
        post_error = ''
        if not title:
            title_error = "please enter a title."
        if not post:
            post_error = "please enter some text."
        if not title_error and not post_error:
            owner = User.query.filter_by(username=session['username']).first()
            newpost = BlogPost(title, post, owner)
            db.session.add(newpost)
            db.session.commit()
            return redirect('/blog?id=' + str(newpost.id))
        else:
            return render_template('newpost.html', title_error=title_error, post_error=post_error)




if __name__ == '__main__':                                      #This will actually get the page to run
    app.run()