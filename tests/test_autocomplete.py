import unittest
import os

from config import CONTENT_DIR

from wiki import create_app


class TestAutocomplete(unittest.TestCase):

    def test_toa(self):
        app = create_app(os.getcwd() + '../')
        with app.test_request_context():
            import wiki.web.routes as routes
            self.assertEquals("<a href='/toast'>Toast</a>", routes.autocomplete("toa"))

    def test_noresult(self):
        app = create_app(os.getcwd() + '../')
        with app.test_request_context():
            import wiki.web.routes as routes
            self.assertEquals("", routes.autocomplete("toankal"))

    def test_home(self):
        app = create_app(os.getcwd() + '../')
        with app.test_request_context():
            import wiki.web.routes as routes
            self.assertEquals("<a href='/home'>test</a>", routes.autocomplete("test"))


if __name__ == '__main__':
    unittest.main()
