from django.test import TestCase
from django.utils import timezone
from sunsetRatingReciever.models import User, SunsetRatingEntry, Error

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

    
    def test_finish_entry_bad(self):
        """
        Test things that would break the finish entry method
        """
        u = User.createNewUser()
        u.finishSetup(u.secret_key)

        # set entry manually
        e = SunsetRatingEntry(user_id=u, date_time=timezone.now(), rating=5, longitude=-248, latitude=-689)
        e.save()

        result = e.finishEntry()
        self.assertEqual(result, "")

        # make sure an error entry has been made
        error = Error.objects.get(pk=1)
        self.assertEqual(error.type, 'open weather failure')
        self.assertTrue('response code' in error.info)

    def test_finish_entry_good(self):
        """
        Test that the finish entry method works and that all fields are filled in.
        """
