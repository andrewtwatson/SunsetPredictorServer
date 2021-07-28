from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import User

@require_POST
@csrf_exempt
def createUser(request):
    """
    Creates a new user and returns JSON with the user's id and secret key
    Returns a status of 201 if it worked correctly
    """
    u = User.createNewUser(timezone.now())
    ret = '{"user_id": "' + str(u.user_id) + '", "secret_key": "' + u.secret_key + '"}'
    
    return HttpResponse(ret, status=201, content_type='application/json')

@require_POST
@csrf_exempt
def finishUserSetup(request):
    """
    After a user is created, this recieves a post from the user to confirm that the user
    has stored their user id and secret key. It marks the user as ready to use.
    Returns status of:
     - 201 if submitted correctly
     - 400 if the post request is malformed (missing secretkey, user is already setup or deleted, etc)
     - 401 if the user's secret key is wrong
     - 403 if the user is not in the database
    """
    try:
        user_id = int(request.POST['user_id'])
        secretKey = request.POST['secret_key']

        user = User.objects.get(pk=user_id)
        user.finishSetup(secretKey)
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
        return HttpResponse('at sunsetRatingReciever/finishUserSetup/', status=201)