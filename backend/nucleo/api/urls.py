from django.urls import path

from . import views

urlpatterns = [
    path("saude", views.saude, name="saude"),
]
