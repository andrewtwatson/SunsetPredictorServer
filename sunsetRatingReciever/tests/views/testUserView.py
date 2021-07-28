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

    def test_finish_user_setup_view(self):
        """
        Tests the finish user view
        """
        createUrl = reverse('sunsetRatingReciever:createUser')
        finishUrl = reverse('sunsetRatingReciever:createUser')

        # try a get request, shouldnt work
        response = self.client.get(finishUrl)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # create a user
        response = self.client.post(createUrl)
        self.assertEqual(response.status_code, 201)
        userJson = json.loads(response.content)

        # try a working version
        goodJsonString = '{"user_id":"' + userJson['user_id'] + '", "secret_key":"' + userJson['secret_key'] + '"}'
        response = self.client.post(finishUrl, goodJsonString)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # try doing it a second time, shouldn't work
        goodJsonString = '{"user_id":"' + userJson['user_id'] + '", "secret_key":"' + userJson['secret_key'] + '"}'
        response = self.client.post(finishUrl, goodJsonString)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')

         # create a second user
        response = self.client.post(createUrl)
        self.assertEqual(response.status_code, 201)
        userJson = json.loads(response.content)

        # try to send but missing the user id
        badJsonString = '{"secret_key":"' + userJson['secret_key'] + '"}'
        response = self.client.post(finishUrl, badJsonString)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # try to send but missing the secret key
        badJsonString = '{"user_id":"' + userJson['user_id'] + '"}'
        response = self.client.post(finishUrl, badJsonString)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # try to send but user doesnt exist
        badJsonString = '{"user_id":"123456789", "secret_key":"' + userJson['secret_key'] + '"}'
        response = self.client.post(finishUrl, badJsonString)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # try to send but the key is wrong
        badJsonString = '{"user_id":"' + userJson['user_id'] + '", "secret_key":"abcdefghijklm"}'
        response = self.client.post(finishUrl, badJsonString)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # try to send but the user has been deleted
        user = User.objects.get(pk=int(userJson['user_id']))
        user.deleted = True
        goodJsonString = '{"user_id":"' + userJson['user_id'] + '", "secret_key":"' + userJson['secret_key'] + '"}'
        response = self.client.post(finishUrl, goodJsonString)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')