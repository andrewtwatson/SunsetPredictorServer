from django.test import TestCase
from sunsetRatingReciever.models import User, SunsetRatingEntry

class SunsetModelTestCase(TestCase):
    def test_bad_entry(self):
        """
        Test making an entry that is illegal
        """
        u = User.createNewUser()
        u.finishSetup(u.secret_key)

        # make an entry for a user that doesn't exist yet
        with self.assertRaises(User.DoesNotExist):
            SunsetRatingEntry.createEntry(2, '12345678901234567890', 8.5, 2.5, 2.5)
        self.assertEquals(u.sunsetratingentry_set.count(), 0)

        # make an entry with a negaitive rating
        with self.assertRaises(ValueError):
            SunsetRatingEntry.createEntry(u.user_id, u.secret_key, -12, 10.15, 10.547)
        self.assertEquals(u.sunsetratingentry_set.count(), 0)

        # make an entry with a bad secret key rating
        with self.assertRaises(PermissionError):
            SunsetRatingEntry.createEntry(u.user_id, u.secret_key + 'abcdefg', -12, 10.15, 10.547)
        self.assertEquals(u.sunsetratingentry_set.count(), 0)
    
    def test_good_entry(self):
        """
        Test making a legal entry
        """
        u = User.createNewUser()
        u.finishSetup(u.secret_key)

        e = SunsetRatingEntry.createEntry(u.user_id, u.secret_key, 5.5, 12.789, -12.78)
        self.assertEquals(u.sunsetratingentry_set.count(), 1)
        self.assertEquals(e.rating, 5.5)