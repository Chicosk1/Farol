from django.urls import path

from . import views

urlpatterns = [
    path("disciplinas", views.listar, name="disciplinas"),
]
