import unittest

from flask_testing import TestCase
from flask_login import current_user

from loki import create_app, db
from loki.config import TestConfig
from loki.models import User


class BaseTestCase(TestCase):
    """A base test case.

    If you don’t define create_app a NotImplementedError will be raised.
    """

    def create_app(self):
        return create_app(TestConfig)

    def setUp(self):
        db.create_all()
        db.session.add(
            User(username="admin", email="ad@min.com", password="admin")
        )
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class FlaskTestCase(BaseTestCase):
    """A test case for all actions made by a non-authenticated client"""

    # Ensure home behaves correctly when non-authenticated
    def test_home(self):
        response = self.client.get('/home', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('home.html')
        self.assert_context("title", "Home")

    # Ensure about behaves correctly when non-authenticated
    def test_about(self):
        response = self.client.get('/about', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('about.html')
        self.assert_context("title", "About")

    # Ensure login behaves correctly when non-authenticated
    def test_login(self):
        response = self.client.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')
        self.assert_context("title", "Log in")

    # Ensure register behaves correctly when non-authenticated
    def test_register(self):
        response = self.client.get('/register', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('register.html')
        self.assert_context("title", "Register")

    # Ensure account behaves correctly when non-authenticated
    def test_account(self):
        response = self.client.get(
            '/account', content_type='html/text', follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')
        self.assert_context("title", "Log in")
        self.assertIn(b'Please log in to access this page.', response.data)

    # Ensure logout behaves correctly when non-authenticated
    def test_logout(self):
        response = self.client.get(
            '/logout', content_type='html/text', follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('home.html')
        self.assert_context("title", "Home")

    # Ensure 'Launch a report' behaves correctly when non-authenticated
    def test_reports_new(self):
        response = self.client.get(
            '/reports/new', content_type='html/text', follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')
        self.assert_context("title", "Log in")
        self.assertIn(b'Please log in to access this page.', response.data)

    # Ensure 'Classify an image' behaves correctly when non-authenticated
    def test_classifiers_classify(self):
        response = self.client.get(
            '/classifiers/classify',
            content_type='html/text',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')
        self.assert_context("title", "Log in")
        self.assertIn(b'Please log in to access this page.', response.data)

    # Ensure 'Visualize Attack' behaves correctly when non-authenticated
    def test_attacks_visualize(self):
        response = self.client.get(
            '/attacks/visualize', content_type='html/text',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')
        self.assert_context("title", "Log in")
        self.assertIn(b'Please log in to access this page.', response.data)


class LoginAndOutTests(BaseTestCase):
    """A test case for actions on the login and logout route"""

    # Ensure login behaves correctly with empty password
    def test_incorrect_login_password_empty(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="valid@email.com", password=""),
                follow_redirects=True
            )
            self.assertIn(b'This field is required.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    # Ensure login behaves correctly with correct credentials
    def test_correct_login(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin"),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(current_user.is_active)
            self.assertTrue(current_user.is_authenticated)

    # Ensure login behaves correctly with invalid credentials
    def test_incorrect_login(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="wrong@gmail.com", password="wrong"),
                follow_redirects=True
            )
            self.assertIn(b'Login unsuccessful!', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    # Ensure logout behaves correctly
    def test_logout(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin"),
                follow_redirects=True
            )
            response = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)


class RegisterTests(BaseTestCase):
    """A test case for actions on the register route"""

    # Ensure login behaves correctly with empty username
    def test_incorrect_register_username_empty(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="", email="test@gmail.com", password="test",
                    confirm_password="test"
                )
            )
            self.assertIn(b'This field is required.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    # Ensure login behaves correctly with empty password
    def test_incorrect_register_password_empty(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email="test@gmail.com", password="",
                    confirm_password="test"
                )
            )
            self.assertIn(b'This field is required.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    # Ensure login behaves correctly with empty confirm password
    def test_incorrect_register_confirm_empty(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email="test@gmail.com", password="test",
                    confirm_password=""
                )
            )
            self.assertIn(b'This field is required.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    # Ensure login behaves correctly with too short username
    def test_invalid_register_username(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="t", email="test@gmail.com", password="test",
                    confirm_password="test"
                )
            )
            self.assertIn(
                b'Field must be between 2 and 15 characters long.',
                response.data
            )
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    # Ensure login behaves correctly with confirm password different
    def test_invalid_register_confirm(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email="test@gmail.com", password="test",
                    confirm_password="test2"
                )
            )
            self.assertIn(b'Field must be equal to password.', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    # Ensure login behaves correctly with username already existing
    def test_invalid_register_username_old(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="admin", email="test@gmail.com", password="test",
                    confirm_password="test"
                )
            )
            self.assertIn(b'Username already exists!', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    # Ensure login behaves correctly with email already existing
    def test_invalid_register_email_old(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email="ad@min.com", password="test",
                    confirm_password="test"
                )
            )
            self.assertIn(b'Account with email already exists!', response.data)
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)

    # Ensure register behaves correctly with correct credentials
    def test_correct_login(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    username="test", email="test@gmail.com", password="test",
                    confirm_password="test"
                ),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(
                b'Account created! You can now log in.', response.data
            )
            self.assertFalse(current_user.is_active)
            self.assertFalse(current_user.is_authenticated)


if __name__ == '__main__':
    unittest.main()
