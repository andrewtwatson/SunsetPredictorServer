from django.db import models
from django.utils import timezone
from .userModel import User

class SunsetRatingEntry(models.Model):
    """
    Holds datum of one sunset rating from a user.
    The top section are the only ones filled in at time of recording. 
    The rest are filled in at a different time as they can be derrived from the first five.
    """

    user_id = models.ForeignKey(User, on_delete=models.PROTECT, db_column='user_id')
    date_time = models.DateTimeField('Date and Time of Recording')
    longitude = models.DecimalField(max_digits=8, decimal_places=6)
    latitude = models.DecimalField(max_digits=8, decimal_places=6)
    rating = models.DecimalField(max_digits=4, decimal_places=2)

    # Everything below this should have a default of null

    @staticmethod
    def createEntry(user_id, postedSecretKey, rating, longitude, latitude, date_time=timezone.now()):
        """
        Creates a new datum entry with the given parameters.
        """

        user = User.objects.get(pk=user_id)
        if user_id < 0:
            raise ValueError('user_id is negative')
        if not user.authenticateUser(postedSecretKey):
            raise PermissionError('Incorrect secret key or not set up or deleted')
        if rating < 0.0 or rating > 10.0:
            raise ValueError('rating outside of range [0..10]')
        if longitude < -180.0 or longitude > 180.0:
            raise ValueError('longitude outside of range [-180..180]')
        if latitude < -180.0 or latitude > 180.0:
            raise ValueError('latitude outside of range [-90..90]')

        e = SunsetRatingEntry(user_id=user, date_time=date_time, rating=rating, longitude=longitude, latitude=latitude)
        e.save()
        return e