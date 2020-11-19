import unittest

from loki import app, db


class Helper():
    """Class with useful functions for testing.
    """
    def register(app, username, email, password, confirm_password):
        """Register a new user.
        """
        return app.post(
            '/register',
            data=dict(username=username,
                      email=email,
                      password=password, confirm_password=confirm_password),
            follow_redirects=True
        )

    def login(app, email, password):
        """Attempt to log a user in.
        """
        return app.post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def logout(app):
        """Attempt to log out.
        """
        return app.get(
            '/logout',
            follow_redirects=True
        )


class FlaskTestCase(unittest.TestCase):
    def test_pages_load(self):
        """Test that pages load correctly.
        """
        tester = app.test_client(self)

        home = tester.get('/', content_type='html/text')
        self.assertEqual(home.status_code, 200)

        login = tester.get('/login', content_type='html/text')
        self.assertEqual(login.status_code, 200)

        register = tester.get('/register', content_type='html/text')
        self.assertEqual(register.status_code, 200)

        account = tester.get('/account', content_type='html/text')
        #   Can't access account page without valid login
        self.assertEqual(account.status_code, 302)

    def test_auth(self):
        # This test always works, even when it shouldn't!!!
        # See issue #18
        tester = app.test_client(self)

        db.drop_all()
        db.create_all()

        valid_registration = Helper.register(tester, username="frege",
                                             email="frege@gmail.com",
                                             password="whereisrussell",
                                             confirm_password="whereisrussell")
        self.assertEqual(valid_registration.status_code, 200)

        valid_login = Helper.login(tester, email="frege@gmail.com",
                                   password="whereisrussell")
        self.assertEqual(valid_login.status_code, 200)

        # invalid_login = Helper.login(tester, email="russell@gmail.com",
        #                             password="fregewasagenius")
        # self.assertIn(b'Login unsuccessful!.', invalid_login.data)
        # self.assertEqual(invalid_login.status_code, 200)


if __name__ == "__main__":
    unittest.main()
