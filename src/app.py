"""Base web application functionality."""

import ipaddress
import re
import requests
from flask import (flash, Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_login import (current_user, LoginManager, login_required,
                         login_user, logout_user)
from .user import (create_user, get_user_id, is_correct_credential_pair, is_user_created,
                   is_valid_username, is_valid_password, User)
from .video import (delete_select_video, get_extension, get_user_id_from_video_id,
                    get_video_list, is_valid_filename, Video)

APP = Flask(__name__)

# Secret key should be recreated for each production instance.
APP.secret_key = b'.S\xf1\x8e\x8a\x07R%1?\x91~\x94%\x11\xc5'
APP.upload_folder = '/srv/videos/'

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
        # Get the current user's user_id, if its empty, send an empty string
        active_user = str(get_user_id(current_user.user_id))
        return render_template('content.html', videos=get_video_list(), signed_in=active_user)

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


@APP.route('/upload', methods=['GET'])
@login_required
def upload():
    """Allow user to upload videos via local file and URL."""
    return render_template('upload.html')

@APP.route('/delete/<path:videopath>')
@login_required
def delete_video(videopath):
    """ Deletes a video if it was uploaded by the same user. """
    if videopath:
        # stores user_id derived from username
        user_request_id = str(get_user_id(current_user.user_id))
        # splitting filename from file extension
        spliter = videopath.split(".")
        # filename/videoID is first element in array spliter
        video_id = spliter[0]
        # gets owner/user_id from video selected for deletion
        video_owner_id = str(get_user_id_from_video_id(video_id))
        # Checking if user requesting to delete video also uploaded it
        if user_request_id == video_owner_id:
            delete_select_video(videopath)
            flash('<span class="flash-success">Video deleted successfully.</span>')
        else:
            flash('<span class="flash-error">User can not delete this.</span>')
    else:
        flash('<span class="flash-error">No Video specified to delete.</span>')
    return redirect(url_for('index'))

@APP.route('/upload/file', methods=['POST'])
@login_required
def upload_file():
    """Handle local file upload if provided."""
    no_file = '<span class="flash-error">No file selected.</span>'
    if 'video' not in request.files:
        flash(no_file)
        return redirect(url_for('upload'))

    file = request.files['video']
    if not file or file.filename == '':
        flash(no_file)
        return redirect(url_for('upload'))

    filename = file.filename
    if not is_valid_filename(filename):
        flash('<span class="flash-error">Invalid file selected.</span>')
        return redirect(url_for('upload'))

    video = Video()
    video.create(filename, current_user.user_id)
    video.save()
    file.save(video.get_path(APP.upload_folder))
    flash('<span class="flash-success">Video uploaded successfully.</span>')
    return redirect(url_for('index'))


@APP.route('/upload/url', methods=['POST'])
@login_required
def upload_url():
    """Handle URL upload if provided."""
    no_url = '<span class="flash-error">No URL specified.</span>'
    url = request.form['url'] if 'url' in request.form else ''
    if not url:
        flash(no_url)
        return redirect(url_for('upload'))

    invalid_url = '<span class="flash-error">Invalid URL specified.<span>'
    pattern = re.compile(r'^(http(?:s)?):\/\/(.*?)(?::(\d{0,5}))?(\/[^\?]*)?(?:\?(.*))?$',
                         re.IGNORECASE)
    result = pattern.match(url)

    if not url or not result:
        flash(invalid_url)
        return redirect(url_for('upload'))

    #protocol = result.group(1)
    host = result.group(2)
    #port = result.group(3)
    path = result.group(4)
    parameters = result.group(5)

    # Ensure host is not just an IP address (should throw exception)
    try:
        ipaddress.ip_address(host)
        flash(invalid_url)
        return redirect(url_for('upload'))
    except ValueError:
        pass

    if host.lower() == 'localhost' or '.' not in host:
        flash(invalid_url)
        return redirect(url_for('upload'))

    video = Video()
    if path and get_extension(path):
        video.create(path, current_user.user_id)
    elif parameters and get_extension(parameters):
        video.create(parameters, current_user.user_id)
    else:
        flash(invalid_url)
        return redirect(url_for('upload'))

    video.save()
    response = requests.get(url)
    with open(video.get_path(APP.upload_folder), 'wb') as file:
        file.write(response.content)

    flash('<span class="flash-success">Video uploaded successfully.</span>')
    return redirect(url_for('index'))


@APP.route('/video/<path:filename>')
@login_required
def static_video(filename):
    """Serve static video file."""
    return send_from_directory(APP.upload_folder, filename)


@APP.route('/view/<path:videopath>')
@login_required
def video_player_page(videopath):
    """Serve video player page to user"""
    extension = get_extension(videopath)
    return render_template('video_player.html', video=videopath, ext=extension)
