from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:1234@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class BlogPost(db.Model):                                       #This is creating a table that will store the blog info
    id = db.Column(db.Integer, primary_key=True)                #This is setting up the id column and setting it as a primary key??
    title = db.Column(db.String(120))                           #This is setting a column in the table named title which will store the title for the blog post
    post = db.Column(db.String(5000))                              #This is setting up a Column which will store the content in the blogpost

    def __init__(self, title, post):                         #Not really sure what this does, but it initalizes the table I guess?
        self.title = title
        self.post = post

# username and password will be needed for Blogz
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120))
#     password = db.Column(db.String(120))

#     def __init__(self, email, password):
#         self.email = email
#         self.password = password


@app.route('/blog', methods=['GET', 'POST'])                        #This is setting up the main page for the web application
def index():
    
    post_id = str(request.args.get('id'))  
    mypost =  BlogPost.query.get(post_id)                                                 #This is setting a function so that the page works?
    posts = BlogPost.query.all()                              #I think this line pulls the info from the SQL table?

    return render_template('index.html', posts=posts, mypost=mypost)       #This will render the html template set for the index


@app.route('/newpost')                #This is another page, which is where the user will input their blog
def newpost():
    return render_template('newpost.html')


@app.route('/add-post', methods=['POST'])                      #I am trying to get this to actually post the blogposts to the page, but no idea...
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
            newpost = BlogPost(title=title, post=post)
            db.session.add(newpost)
            db.session.commit()
            return redirect('/blog?id={0}'.format(newpost.id))
        else:
            return render_template('newpost.html', title_error=title_error, post_error=post_error)




if __name__ == '__main__':                                      #This will actually get the page to run
    app.run()