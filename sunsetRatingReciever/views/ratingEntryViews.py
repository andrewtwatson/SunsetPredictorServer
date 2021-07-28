from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import SunsetRatingEntry, User

@require_POST
@csrf_exempt
def submitRating(request):
    """
    Submits a rating to the database. Expects a post request with the parameters: userId, rating, longitude, latitude
    Returns status of:
     - 201 if submitted correctly
     - 400 if the post request is malformed (missing data, etc)
     - 401 if the secret key is wrong
     - 403 if the user is not in the database
    """
    try:
        user_id = int(request.POST['user_id'])
        secretKey = request.POST['secret_key']
        rating = float(request.POST['rating'])
        longitude = float(request.POST['longitude'])
        latitude = float(request.POST['latitude'])
        
        SunsetRatingEntry.createEntry(user_id, secretKey, rating, longitude, latitude)

    except (KeyError, ValueError) as err:
        message = (str(type(err)) + err.args[0]) if settings.DEBUG else ''
        return HttpResponse(message, status=400)
    except PermissionError as err:
        message = (str(type(err)) + err.args[0]) if settings.DEBUG else ''
        return HttpResponse(message, status=401)
    except (User.DoesNotExist) as err:
        message = (str(type(err)) + err.args[0]) if settings.DEBUG else ''
        return HttpResponse(message, status=403)
    
    else:
        return HttpResponse('at sunsetRatingReciever/submitRating/', status=201)