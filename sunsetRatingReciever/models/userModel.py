from django.db import models
from django.utils import timezone
from random import SystemRandom
import string

class User(models.Model):
    """
    Holds information about each user. Just an ID and a origination date for now 
    """

    # When a user is created, send this to the client
    user_id = models.BigAutoField(primary_key=True)

    # Random string generated when the user is created.
    # Used for a very basic authentication scheme. The secret key must be included in any post request.
    secret_key = models.CharField(max_length=20)

    first_login_date = models.DateTimeField()

    # Set to true once the client sends confirmation that the user_id was saved.
    setup_confirmed = models.BooleanField(default=False)

    # if for whatever reason the user should be deleted, set to true
    deleted = models.BooleanField(default=False)

    def authenticateUser(self, postedSecretKey):
        """
        Tests the secret key sent in the post request with the one stored for this user.
        Also checks that the user has been set up and is not deleted
        Return true if they are the same, false otherwise.
        """
        return self.deleted == False and self.setup_confirmed == True and self.secret_key == postedSecretKey

    @staticmethod
    def createNewUser(dateTime=timezone.now()):
        """
        Creates and returns a new user.
        """
        secretKey = _generateSecretKey()
        u = User(secret_key=secretKey, first_login_date=dateTime)
        u.save()
        return u

    def finishSetup(self, postedSecretKey):
        # if already setup or deleted, throw error
        if self.setup_confirmed or self.deleted:
            raise KeyError('User is already set up or deleted')

        if self.secret_key != postedSecretKey:
            raise PermissionError('Incorrect secret key')

        # change setup_confirmed to true
        self.setup_confirmed = True
        self.save()

def _generateSecretKey():
    """
    Generates a random string of length 20 with letters and numbers to be stored 
    as a user's secret key.
    """
    return ''.join(SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))