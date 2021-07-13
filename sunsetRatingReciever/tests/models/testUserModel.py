from django.test import TestCase
from sunsetRatingReciever.models import User, SunsetRatingEntry

class UserModelTestCase(TestCase):
    def test_new_user_model(self):
        """
        Tests the new user model
        """
        u = User.createNewUser()
        self.assertEqual(u.user_id, 1)
        self.assertEqual(u.setup_confirmed, False)
        self.assertEqual(u.deleted, False)