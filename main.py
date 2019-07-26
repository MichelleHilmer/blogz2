from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "cheeseburgersaregood"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(350))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, password):
        self.name = name
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'name' not in session:
        return redirect('/login')

@app.route('/index', methods=['POST', 'GET'])
def index():
    
    users = User.query.all()



    return render_template('index.html', users=users)

def logged_in_user():
    owner = User.query.filter_by(name=session['name']).first()
    return owner

    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        password= request.form['password']
        verify = request.form['verify']

        password_error = ''
        verify_error = ''
        user_error = ''

        if len(password) <=0:
                password_error = 'Please enter a valid password.'
                password = ''
        
        if len(verify) <=0:
                verify_error = 'Please enter a valid password.'
                verify = ''

        if len(password) < 3 or len(password) >20:
                password_error = "Please enter a password between 3 and 20 characters."
                password = ''

        if len(verify) < 3 or len(verify) >20:
                verify_error = "Please enter a password between 3 and 20 characters."
                verify = ''

        if verify != password:
                verify_error = "Passwords dont match!"
                password = ''
                verify = ''
        
        if ' ' in password:
                password_error = 'Please enter a valid password'
                password = ''

        if ' ' in verify:
                verify_error = "Please enter a valid password."
                verify = ''

        
        if len(name) > 0:
                if ' ' in name:
                        user_error = 'Thats not a valid username.'
                        name = ''
                elif len(name) < 3 and len(name) > 20:
                        user_error = "Thats not a valid username."
                        name = ''

        existing_user = User.query.filter_by(name=name).first()

        if existing_user:
            user_error = "User already exist"
            name = ''

        if password_error or verify_error or user_error:
            return render_template('signup.html', password_error=password_error, user_error=user_error, verify_error=verify_error)    

        else:
            if not password_error and not verify_error and not user_error:
            
                if not existing_user:
                    new_user = User(name, password)
                    db.session.add(new_user)
                    db.session.commit()
                    session['name'] = name

                    return redirect('/newpost')
        

        
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=name).first()

        password_error = ''
        user_error = ''

        if user and user.password == password:
            session['name'] = name
            return redirect('/newpost')

        elif not user:
            user_error = "Username doesn't exist."
            name = ''
            return render_template('login.html', user_error=user_error)

        else:
            if password == '' or password != user.password:
                password_error = "make sure you entered the right password"
                password= ''
                return render_template('login.html', password_error=password_error, user=user)
            
        return render_template('login.html', name=name, password=password, user_error=user_error, password_error=password_error)


    return render_template('login.html')

@app.route("/singleUser", methods=['POST','GET'])
def singleUser():
    users = User.query.filter_by(name=session['name']).first()
    user_id = request.args.get('id')
    blogz = Blog.query.filter_by(owner_id=user_id).all()

    return render_template('singleUser.html', blogz=blogz)




@app.route("/blog", methods=['POST', 'GET'])
def blog():
    blog_entries = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('name')

    if blog_id == None:
        blog_entries = Blog.query.all()
        return render_template('blog.html', blog_entries=blog_entries)

    elif blog_id:
        new_entry = Blog.query.filter_by(id=user_blog).first()
        return render_template('post.html', new_entry=new_entry)

    else:
        if user_id:
            users = User.query.filter_by(name=session['name']).first()
            user_id = request.args.get('id')
            blogz = Blog.query.filter_by(owner_id=user_id).all()
            return render_template('singleUser.html', blogz=blogz)

    return render_template('blog.html', blog_entries=blog_entries, name=name)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(name=session['name']).first()

    if request.method == "POST":
        title_post = request.form['title_post']
        blog_body = request.form['blog_body']
        title_error = ''
        body_error = ''

        if len(title_post) <= 0 :
            title_error = 'Please enter a blog title.'
            title_post = ''

        if len(blog_body) < 1 :
            body_error = 'Please enter a blog entry.'
            blog_body = ''


        if not title_error and not body_error:
            owner = User.query.filter_by(name=session['name']).first()
            new_entry = Blog(title_post, blog_body, owner)
            db.session.add(new_entry)
            db.session.commit()

            return render_template('post.html', new_entry=new_entry)

        else:
            return render_template('newpost.html', title_post=title_post, blog_body=blog_body, title_error=title_error,
            body_error=body_error)

    return render_template('newpost.html')

@app.route('/logout')
def logout():
    del session['name']
    return redirect('/blog')






if __name__ == "__main__":
    app.run()
