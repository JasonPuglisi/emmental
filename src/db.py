"""Contains functionality for interfacing with the database."""

import os
import bcrypt
import mysql.connector


def connect_db():
    """Create a connection to MariaDB."""
    dbconnection = mysql.connector.connect(
        host=os.environ['MARIADB_IP'],
        user=os.environ['MARIADB_USER'],
        password=os.environ['MARIADB_PASSWORD'],
        database=os.environ['MARIADB_DATABASE'])
    return dbconnection


def close_db(dbconnection):
    """Close connection to MariaDB."""
    dbconnection.close()


def is_valid_credential_pair_db(username, password):
    """Ensures credential pair exists in the database. Returns True if
       successful."""
    connection = connect_db()
    cursor = connection.cursor(buffered=True)
    cursor.execute('SELECT password FROM Users WHERE username=%s LIMIT 1',
                   (username,))
    result = cursor.fetchall()
    close_db(connection)
    return result and bcrypt.checkpw(password.encode(), result[0][0].encode())


def is_user_created_db(username):
    """Ensure user exists in the database. Returns True if successful."""
    connection = connect_db()
    cursor = connection.cursor(buffered=True)
    cursor.execute('SELECT 1 FROM Users WHERE username=%s LIMIT 1',
                   (username,))
    result = cursor.fetchall()
    close_db(connection)
    return bool(result)


def create_user_db(user_id, username, password_hash):
    """Create a user in the database with the specified details. Returns True
       if successful."""
    connection = connect_db()
    connection.cursor().execute(
        'INSERT INTO Users (userID, username, password) VALUES (%s, %s, %s)',
        (user_id, username, password_hash))
    connection.commit()
    close_db(connection)
    return is_user_created_db(username)
