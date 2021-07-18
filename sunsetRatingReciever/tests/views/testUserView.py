import json
from django.test import TestCase
from django.urls import reverse
from sunsetRatingReciever.models import User, SunsetRatingEntry

class UserViewTestCase(TestCase):
    def test_new_user_view(self):
        """
        Creates a new user and verifies that the response is good.
        """
        
        url = reverse('sunsetRatingReciever:createUser')

        # try to send a get request, should not work
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # create a user, verify the expected user id it would return
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        responseJson = json.loads(response.content)
        self.assertEqual(responseJson['user_id'], '1')
        self.assertEqual(len(responseJson['secret_key']), 20)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        responseJson = json.loads(response.content)
        self.assertEqual(responseJson['user_id'], '2')
        self.assertEqual(len(responseJson['secret_key']), 20)