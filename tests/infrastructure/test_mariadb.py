"""Tests the MariaDB infrastructure."""

import os
import uuid
import bcrypt
import mysql.connector
import pytest


@pytest.fixture(scope='module', name='connection')
def db_connection():
    """Connects to the database."""
    connection = mysql.connector.connect(
        host=os.environ['MARIADB_IP'],
        user=os.environ['MARIADB_USER'],
        password=os.environ['MARIADB_PASSWORD'],
        database=os.environ['MARIADB_DATABASE'])
    connection.cursor(buffered=True).execute(
        'USE %s' % os.environ['MARIADB_DATABASE'])
    yield connection
    connection.close()


def test_connectable(connection):
    """Ensure that the machine can connect to the database."""
    assert connection.is_connected()


def test_db_created(connection):
    """Ensure that the database has been created."""
    database = 'emmental'

    cursor = connection.cursor(buffered=True)
    cursor.execute(
        'SELECT 1 FROM information_schema.schemata WHERE schema_name=%s',
        (database,))
    result = cursor.fetchall()
    assert result


@pytest.mark.parametrize('user_id, username, password, success', [
    ('00000000-0000-0000-0000-000000000000', 'User1', 'password', True),
    ('0b00fb30-fade-4890-9617-4f988a7f3d74', 'User2', 'password123!', True),
    ('fabda83c-ed59-48bb-be78-64a0a7807814', 'a' * 31, 'password', False),
    ('71b4adf1-aa88-426e-af0d-438ae29fd9af', 'User1', 'password', False),
    ('00000000-0000-0000-0000-000000000000', 'User3', 'password', False),
    ('e125f968-9421-489b-8132-4ae3132df6a2', '', 'password', False),
    ('36b33634-ea16-481b-9944-67f1a042b90e', 'User4', '', False)
])
def test_db_insertion(connection, user_id, username, password, success):
    """Ensure that data can be inserted into the database."""
    user_id = uuid.UUID(user_id).bytes
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute(
            'INSERT INTO Users (userID, username, password) VALUES (%s, %s, %s)',
            (user_id, username, password_hash))
        connection.commit()
    except (mysql.connector.IntegrityError, mysql.connector.DataError):
        assert not success


@pytest.mark.parametrize('username, success', [
    ('User1', True),
    ('User2', True),
    ('User3', False)
])
def test_db_read(connection, username, success):
    """Ensure that data can be read from the database."""
    cursor = connection.cursor(buffered=True)
    cursor.execute('SELECT 1 FROM Users WHERE username=%s LIMIT 1',
                   (username,))
    result = cursor.fetchall()
    assert bool(result) == success


@pytest.mark.parametrize('username, success', [
    ('User1', True),
    ('User2', True),
    ('User3', False)
])
def test_db_deletion(connection, username, success):
    """Ensure that data can be deleted from the database."""
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute('DELETE FROM Users WHERE username=%s', (username,))
        connection.commit()
    except mysql.connector.DataError:
        assert not success
