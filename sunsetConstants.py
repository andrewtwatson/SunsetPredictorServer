"""
These are the constants to be used throughout the application.
Many of these pull from environmental variables that must be set up.
"""

import os

# The secret key for django
DJANGO_SECRET_KEY = os.environ['SUNSET_PREDICTOR_DJANGO_KEY']

# api key for open weather
OPEN_WEATHER_API_KEY = os.environ['SUNSET_PREDICTOR_OPEN_WEATHER_KEY']

# api key for sunrise sunset
SUNRISE_SUNSET_API_KEY = os.environ['SUNSET_PREDICTOR_SUNRISE_SUNSET_KEY']
