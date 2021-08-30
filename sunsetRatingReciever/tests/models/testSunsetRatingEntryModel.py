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
        e = SunsetRatingEntry(user_id=u, date_time=timezone.now(), rating=5.1, longitude=811.0, latitude=-559.0)
        e.save()

        result = e.finishRatingEntry()
        self.assertEqual(result, None)

        # make sure an error entry has been made
        error = Error.objects.get(pk=1)
        self.assertEqual(error.type, 'open weather failure')
        self.assertTrue('response code' in error.info)

    def test_finish_entry_good(self):
        """
        Test that the finish entry method works and that all fields are filled in.
        """
        u = User.createNewUser()
        u.finishSetup(u.secret_key)

        e = SunsetRatingEntry.createEntry(u.user_id, u.secret_key, 5.5, latitude=35.776, longitude=-78.6382)

        # make sure there is no errors
        self.assertEqual(0, len(Error.objects.all()))

        # make sure the entry is all filled out
        self.assertTrue(e.sunset_time != None)
        self.assertTrue(e.minutes_to_sunset != None)
        self.assertTrue(0 <= e.cloud_cover_percent <= 100)
        self.assertTrue(e.air_quality_index >= 0)
        self.assertTrue(e.air_quality_pm10 >= 0)
        self.assertTrue(0 <= e.humidity <= 100)
        self.assertTrue(e.temperature != None)
        self.assertTrue(e.air_pressure != None)
        self.assertTrue(0 <= e.time_from_last_rain_to_sunset <= 24)
        self.assertTrue(e.season in ['summer', 'fall', 'winter', 'spring'])
        
        self.assertEqual(e.rating, 5.5)