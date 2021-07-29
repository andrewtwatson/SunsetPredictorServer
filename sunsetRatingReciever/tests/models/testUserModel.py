from django.test import TestCase
from sunsetRatingReciever.models import User, SunsetRatingEntry

class UserModelTestCase(TestCase):
    def test_new_user_model(self):
        """
        Tests the new user model and finish setup of user
        """
        u1 = User.createNewUser()
        self.assertEqual(u1.user_id, 1)
        self.assertEqual(u1.setup_confirmed, False)
        self.assertEqual(u1.deleted, False)
        self.assertEqual(len(u1.secret_key), 20)

        # finish setup good
        u1.finishSetup(u1.secret_key)
        self.assertEqual(u1.user_id, 1)
        self.assertEqual(u1.setup_confirmed, True)
        self.assertEqual(u1.deleted, False)
        self.assertEqual(len(u1.secret_key), 20)

        # finish setup duplicate
        with self.assertRaises(KeyError):
            u1.finishSetup(u1.secret_key)
        self.assertEqual(u1.user_id, 1)
        self.assertEqual(u1.setup_confirmed, True)
        self.assertEqual(u1.deleted, False)
        self.assertEqual(len(u1.secret_key), 20)

        u2 = User.createNewUser()
        self.assertEqual(u2.user_id, 2)
        self.assertEqual(u2.setup_confirmed, False)
        self.assertEqual(len(u2.secret_key), 20)
        self.assertNotEqual(u1.secret_key, u2.secret_key)

        # finish setup bad key
        with self.assertRaises(PermissionError):
            u2.finishSetup('abcd')
        self.assertEqual(u2.user_id, 2)
        self.assertEqual(u2.setup_confirmed, False)
        self.assertEqual(len(u2.secret_key), 20)
        self.assertNotEqual(u1.secret_key, u2.secret_key)


    def test_authenticate_user(self):
        """
        test the user.authenticateUser method
        """
        u1 = User.createNewUser()
        u1.finishSetup(u1.secret_key)

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

    def test_deleted_user(self):
        """
        If the user is deleted, nothing should work.
        """
        u1 = User.createNewUser()
        u1.finishSetup(u1.secret_key)
        u1.deleted = True
        u1.save()

        # test that authenticate fails
        self.assertFalse(u1.authenticateUser(u1.secret_key))

        # test that submiting an entry fails
        with self.assertRaises(PermissionError):
            SunsetRatingEntry.createEntry(u1.user_id, u1.secret_key, 1.2, 34, 56)