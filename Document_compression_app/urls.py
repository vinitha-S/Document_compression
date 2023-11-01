from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django.urls import path
from .views import FileUploadAndCompressView

urlpatterns = [
    path('', FileUploadAndCompressView.as_view(), name='file_upload'),
]


