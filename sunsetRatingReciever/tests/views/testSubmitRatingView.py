#import os, sys
#from contextlib import ContextDecorator, redirect_stderr
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from sunsetRatingReciever.models import User, SunsetRatingEntry

#class disableStderr(ContextDecorator):
#    def __enter__(self):
#        """
#        Disable the stderr, send it to devnull
#        """
#        redirect_stderr(os.devnull)

#    def __exit__(self, *exc):
#        """
#        Reset the stderr to normal stderr
#        """
#        redirect_stderr(sys.__stderr__)

def compliantPostDataFactory(secretKey):
    return {
        'user_id': '1',
        'secret_key': secretKey,
        'rating': '7.2',
        'longitude': '-78.644257',
        'latitude': '35.787743',
        }

url = reverse('sunsetRatingReciever:submitRating')

class SubmitRatingViewTestCase(TestCase):
    
    def test_submit_incomplete_rating_view(self):
        """
        Tests submitting bad incomplete ratings to the server
        """
        
        # try to send a get request, should not work
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # try to send a post with no data
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # try to send a good post a user that hasn't been created
        data = compliantPostDataFactory('abc')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content.decode('UTF-8'), '')

        # create a user
        u = User.createNewUser()
        skey = u.secret_key
        self.assertEqual(u.user_id, 1)

        # try to send a good post except no user_id
        data = compliantPostDataFactory(skey)
        data.pop('user_id')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

        # try to send a good post except no secret key
        data = compliantPostDataFactory(skey)
        data.pop('secret_key')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

        # try to send a good post except no rating
        data = compliantPostDataFactory(skey)
        data.pop('rating')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

        # try to send a good post except no longitude
        data = compliantPostDataFactory(skey)
        data.pop('longitude')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

        # try to send a good post except no latitude
        data = compliantPostDataFactory(skey)
        data.pop('latitude')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

    def test_submit_malformed_rating_view_debug_false(self):
        """
        Run through the malformed rating view with debug as false
        """
        self.submitMalformedRatingViewWithDebugOption(False)
    
    
    #@disableStderr()
    def test_submit_malformed_rating_view_debug_true(self):
        """
        Run through the malformed rating view with debug as false
        This prints all the "Bad Requests" when the tests are run, nothing I an do about it.
        """
        with self.settings(DEBUG=True):
           self.submitMalformedRatingViewWithDebugOption(True)

    def submitMalformedRatingViewWithDebugOption(self, debug):
        """
        Tests submitting bad datatyped ratings to the server
        """
        
        # setup for tests
        u = User.createNewUser()
        skey = u.secret_key
        self.assertEqual(1, u.user_id)

        # try to send a good post except the user_id is alphenumeric
        data = compliantPostDataFactory(skey)
        data['user_id'] = '12abcd'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        if debug:
            self.assertIn('ValueError', response.content.decode('UTF-8'))
        else:
            self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

        # try to send a good post except the secret_key is off by one letter
        data = compliantPostDataFactory(skey)
        toReplace = 'a'
        if data['secret_key'][0] == 'a':
            toReplace = 'b'
        data['secret_key'] = toReplace + data['secret_key'][1:]
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)
        if debug:
            self.assertIn('PermissionError', response.content.decode('UTF-8'))
        else:
            self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

        # try to send a good post except the rating is alphenumeric
        data = compliantPostDataFactory(skey)
        data['rating'] = '12abcd'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        if debug:
            self.assertIn('ValueError', response.content.decode('UTF-8'))
        else:
            self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

        # try to send a good post except the rating is negative
        data = compliantPostDataFactory(skey)
        data['rating'] = '-7.1'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        if debug:
            self.assertIn('ValueError', response.content.decode('UTF-8'))
        else:
            self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

        # try to send a good post except the rating is above 10.0
        data = compliantPostDataFactory(skey)
        data['rating'] = '10.2'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        if debug:
            self.assertIn('ValueError', response.content.decode('UTF-8'))
        else:
            self.assertEqual(response.content.decode('UTF-8'), '')
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

    def test_submit_good_rating(self):
        """
        Tests sending a good rating to the system
        """
        
        # create a user
        u = User.createNewUser()
        skey = u.secret_key
        self.assertEqual(u.user_id, 1)
        self.assertEqual(u.sunsetratingentry_set.count(), 0)

        # send a good post
        data = compliantPostDataFactory(skey)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(u.sunsetratingentry_set.count(), 1)
        #self.assertEqual(response.content.decode('UTF-8'), '')
