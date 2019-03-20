"""Base web application functionality."""

from flask import flash, Flask, redirect, render_template, request, url_for
from flask_login import (current_user, LoginManager, login_required,
                         login_user, logout_user)
from .user import (create_user, is_correct_credential_pair, is_user_created,
                   is_valid_username, is_valid_password, User)

APP = Flask(__name__)

# Secret key should be recreated for each production instance.
APP.secret_key = b'.S\xf1\x8e\x8a\x07R%1?\x91~\x94%\x11\xc5'

LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.init_app(APP)
LOGIN_MANAGER.login_view = 'index'


@LOGIN_MANAGER.user_loader
def load_user(user_id):
    """Load a user object with the specified user ID (username)."""
    return User(user_id)


@APP.route('/', methods=['GET'])
def index():
    """Route to the index page. Present login/landing page if
       unauthenticated."""
    if current_user.is_authenticated:
        # User is authenticated, present content page.
        return render_template('content.html')

    # User is unauthenticated, present landing/login page.
    return render_template('landing.html')


@APP.route('/signup', methods=['POST'])
def signup():
    """Handle signup attempt if posted."""
    username = request.form['username']
    password = request.form['password']

    if is_valid_username(username) and is_valid_password(username, password):
        # Username and password are valid, check if username is taken.
        if not is_user_created(username):
            # Username is not taken, attempt to create user.
            if create_user(username, password):
                # User was created, log in and redirect.
                login_user(User(username))
                flash('<span class="flash-success">Account created.</span>')
                return redirect(url_for('index'))

            # User was not created, prompt again.
            flash('<span class="flash-error">Error creating account.</span>')

        # Username is taken, prompt again.
        flash('<span class="flash-error">Username is taken.</span>')
        return redirect(url_for('index'))

    # Username and/or password is not valid, prompt again.
    flash('<span class="flash-error">Invalid username or password.</span>')
    return redirect(url_for('index'))


@APP.route('/login', methods=['POST'])
def login():
    """Handle login attempt if posted."""
    username = request.form['username']
    password = request.form['password']

    if is_correct_credential_pair(username, password):
        # Login attempt was successful, log user in and redirect.
        login_user(User(username))
        flash('<span class="flash-success">Login successful.</span>')
        return redirect(url_for('index'))

    # Login attempt was unsuccessful, prompt again.
    flash('<span class="flash-error">Invalid username or password.</span>')
    return redirect(url_for('index'))


@APP.route('/logout', methods=['GET'])
@login_required
def logout():
    """Handle logout if already logged in."""
    logout_user()
    return redirect(url_for('index'))
