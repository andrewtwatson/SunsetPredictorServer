# SunsetPredictorServer

Server for the SunsetPredictor application. Hopefully this will be integrated with heroku... We'll see.

Server runs with django

When you first download the app, it should send a GET request to setup a new user. The server will respond with a userID that should be saved on the phone.
Then every later POST request should include the userID so it can be kept track of.

Environment Variables Set:
- set DJANGO_SETTINGS_MODULE=SunsetPredictorServer.settings
  - Just make a second settings file for production and set a different environment variable on the main server to point to that one

//TODO make the settings.DEBUG work