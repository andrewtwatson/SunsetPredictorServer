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
    """
    u = User.createNewUser(timezone.now())
    ret = '{"user_id": "' + str(u.user_id) + '", "secret_key": "' + u.secret_key + '"}'
    
    return HttpResponse(ret, status=201, content_type='application/json')