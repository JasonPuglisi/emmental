"""Test user handling functionality."""

import pytest
from src.user import (create_user, is_correct_credential_pair, is_user_created,
                      is_valid_password, is_valid_username, User)
from .test_db import (arrange_users, prepare_create_user_db,  # pylint: disable=unused-import
                      TEST_CREDENTIAL_PAIRS, TEST_USERS)


def test_user_class():
    """Ensure User class is created and returns information correctly."""
    username = '1234'
    user = User(username)
    assert user.get_id() == username


@pytest.mark.parametrize('username, success', [
    ('User', True),
    ('1234', True),
    ('Ab12', True),
    ('a' * 30, True),
    ('', False),
    ('Abc!', False),
    ('ab d', False),
    ('a' * 31, False)
])
def test_is_valid_username(username, success):
    """Ensure usernames are properly validated."""
    assert is_valid_username(username) == success


@pytest.mark.parametrize('username, password, success', [
    ('User', 'Password', True),
    ('User', 'Pa s12!@', True),
    ('User', 'a' * 72, True),
    ('User', '', False),
    ('User', 'user123', False),
    ('User', 'a' * 73, False)
])
def test_is_valid_password(username, password, success):
    """Ensure usernames are properly validated."""
    assert is_valid_password(username, password) == success


@pytest.mark.parametrize('username, password, success', TEST_CREDENTIAL_PAIRS)
def test_is_correct_credential_pair(username, password, success):
    """Ensure user credentials are properly validated."""
    assert is_correct_credential_pair(username, password) == success


@pytest.mark.parametrize('username, success', [
    (TEST_USERS[0][0], True),
    (TEST_USERS[0][0] * 2, False)
])
def test_is_user_created(username, success):
    """Ensure a user is properly determined to exist."""
    assert is_user_created(username) == success


def test_create_user_db(prepare_create_user):
    """Ensure a user is correctly created."""
    username = prepare_create_user
    password = TEST_USERS[0][1]
    create_user(username, password)
    assert is_user_created(username)
