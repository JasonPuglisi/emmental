"""Tests Flask web application authentication backend."""

from src import user


def test_user_creation():
    """tests creating a user, 'admin'"""
    test_username = "admin"
    test_password = "abcd123"
    assert user.create_user(test_username, test_password)


def test_user_exists():
    """tests if admin user was created"""
    assert user.is_correct_credential_pair("admin", "abcd123")


def test_bad_user():
    """tests with a bad password requirement"""
    test_username = 'admins'
    test_password = 'Admins'
    # password can't contain username, therefore this is invalid.
    assert not user.is_correct_credential_pair(test_username, test_password)
