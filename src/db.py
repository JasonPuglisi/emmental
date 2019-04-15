"""Contains functionality for interfacing with the database."""

import os
import uuid
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
    return bool(result and
                bcrypt.checkpw(password.encode(), result[0][0].encode()))


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


def get_user_id_db(username):
    """Get a user ID from a username."""
    connection = connect_db()
    cursor = connection.cursor(buffered=True)
    cursor.execute('SELECT userID from Users WHERE username=%s', (username,))
    result = cursor.fetchall()
    close_db(connection)
    # catches empty results
    if not result:
        return ""
    return bytes(result[0][0])


def save_video_db(video_id, extension, user_id):
    """Save a video reference to the database."""
    connection = connect_db()
    connection.cursor().execute(
        'INSERT INTO Content (contentID, extension, userID) VALUES (%s, %s, %s)',
        (video_id, extension, user_id))
    connection.commit()
    close_db(connection)
    return True


def delete_video_db(video_id):
    """Delete a video reference from the database."""
    connection = connect_db()
    connection.cursor().execute('DELETE FROM Content WHERE contentID=%s',
                                (video_id,))
    connection.commit()
    close_db(connection)
    return True


def get_video_list_db():
    """Get a list of all videos saved to the database."""
    connection = connect_db()
    cursor = connection.cursor(buffered=True)
    cursor.execute('SELECT contentID, extension, userID FROM Content')
    result = cursor.fetchall()
    close_db(connection)
    return result

def get_user_id_from_video(video_id):
    """Get user id (creator) based on the video_id """
    connection = connect_db()
    cursor = connection.cursor(buffered=True)
    cursor.execute('SELECT userID FROM Content WHERE contentID=%s', (video_id,))
    result = cursor.fetchall()
    close_db(connection)
    #returns the user_id, which is in row 0, column zero of result
    return bytes(result[0][0])

def db_query_usernames(query):
    """ Get db query for usernames"""
    error = ['[X] User Not Found']
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM Users WHERE username = '%s';" % query)
        results = cursor.fetchall()
        close_db(connection)
    except mysql.connector.Error:
        return error
    #returns the result of query from the database
    usernames = []
    for result in results:
        usernames.append(result[0])
    if usernames:
        return usernames
    return error

def db_query_videos_by_username(query):
    """Get videos list by username"""
    try:
        connection = connect_db()
        cursor = connection.cursor()
        outer_stm = "SELECT contentID from Content where userID="
        cursor.execute(outer_stm + "(SELECT userID FROM Users WHERE username = '%s');" % query)
        video_list = cursor.fetchall()
        close_db(connection)
    except mysql.connector.Error:
        return ["Database error"]
    videos = []
    for video in video_list:
        byte_entry = bytes(video[0])
        videos.append(uuid.UUID(bytes=byte_entry))
    if videos:
        return videos
    return ["No Videos Found"]

def db_does_user_exist_vulnerable(query):
    """Check if user did upload video"""
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("SELECT userID, username from Users where username= '%s';" % query)
        video_list = cursor.fetchall()
        close_db(connection)
    except mysql.connector.Error:
        return ['Database Query Error']
    if video_list:
        return "User Exists!"
    return "NO"
