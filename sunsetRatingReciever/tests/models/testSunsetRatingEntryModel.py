from django.test import TestCase
from sunsetRatingReciever.models import User, SunsetRatingEntry

class SunsetModelTestCase(TestCase):
    def test_bad_entry(self):
        """
        Test making an entry that is illegal
        """
        u = User.createNewUser()

        # make an entry for a user that doesn't exist yet
        with self.assertRaises(User.DoesNotExist):
            User.DoesNotExist, SunsetRatingEntry.createEntry(2, 8.5, 2.5, 2.5)
        self.assertEquals(u.sunsetratingentry_set.count(), 0)