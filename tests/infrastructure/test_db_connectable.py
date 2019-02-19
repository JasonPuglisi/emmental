import mysql.connector
import os

class TestClass(object):
  def test_connectable(self):
    dbconnection = mysql.connector.connect(host=os.environ['MARIADB_IP'], user='databaseuser', password='securedatabasepassword', database='emmental')
    dbconnection.close()

  def test_db_created(self):
    dbconnection = mysql.connector.connect(host=os.environ['MARIADB_IP'], user='databaseuser', password='securedatabasepassword', database='emmental')
    cursor = dbconnection.cursor()
    query = ('select 1 from information_schema.schemata where schema_name="emmental"')
    cursor.execute(query)
    results = 0
    for result in cursor:
      results += 1
    assert results == 1
    dbconnection.close()

  def test_db_insertion(self):
    dbconnection = mysql.connector.connect(host=os.environ['MARIADB_IP'], user='databaseuser', password='securedatabasepassword', database='emmental')
    cursor = dbconnection.cursor()
    query = ('use emmental;')
    cursor.execute(query)
    query = ('INSERT Users VALUES("1", "user1", "password1");')
    cursor.execute(query)
    query = ('SELECT * FROM Users WHERE userID="1";')
    cursor.execute(query)
    results = 0
    for result in cursor:
        results += 1
    assert results == 1
    dbconnection.close()
  def test_db_deletion(self):
    dbconnection = mysql.connector.connect(host=os.environ['MARIADB_IP'], user='databaseuser', password='securedatabasepassword', database='emmental')
    cursor = dbconnection.cursor()
    query = ('use emmental;')
    cursor.execute(query)
    query = ('DELETE FROM Users WHERE userID="1";')
    cursor.execute(query)
    query = ('SELECT * FROM Users WHERE userID="1";')
    cursor.execute(query)
    results = 0
    for result in cursor:
        results += 1
    assert results == 0
    dbconnection.close()
