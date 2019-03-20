"""This module tests the database container and infrastructure."""

import os
import uuid
import mysql.connector

TEST_USER_ID = uuid.uuid4().bytes

def test_connectable():
    """Ensure that the machine can connect to the database."""
    dbconnection = mysql.connector.connect(
        host=os.environ['MARIADB_IP'], user='databaseuser',
        password='securedatabasepassword', database='emmental')
    dbconnection.close()


def test_db_created():
    """Ensure that the database has been created."""
    dbconnection = mysql.connector.connect(
        host=os.environ['MARIADB_IP'], user='databaseuser',
        password='securedatabasepassword', database='emmental')
    cursor = dbconnection.cursor()
    query = (
        'select 1 from information_schema.schemata where schema_name="emmental"')
    cursor.execute(query)
    results = 0
    for _ in cursor:
        results += 1
    assert results == 1
    dbconnection.close()


def test_db_insertion():
    """Ensure that data can be inserted into the database."""
    dbconnection = mysql.connector.connect(
        host=os.environ['MARIADB_IP'], user='databaseuser',
        password='securedatabasepassword', database='emmental')
    cursor = dbconnection.cursor()
    query = ('use emmental;')
    cursor.execute(query)
    query = ('INSERT Users VALUES(%s, "user1", "password1");')
    cursor.execute(query, (TEST_USER_ID,))
    query = ('SELECT * FROM Users WHERE userID=%s;')
    cursor.execute(query, (TEST_USER_ID,))
    results = 0
    for _ in cursor:
        results += 1
    assert results == 1
    dbconnection.close()


def test_db_deletion():
    """Ensure that data can be deleted from the database."""
    dbconnection = mysql.connector.connect(
        host=os.environ['MARIADB_IP'], user='databaseuser',
        password='securedatabasepassword', database='emmental')
    cursor = dbconnection.cursor()
    query = ('use emmental;')
    cursor.execute(query)
    query = ('DELETE FROM Users WHERE userID=%s;')
    cursor.execute(query, (TEST_USER_ID,))
    query = ('SELECT * FROM Users WHERE userID=%s;')
    cursor.execute(query, (TEST_USER_ID,))
    results = 0
    for _ in cursor:
        results += 1
    assert results == 0
    dbconnection.close()
