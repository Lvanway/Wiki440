from flask import current_app
from flask import Flask
from flask import g
from flask_login import LoginManager
from werkzeug.local import LocalProxy

from wiki.core import Wiki
from wiki.web.user import UserManager

import unittest

import os
'''
class TestHistory(unittest.TestCase):

    def test_empty_history(self):
        @patch('test_app.')
'''
