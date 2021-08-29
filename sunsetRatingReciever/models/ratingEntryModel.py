from datetime import date, datetime
from django.db import models
from django.utils import timezone
from .userModel import User
from .errorModel import Error
from ..utils import hoursDelta, minutesDelta
from pathlib import Path
import requests
import sys
import traceback
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
    # measured in μg/m3
    air_quality_pm10 = models.DecimalField(max_digits=15, decimal_places=10, null=True, default=None, blank=True)
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

        # define variables for error use
        weatherUrlNow = None
        weatherResponseNow = None
        weatherUrlYesterday = None
        weatherResponseYesterday = None
        aqiUrl = None
        aqiResponse = None

        # extract weather data
        try:
            # get the weather api info
            # Using the historical api bc it has hisotry and current.
            # going to need the data from today and yesterday to get the last 24 hours of rain
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
            minToSunset = minutesDelta(currentUnixTime, sunsetUnixTime)
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
            unixTimeOfLastRain = 86400
            dayData = weatherData
            # this is how far back we've looked for rain in this day so far. Basically in index into the json response
            hourCounter = -1
            while hoursSinceRain < 24:
                # if first time through, use current. Otherwise use the hourly
                thisHourWeatherData = None
                if hourCounter == -1:
                    thisHourWeatherData = dayData['current']
                else:
                    thisHourWeatherData = dayData['hourly'][hourCounter]
                thisHourWeatherId = thisHourWeatherData['weather'][0]['id']

                # see https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2 for weather codes
                if thisHourWeatherId <= 701:
                    unixTimeOfLastRain = thisHourWeatherData['dt']
                    break

                hourCounter += 1
                # see if we hit the end of this day, if so go to previous day
                if hourCounter >= len(dayData['hourly']):
                    dayData = yesterdayData
                    hourCounter = 0

                hoursSinceRain += 1

            rainToSunset = hoursDelta(unixTimeOfLastRain, sunsetUnixTime)
            # the most to measure for rain is 24
            self.time_from_last_rain_to_sunset = min(rainToSunset, 24)

            # do seperate call for the air quality
            aqiUrl = ("https://api.openweathermap.org/data/2.5/air_pollution?"
                             "lat=%f&lon=%f&appid=%s" 
                             % (self.latitude, self.longitude, OPEN_WEATHER_API_KEY))
            aqiResponse = requests.get(aqiUrl)
            aqiData = aqiResponse.json()
            self.air_quality_index = aqiData['list'][0]['main']['aqi']
            self.air_quality_pm10 = aqiData['list'][0]['components']['pm10']

            self.save()
        except Exception as exc:
            # make sure all variables are defined
            if weatherUrlNow is None:
                weatherUrlNow = "NONE"
            if weatherResponseNow is None:
                nowStatusCode = 999
                nowContent = "NONE"
            else:
                nowStatusCode = weatherResponseNow.status_code
                nowContent = weatherResponseNow.content
            if weatherUrlYesterday is None:
                weatherUrlYesterday = "NONE"
            if weatherResponseYesterday is None:
                yesterdayStatusCode = 999
                yesterdayContent = "NONE"
            else:
                yesterdayStatusCode = weatherResponseYesterday.status_code
                yesterdayContent = weatherResponseYesterday.content
            if aqiUrl is None:
                aqiUrl = "NONE"
            if aqiResponse is None:
                aqiStatusCode = 999
                aqiContent = "NONE"
            else:
                aqiStatusCode = aqiResponse.status_code
                aqiContent = aqiResponse.content

            errInfo = ("There was an error extracting the data from the weather api.\n"
                       "exception: %s\n"
                       "traceback: %s\n"
                       "user_id: %d\n"
                       "url now: %s\n"
                       "response code now: %d\n"
                       "response content now: %s\n"
                       "url yesterday: %s\n"
                       "response code yesterday: %d\n"
                       "response content yesterday: %s\n"
                       "url aqi: %s\n"
                       "response code aqi: %d\n"
                       "response content aqi: %s\n"
                       % (str(exc), traceback.format_exc(), self.user_id.user_id, weatherUrlNow, nowStatusCode, nowContent, \
                          weatherUrlYesterday, yesterdayStatusCode, yesterdayContent, aqiUrl, aqiStatusCode, aqiContent)
                      )
            error = Error(date=timezone.now(), type='open weather failure', info=errInfo)
            error.save()
            #return ""