from django.urls import path
from home.views import index, feedback, offers

urlpatterns = [
    path('', index, name='index'),
    path('feedback/', feedback, name='feedback'),
    path('offers/', offers, name='offers'),
]