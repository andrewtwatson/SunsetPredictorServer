from .userViews import createUser, finishUserSetup
from .ratingEntryViews import submitRating

def index(request):
    return HttpResponse('at sunsetRatingReciever')