import json
import unittest

from loki import User, create_app, db, schemas
from loki.config import TestConfig


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(username="Test",
                 email="test@test.com",
                 password='cat')

        self.assertTrue(u._password is not None)

    def test_password_verification(self):
        u = User(username="Test",
                 email="test@test.com",
                 password='cat')

        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u1 = User(username="Test",
                  email="test@test.com",
                  password='cat')

        u2 = User(username="Test2",
                  email="test2@test.com",
                  password='cat')

        self.assertTrue(u1._password != u2._password)
