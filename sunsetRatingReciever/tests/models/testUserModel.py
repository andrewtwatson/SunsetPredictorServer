from django.test import TestCase
from sunsetRatingReciever.models import User, SunsetRatingEntry

class UserModelTestCase(TestCase):
    def test_new_user_model(self):
        """
        Tests the new user model
        """
        u1 = User.createNewUser()
        self.assertEqual(u1.user_id, 1)
        self.assertEqual(u1.setup_confirmed, False)
        self.assertEqual(u1.deleted, False)
        self.assertEqual(len(u1.secret_key), 20)

        u2 = User.createNewUser()
        self.assertEqual(u2.user_id, 2)
        self.assertEqual(u2.setup_confirmed, False)
        self.assertEqual(len(u2.secret_key), 20)
        self.assertNotEqual(u1.secret_key, u2.secret_key)

    def test_authenticate_user(self):
        """
        test the user.authenticateUser method
        """
        u1 = User.createNewUser()

        # test working
        self.assertTrue(u1.authenticateUser(u1.secret_key))

        # test secret key thats too short
        self.assertFalse(u1.authenticateUser(u1.secret_key[:-1]))

        # test secret key thats too short
        self.assertFalse(u1.authenticateUser(u1.secret_key + 'a'))

        # test one letter different
        toReplace = 'a'
        if u1.secret_key[0] == 'a':
            toReplace = 'b'
        skey = toReplace + u1.secret_key[1:]
        self.assertFalse(u1.authenticateUser(skey))