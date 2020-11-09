import unittest

from loki import app


class FlaskTestCase(unittest.TestCase):
    def test_pages_load(self):
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


if __name__ == "__main__":
    unittest.main()
