"""Tests MariaDB interfacing functionality."""

import uuid
import bcrypt
import pytest
from src.db import (close_db, connect_db, create_user_db, is_user_created_db,
                    get_user_id_db, is_valid_credential_pair_db, save_video_db,
                    delete_video_db, db_query_usernames)

TEST_USERS = [
    ('User1', 'password1'),
    ('User2', 'password2'),
    ('User3', 'password3')
]

TEST_CREDENTIAL_PAIRS = [
    (TEST_USERS[0][0], TEST_USERS[0][1], True),
    (TEST_USERS[0][0], TEST_USERS[0][1] * 2, False),
    (TEST_USERS[0][0] * 2, TEST_USERS[0][1], False)
]


@pytest.fixture(scope='module', autouse=True)
def arrange_users():
    """Insert and remove users before and after tests."""
    connection = connect_db()
    for user in TEST_USERS:
        user_id = uuid.uuid4().bytes
        username = user[0]
        password_hash = bcrypt.hashpw(user[1].encode(), bcrypt.gensalt())
        connection.cursor().execute(
            'INSERT INTO Users (userID, username, password) VALUES (%s, %s, %s)',
            (user_id, username, password_hash))
    connection.commit()
    yield 1
    for user in TEST_USERS:
        user_id = uuid.uuid4().bytes
        username = user[0]
        connection.cursor().execute('DELETE FROM Users WHERE username=%s',
                                    (username,))
    connection.commit()
    close_db(connection)

@pytest.fixture(name='prepare_create_user')
def prepare_create_user_db():
    """Clear a user from the database to be created."""
    username = TEST_USERS[0][0]
    connection = connect_db()
    connection.cursor().execute('DELETE FROM Users WHERE username=%s',
                                (username,))
    connection.commit()
    close_db(connection)
    return username


def test_connect_db():
    """Ensure app can connect to the database."""
    connection = connect_db()
    assert connection.is_connected()
    close_db(connection)


def test_close_db():
    """Ensure connection to the database can be closed."""
    connection = connect_db()
    close_db(connection)
    assert not connection.is_connected()


@pytest.mark.parametrize('username, password, success', TEST_CREDENTIAL_PAIRS)
def test_is_valid_credential_pair_db(username, password, success):
    """Ensure user credentials are properly validated."""
    assert is_valid_credential_pair_db(username, password) == success


@pytest.mark.parametrize('username, success', [
    (TEST_USERS[0][0], True),
    (TEST_USERS[1][0], True),
    (TEST_USERS[0][0] * 2, False)
])
def test_is_user_created_db(username, success):
    """Ensure a user is properly determined to exist in the database."""
    assert is_user_created_db(username) == success


def test_create_user_db(prepare_create_user):
    """Ensure a user is correctly created in the database."""
    user_id = uuid.uuid4().bytes
    username = prepare_create_user
    password_hash = bcrypt.hashpw(TEST_USERS[0][1].encode(), bcrypt.gensalt())
    create_user_db(user_id, username, password_hash)
    assert is_user_created_db(username)

def test_get_user_id_db(prepare_create_user):
    """Ensure that a username maps to a user_id correctly. """
    user_id = uuid.uuid4().bytes
    username = prepare_create_user
    password_hash = bcrypt.hashpw(TEST_USERS[0][1].encode(), bcrypt.gensalt())
    create_user_db(user_id, username, password_hash)
    assert get_user_id_db(username) == user_id


@pytest.mark.parametrize('video_id, user_id, extension, success', [
    (uuid.uuid4().bytes, uuid.uuid4().bytes, 'mp4', True),
    (uuid.uuid4().bytes, uuid.uuid4().bytes, 'ogg', True),
])
def test_save_video_db(video_id, user_id, extension, success):
    """ Tests save_video_db() functionality """
    assert save_video_db(video_id, extension, user_id) == success
    assert delete_video_db(video_id) == success

@pytest.mark.parametrize('username, response', [
    (TEST_USERS[0][0], [TEST_USERS[0][0]]),
    ('FakeUser', ['[X] User Not Found']),
    ('', ['[X] User Not Found']),
    ('\' or \'1\'=\'1', ['User1', 'User2', 'User3']),
    ])
def test_db_search_users(username, response):
    """ Test that users are searchable in db """
    arrange_users()
    assert db_query_usernames(username) == response
