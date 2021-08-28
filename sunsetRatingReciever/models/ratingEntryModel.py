from datetime import date, datetime
from django.db import models
from django.utils import timezone
from .userModel import User
from .errorModel import Error
from ..utils import hoursDelta, minutesDelta
from pathlib import Path
import requests
import sys
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(BASE_DIR)
from sunsetConstants import OPEN_WEATHER_API_KEY, SUNRISE_SUNSET_API_KEY


class SunsetRatingEntry(models.Model):
    """
    Holds datum of one sunset rating from a user.
    The top section are the only ones filled in at time of recording. 
    The rest are filled in at a different time as they can be derrived from the first five.
    """

    user_id = models.ForeignKey(User, on_delete=models.PROTECT, db_column='user_id')
    # UTC time
    date_time = models.DateTimeField('Date and Time of Recording')
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    rating = models.DecimalField(max_digits=4, decimal_places=2)

    # Everything below this should have a default of null
    # UTC time
    sunset_time = models.DateTimeField('Date and Time of Sunset', null=True, default=None, blank=True)
    # minutes between when submitted and sunset. may be negative
    minutes_to_sunset = models.DecimalField(max_digits=6, decimal_places=1, null=True, default=None, blank=True)

    # weather conditions
    cloud_cover_percent = models.IntegerField(null=True, default=None, blank=True)
    air_quality_index = models.IntegerField(null=True, default=None, blank=True)
    humidity = models.IntegerField(null=True, default=None, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None, blank=True)
    air_pressure = models.IntegerField(null=True, default=None, blank=True)
    # time between last rainfall and when the sunset was. Measured in hours.
    time_from_last_rain_to_sunset = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None, blank=True)
    season = models.CharField(max_length=8, null=True, default=None, blank=True)

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

        e.finishRatingEntry()

        return e

    def finishRatingEntry(self):
        """
        Assumes that the entry already has the first parts filled out. Then uses apis to fill out the rest of the entry
        """
        if self.rating == None or self.longitude == None or self.latitude == None:
            raise ValueError('entry not set up yet')

        # extract weather data
        try:
            # get the weather api info
            # Using the historical api bc it has hisotry and current.
            # going to need the data from today and yesterday to get the last 24 hours of rain
            # TODO its saying it in the future. Try subtracting a few more seconds
            currentUnixTime = int(datetime.now().timestamp()) - 60
            weatherUrlNow = ("https://api.openweathermap.org/data/2.5/onecall/timemachine?"
                             "lat=%f&lon=%f&units=%s&dt=%d&appid=%s" 
                             % (self.latitude, self.longitude, "imperial", currentUnixTime, OPEN_WEATHER_API_KEY))
            weatherResponseNow = requests.get(weatherUrlNow)
            weatherUrlYesterday = ("https://api.openweathermap.org/data/2.5/onecall/timemachine?"
                                   "lat=%f&lon=%f&units=%s&dt=%d&appid=%s" 
                                   % (self.latitude, self.longitude, "imperial", currentUnixTime - 86400, OPEN_WEATHER_API_KEY))
            weatherResponseYesterday = requests.get(weatherUrlYesterday)
            if weatherResponseNow.status_code > 200 or weatherResponseYesterday.status_code > 200:
                raise ValueError('response code above 200')

            weatherData = weatherResponseNow.json()
            yesterdayData = weatherResponseYesterday.json()

            sunsetUnixTime = int(weatherData['current']['sunset'])
            self.sunset_time = datetime.utcfromtimestamp(sunsetUnixTime)
            # if its almost 24 hours off bc of utc, add/sub 24 hours
            minToSunset = minuteDelta(sunsetUnixTime)
            if minToSunset > 60 * 12:
                minToSunset -= 60 * 12
            if minToSunset < -60 * 12:
                minToSunset += 60 * 12
            self.minutes_to_sunset = minToSunset

            self.cloud_cover_percent = weatherData['current']['clouds']
            self.humidity = weatherData['current']['humidity']
            self.temperature = weatherData['current']['temp']
            self.air_pressure = weatherData['current']['pressure']

            # get the season
            doy = datetime.today().timetuple().tm_yday
            # "day of year" ranges for the northern hemisphere
            spring = range(80, 172)
            summer = range(172, 264)
            fall = range(264, 355)
            # winter = everything else
            if doy in spring:
              season = 'spring'
            elif doy in summer:
              season = 'summer'
            elif doy in fall:
              season = 'fall'
            else:
              season = 'winter'
            self.season = season

            # figure out when the last rain was
            # start from now and go backwards until you hit 24 hours or the weather code says rain
            hoursSinceRain = 0
            secondsOfLastRain = 0
            while hoursSinceRain < 24:
                weatherCode = None # TODO ( if hours=0: present, else go back in time)
                # TODO current idea for this: make var `currentDayData`, and a counter to go back through that list, once you get to the end of the list
                # reset the counter, change currentDayData to the other day.

                # see https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2 for weather codes
                if weatherCode <= 701:
                    secondsOfLastRain = None # TODO
                    break
                hoursSinceRain += 1

            rainToSunset = timeDelta(secondsOfLastRain, sunsetUnixTime)
            # the most to measure for rain is 24
            self.rainToSunset = min(rainToSunset, 24)

            # do seperate call for the air quality
            # TODO
            #self.air_quality_index = weatherData['list'][0]['main']['aqi']

            self.save()
        except Exception as exc:
            errInfo = ("There was an error extracting the data from the weather api.\n"
                       "exception: %s\n"
                       "user_id: %d\n"
                       "url now: %s\n"
                       "response code now: %d\n"
                       "response content now: %s\n"
                       "url yesterday: %s\n"
                       "response code yesterday: %d\n"
                       "response content yesterday: %s"
                       % (str(exc), self.user_id.user_id, weatherUrlNow, weatherResponseNow.status_code, weatherResponseNow.content, \
                          weatherUrlYesterday, weatherResponseYesterday.status_code, weatherResponseYesterday.content)
                      )
            error = Error(date=timezone.now(), type='open weather failure', info=errInfo)
            error.save()
            #return ""