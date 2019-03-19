import mysql.connector, os
import bcrypt

# get reference to connected DB
def get_db():
    return connect_db()
# connect to db
def connect_db():
  dbconnection = mysql.connector.connect(host=os.environ['MARIADB_IP'], user='databaseuser', password='securedatabasepassword', database='emmental')
  if dbconnection:
    print("SUCCESS")
  if not dbconnection:
    print("FAILURE")
  return dbconnection

# close db connection
def close_db(dbconnection):
  dbconnection.close()

#make a 'select' type query - must not be destructive. Does not commit to db.
def query(sqlquery):
  dbconnection = get_db()
  cursor = dbconnection.cursor()
  cursor.execute("use emmental;")
  cursor.execute(sqlquery)
  close_db(dbconnection)
  for result in cursor:
    print(result)

# insert/add user into mariadb
def add_user(username, password):
  dbconnection = get_db()
  userID = generate_userID()
  cursor = dbconnection.cursor()
  dbusername = username
  cursor.execute("INSERT INTO Users (userID, username, password) VALUES (%s,%s,%s)", (userID, dbusername, password))
  dbconnection.commit()
  close_db(dbconnection)
  #result = cursor.fetchone() -  could add a check here that "1 row" was affected
  if check_username(username) == "exists":
    return "success"
  else:
    return "fail"

# checks if username input meets requirements
# True == valid and meets requirements, False does not
def username_validity_check(username):
  # usernames must be alphanumeric and 30 chars or less, but also not empty.
  if ((username.isalnum()) and (len(username) < 31) and (len(username) > 0)):
      return True
  else:
    return False


# check if password input meets requirements
# True == valid and meets requirement, False does not
def password_validity_check(username, password):
  if ((len(password) > 0) and (username.lower() not in password.lower()) and (len(password) < 73)):
    return True
  else:
    return False

# retrieves username status
def check_username(username):
  dbconnection = get_db()
  cursor = dbconnection.cursor()
  dbusername = username
  cursor.execute("SELECT * FROM Users WHERE username=%s", (dbusername,))
  username_check = cursor.fetchone()
  close_db(dbconnection)
  if not username_check:
    return "open"
  else:
    return "exists"

# checks password is valid for username
def check_password(username, password):
  dbconnection = get_db()
  cursor = dbconnection.cursor()
  cursor.execute("SELECT password FROM Users WHERE (username=%s)", (username,))
  password_check = cursor.fetchone()
  close_db(dbconnection)
  if not password_check:
    return False
  elif bcrypt.checkpw(password.encode(), password_check[0].encode()):
        return True
  else:
    return False

# generate and return unique userID
def generate_userID():
  dbconnection = get_db()
  cursor = dbconnection.cursor()
  query = 'SELECT UUID();'
  cursor.execute(query)
  user_id_tuple = cursor.fetchone()
  close_db(dbconnection)
  if not user_id_tuple:
    return "error"
  return str(user_id_tuple[0])
