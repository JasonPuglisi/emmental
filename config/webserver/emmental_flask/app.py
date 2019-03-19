from flask import Flask, abort,request, render_template, flash, session, redirect, url_for
from . import user, db
import os
import bcrypt
#from flask_login import LoginManager

app = Flask(__name__)
# This key should be recreated for each instance. It should be kept secret.
app.secret_key = b'_5#y2jdshgngdhsyfjgbngjdQ8z\n\xec]/'
#login_manager = LoginManager()
#login_manager.init_app(app)

# True == Password matches username
# False == Passsword doesn't match username
def authenticate_user(username, password):
  return db.check_password(username, password)

"""
@login_manager.user_loader
def load_user(user_id):
  return User.get(user_id)
"""
@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  # error to flash
  errormsg = None 
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    # checks that usernames are safe and meet requirements
    if (db.username_validity_check(username)):
      # status: [good | bad ]
      if (authenticate_user(username, password)):
        # some session information needs to happen here
        #flash("User successfully authenticated!")
        return render_template('content.html')
      else:
        flash("Bad Username/Password.")
        errormsg = "Bad Username/Password."
        #abort(401)
    else:
      # bad username or password
      flash("Invalid Username/Password.")
      errormsg = "Invalid Username/Password"
  return render_template('auth/login.html', error=errormsg)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  # error to flash
  errormsg = None
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    # checks that username and password are safe and meet requirements
    if (db.username_validity_check(username) and db.password_validity_check(username, password)):
      # status: [good | bad ]
      check_bool = db.check_username(username)
      if check_bool == 'open':
        #hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())    
        #db.add_user(username, hashed)
        user.create_user(username, password)
        flash("User added Successfully")
        return render_template("content.html")
      else:
        flash("User already taken")
        errormsg = "User already taken."
    else:
      # username/password didn't meet the requirements
      errormsg = "Invalid Username/Password"
  return render_template('auth/signup.html', error=errormsg)

'''
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('/'))

  @app.errorhandler(404)
  def not_found_error(error):
      return render_template('404.html'), 404

  @app.errorhandler(500)
  def internal_error(error):
      db.session.rollback()
    return render_template('500.html'), 500
'''
