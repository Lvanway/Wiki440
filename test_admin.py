import unittest
import json
from wiki.web.user import UserManager

class TestAdmin(unittest.TestCase):


    def test_user_role(self):
        # get a user instance and verify user role
        user_manager = UserManager
        user = user_manager.get_user(user_manager, "admin")
        self.assertEqual(user.get("roles")[0], 'admin')


    def test_user_role_update(self):
        user_manager = UserManager
        user = user_manager.get_user(user_manager, "logan")
        if self.assertNotEqual(user.get("roles")[0], 'user'):
            user.set("roles", 'admin')
            user.save()
            self.assertEqual(user.get("roles")[0], 'admin')
        else:
            user.set("roles", 'user')
            self.assertNotEqual(user.get("roles")[0], 'admin')

if __name__ == '__main__':
    unittest.main()