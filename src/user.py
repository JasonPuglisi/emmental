"""This module contains functionality for creating application users."""

import uuid
import bcrypt
from flask_login import UserMixin
from .db import create_user_db, is_user_created_db, is_valid_credential_pair_db


class User(UserMixin):
    """Simple user object containing a user ID (username)"""

    def __init__(self, user_id):
        self.user_id = user_id

    def get_id(self):
        return self.user_id


def is_valid_username(username):
    """Ensure username meets requirements. Returns True if successful."""
    return bool(username and username.isalnum() and len(username) <= 30)


def is_valid_password(username, password):
    """Ensure password meets requirements. Returns True if successful."""
    return bool(password and username.lower() not in password.lower() and
                len(password) <= 72)


def is_correct_credential_pair(username, password):
    """Ensure username and password are valid/correct. Returns True if
       successful."""
    return bool(is_valid_username(username) and
                is_valid_password(username, password) and
                is_valid_credential_pair_db(username, password))


def is_user_created(username):
    """Ensure user exists. Returns True if successful."""
    return is_user_created_db(username)


def create_user(username, password):
    """Create a user and insert it into the database. Returns True if
       successful."""
    if (is_valid_username(username) and is_valid_password(username, password)
            and not is_user_created_db(username)):
        user_id = uuid.uuid4().bytes
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return create_user_db(user_id, username, password_hash)
    return False
