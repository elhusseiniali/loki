import json
import unittest

from loki import User, create_app, db, schemas


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

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

    def test_api_get_all_users(self):
        tester = self.app.test_client(self)

        user1 = User(username="user1",
                     email="user1@gmail.com",
                     password="1234")

        user2 = User(username="user2",
                     email="user2@gmail.com",
                     password="1234")

        db.session.add_all([user1, user2])
        db.session.commit()

        response = tester.get('http://127.0.0.1:5000/api/1/users/')
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['users'][0]['username'], 'user1')
        self.assertEqual(json_response['users'][0]['email'], 'user1@gmail.com')
        self.assertEqual(json_response['users'][1]['username'], 'user2')
        self.assertEqual(json_response['users'][1]['email'], 'user2@gmail.com')

    def test_api_get_user(self):
        tester = self.app.test_client(self)

        user1 = User(username="user1",
                     email="user1@gmail.com",
                     password="1234")

        db.session.add(user1)
        db.session.commit()

        response = tester.get('http://127.0.0.1:5000/api/1/users/user_id={}'
                              .format(user1.id))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['user']['username'], 'user1')
        self.assertEqual(json_response['user']['email'], 'user1@gmail.com')

        response = tester.get('http://127.0.0.1:5000/api/1/users/{}'
                              .format(110))
        self.assertEqual(response.status_code, 404)

    def test_api_post_user(self):
        tester = self.app.test_client(self)

        user1 = User(username="user1",
                     email="user1@gmail.com",
                     password="1234")

        response = tester.post('http://127.0.0.1:5000/api/1/users/'
                               f'?username={user1.username}'
                               f'&email={user1.email}'
                               f'&password={user1.password}')

        self.assertEqual(response.status_code, 201)
