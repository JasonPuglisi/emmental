from config.webserver.emmental_flask.user import create_user
from config.webserver.emmental_flask.app import authenticate_user
from config.webserver.emmental_flask.db import password_validity_check

class TestClass(object):
    # tests creating a user, 'admin'
    def test_user_creation(self):
        test_username = "admin"
        test_password = "abcd123"
        if (create_user(test_username, test_password)):
            assert True
        else:
            assert False
    # tests if admin user was created
    def test_user_exists(self):
        if(authenticate_user("admin", "abcd123")):
            assert True
        else:
            assert False
    # tests with a bad password requirement
    def test_bad_user(self):
        test_username = 'admins'
        test_password = 'Admins'
        # password can't contain username, therefore this is invalid.
        assert not password_validity_check(test_username, test_password)
