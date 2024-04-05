from django.urls import path

from .views import pdfToRdf

urlpatterns = [
    path('api/pdfToRdf', pdfToRdf, name='pdfToRdf'),
]