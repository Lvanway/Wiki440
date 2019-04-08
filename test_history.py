from history.history import add_history
from history.history import get_history
from history.history import move_history
from history.history import delete_history
from history.history import revert_to_index

from config import CONTENT_DIR

import unittest

import os
import json

# unit tests require that no page called 'unittest.md' and no history db called 'unittest.json' exist


class TestHistory(unittest.TestCase):

    def test_get_history(self):
        # create mock history json file
        with open('./history/content/unittest.json', 'w') as json_file:
            dict = { "1" : {
                "author": "Tester",
                "datetime": "11/11/1111 11:11:11",
                "message": "Test!",
                "html": "<p>Test!</p>",
                "markdown": "title: \ntags: \n\nTest!",
                "action": "edit"
            }}
            json.dump(dict, json_file)

        # get history and test
        history = get_history('unittest')
        self.assertEqual(history["1"]["message"], 'Test!')
        self.assertEqual(history["1"]["html"], '<p>Test!</p>')

        # tear down
        os.remove('./history/content/unittest.json')

    def test_add_history(self):
        # add history and test
        add_history('unittest', 'Tester', 'Test!', '<p>Test!</p>', 'title: \ntags: \n\nTest!', 'edit')
        history = get_history('unittest')
        self.assertEqual(history["1"]["message"], 'Test!')
        self.assertEqual(history["1"]["html"], '<p>Test!</p>')

        # tear down
        os.remove('./history/content/unittest.json')

    def test_move_history(self):
        # add history and do the move
        add_history('unittest', 'Tester', 'Test!', '<p>Test!</p>', 'title: \ntags: \n\nTest!', 'edit')
        move_history('unittest', 'newunittest')
        history = get_history('newunittest')

        # test
        self.assertEqual(history["1"]["message"], 'Test!')
        self.assertEqual(history["1"]["html"], '<p>Test!</p>')

        # tear down
        os.remove('./history/content/newunittest.json')

    def test_delete_history(self):
        # add history and assert it was added
        add_history('unittest', 'Tester', 'Test!', '<p>Test!</p>', 'title: \ntags: \n\nTest!', 'edit')
        self.assertTrue(os.path.exists('./history/content/unittest.json'))

        # delete history and assert it was deleted
        delete_history('unittest')
        self.assertTrue(not os.path.exists('./history/content/unittest.json'))

    def test_revert(self):
        # create markdown file for test
        open(CONTENT_DIR + 'unittest.md', 'w').close()

        # create mock history json file
        with open('./history/content/unittest.json', 'w') as json_file:
            dict = {"1": {
                "author": "Tester",
                "datetime": "11/11/1111 11:11:11",
                "message": "Test!",
                "html": "<p>Test!</p>",
                "markdown": "title: \ntags: \n\nTest!",
                "action": "edit"
            }, "2": {
                "author": "Tester",
                "datetime": "11/11/1111 11:11:11",
                "message": "Changed!",
                "html": "<p>New!</p>",
                "markdown": "title: \ntags: \n\nNew!",
                "action": "edit"
            }}
            json.dump(dict, json_file)

        # do revert and test
        revert = revert_to_index('unittest', '1')
        self.assertEqual(revert[0], '<p>Test!</p>')
        self.assertEqual(revert[1], 'title: \ntags: \n\nTest!')

        # tear down
        os.remove('./history/content/unittest.json')
        os.remove(CONTENT_DIR + 'unittest.md')


if __name__ == '__main__':
    unittest.main()
