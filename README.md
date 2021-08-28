# SunsetPredictorServer
### Version 0.1.3 -- all tests passing locally, has not been deployed to remote yet, only does recieving

Server for the SunsetPredictor application. Will be deployed with Heroku.

Server runs with django

When you first download the app, it should send a GET request to setup a new user. The server will respond with a user_id and a secret_id that should be saved on the phone.
The client then sends a POST to confirm the setup of the user.
Then every later POST request should include the user_id so it can be kept track of.

Dependencies:
 - django
 - requests

To Set Up:
 - set environmental variables for:
   - SUNSET_PREDICTOR_DJANGO_KEY
   - SUNSET_PREDICTOR_OPEN_WEATHER_KEY
   - SUNSET_PREDICTOR_SUNRISE_SUNSET_KEY

APIs:
 - openweathermap
 - https://sunrise-sunset.org/api

Current Release - 0.1.0:
 - All test cases are passing. But nothing has been set up with Heroku yet. That's the next TODO
 - Only recieves data, no predictions yet