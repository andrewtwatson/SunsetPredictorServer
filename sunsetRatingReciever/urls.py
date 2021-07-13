from django.urls import path

from . import views

app_name = 'sunsetRatingReciever'
urlpatterns = [
    path('', views.index, name='index'),
    path('submitRating/', views.submitRating, name='submitRating'),
    path('createUser/', views.createUser, name='createUser'),
]