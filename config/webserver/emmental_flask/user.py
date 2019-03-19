import bcrypt
import os
from . import db
'''
# user functions need to exist here, : logoin,out, password setting, etc.
class ClassName(object):
    def __init__(self, *args):
        super(ClassName, self).__init__(*args))
'''
# Input: plaintext username & password
# create_user creates user by inserting username, hashing password, and storing in DB.
# Output: Status code of creation {True=Success | False=Failure}
def create_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db.add_user(username, hashed)
    if(db.check_username(username) == "exists"):
        if(db.check_password(username, password)):
            return True
        else:
            return False
    else:
        return False

