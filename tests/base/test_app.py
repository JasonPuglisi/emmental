"""Tests Flask web application functionality."""

import requests
import pytest
from bs4 import BeautifulSoup
from src.app import load_user
from src.db import connect_db, close_db
from src.user import User

TEST_USERS = ('User1', 'User2', 'User3')


@pytest.fixture(scope='module', autouse=True)
def remove_users():
    """Remove inserted users after tests."""
    yield 1
    connection = connect_db()
    for username in TEST_USERS:
        connection.cursor().execute('DELETE FROM Users WHERE username=%s',
                                    (username,))
    connection.commit()
    close_db(connection)


@pytest.mark.parametrize('username', [
    (TEST_USERS[0]),
    (TEST_USERS[1])
])
def test_load_user(username):
    """Ensure the load user function is properly creating users."""
    assert load_user(username) == User(username)


def test_unauthenticated_index():
    """Ensure unauthenticated user is presented with landing page."""
    response = requests.get('http://localhost/', timeout=3)

    html = BeautifulSoup(response.text, 'html.parser')
    assert html.select('.container .user-buttons .signup-button')
    assert html.select('.container .user-buttons .login-button')
    assert not html.select('.container .user-buttons .logout-button')


def test_unauthenticated_logout():
    """Ensure unauthenticated user cannot be logged out."""
    response = requests.get('http://localhost/logout', timeout=3)
    assert response.history[0].status_code == 302
    assert response.url == 'http://localhost/?next=%2Flogout'

    html = BeautifulSoup(response.text, 'html.parser')
    assert (html.select('.container .flash-messages p')[0].text ==
            'Please log in to access this page.')


@pytest.mark.parametrize('username, password, success', [
    (TEST_USERS[0], 'password', True),
    (TEST_USERS[1], 'Password123!', True),
    (TEST_USERS[2], '', False),
    (TEST_USERS[2] * 30, 'password', False),
    ('', 'password', False),
    ('', '', False)
])
def test_signup(username, password, success):
    """Ensure user can sign up."""
    response = requests.post('http://localhost/signup', timeout=3, data={
        'username': username, 'password': password
    })

    html = BeautifulSoup(response.text, 'html.parser')
    success_messages = html.select('.container .flash-messages .flash-success')
    assert bool(success_messages and success_messages[0].text ==
                'Account created.') == success


@pytest.mark.parametrize('username, password, success', [
    (TEST_USERS[0], 'password', True),
    (TEST_USERS[1], 'Password123!', True),
    (TEST_USERS[0], 'password1', False),
    (TEST_USERS[1], 'password', False),
    (TEST_USERS[2], 'password', False)
])
def test_login(username, password, success):
    """Ensure user can log in."""
    response = requests.post('http://localhost/login', timeout=3, data={
        'username': username, 'password': password
    })

    html = BeautifulSoup(response.text, 'html.parser')
    success_messages = html.select('.container .flash-messages .flash-success')
    assert bool(success_messages and success_messages[0].text ==
                'Login successful.') == success


@pytest.mark.parametrize('username, password, success', [
    (TEST_USERS[0], 'password', True),
    (TEST_USERS[0], 'password1', False)
])
def test_authenticated_index(username, password, success):
    """Ensure authenticated user is presented with content page."""
    session = requests.session()
    session.post('http://localhost/login', timeout=3, data={
        'username': username, 'password': password
    })
    response = session.get('http://localhost/', timeout=3)

    html = BeautifulSoup(response.text, 'html.parser')
    assert (bool(html.select('.container .user-buttons .logout-button')) ==
            success)
    assert (not html.select('.container .user-buttons .signup-button') ==
            success)
    assert (not html.select('.container .user-buttons .login-button') ==
            success)

@pytest.mark.parametrize('username, password, success', [
    (TEST_USERS[0], 'password', True),
    (TEST_USERS[0], 'password1', False)
])
def test_authenticated_logout(username, password, success):
    """Ensure authenticated user can be logged out."""
    session = requests.session()
    session.post('http://localhost/login', timeout=3, data={
        'username': username, 'password': password
    })
    response = session.get('http://localhost/logout', timeout=3)
    assert response.history[0].status_code == 302
    if success:
        assert response.url == 'http://localhost/'
    else:
        assert response.url == 'http://localhost/?next=%2Flogout'

    html = BeautifulSoup(response.text, 'html.parser')
    assert html.select('.container .user-buttons .signup-button')
    assert html.select('.container .user-buttons .login-button')
    assert not html.select('.container .user-buttons .logout-button')

@pytest.mark.parametrize('username, password, user_to_check, return_msg', [
    (TEST_USERS[0], 'password', TEST_USERS[0], 'User Exists!'),
    (TEST_USERS[0], 'password', "abcd", 'NO'),
    (TEST_USERS[0], 'password', TEST_USERS[0]+'\' OR \'1\'=\'1', 'User Exists!'),
])
def test_blind_sql_on_users_exist_page(username, password, user_to_check, return_msg):
    """ Test that blind sql statements occur on /user-exist page """
    session = requests.session()
    session.post('http://localhost/login', timeout=3, data={
        'username': username, 'password': password
    })
    response = session.get('http://localhost/', timeout=3)
    url_request = 'http://localhost/user-check/' + user_to_check
    response = session.get(url_request, timeout=3)
    #html = BeautifulSoup(response.text, 'html.parser')
    assert response.text == return_msg
