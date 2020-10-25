import unittest

from loki import app


class FlaskTestCase(unittest.TestCase):
    def test_pages_load(self):
        tester = app.test_client(self)

        home = tester.get('/', content_type='html/text')
        self.assertEqual(home.status_code, 200)

        login = tester.get('/login', content_type='html/text')
        self.assertEqual(login.status_code, 200)


if __name__ == "__main__":
    unittest.main()
