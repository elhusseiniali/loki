import unittest
from loki import User


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(username="Test", email="test@test.com", password='cat')
        self.assertTrue(u._password is not None)

    def test_password_verification(self):
        u = User(username="Test", email="test@test.com", password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(username="Test", email="test@test.com", password='cat')
        u2 = User(username="Test2", email="test2@test.com", password='cat')
        self.assertTrue(u._password != u2._password)
