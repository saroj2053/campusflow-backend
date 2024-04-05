from django.urls import path
from .views import get_universities
   
urlpatterns = [
    path('', get_universities, name="get-universities"),
]