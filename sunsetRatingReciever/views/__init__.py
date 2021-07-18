from .userViews import createUser
from .ratingEntryViews import submitRating

def index(request):
    return HttpResponse('at sunsetRatingReciever')