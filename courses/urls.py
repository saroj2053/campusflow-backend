from django.urls import path

from . import views
from .views import get_courses_from_university

urlpatterns = [
    path('', get_courses_from_university, name="get-courses"),
]