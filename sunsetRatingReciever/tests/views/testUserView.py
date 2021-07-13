from django.test import TestCase
from django.urls import reverse
from sunsetRatingReciever.models import User, SunsetRatingEntry

class UserViewTestCase(TestCase):
    def test_new_user_view(self):
        """
        Creates a new user and verifies it has a correct user_id
        """
        
        url = reverse('sunsetRatingReciever:createUser')

        # try to send a get request, should not work
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # create a user, verify the expected user id it would return
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content.decode('UTF-8'), '1')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content.decode('UTF-8'), '2')