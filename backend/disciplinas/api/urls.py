from django.urls import path

from . import views

urlpatterns = [
    path("disciplinas", views.listar, name="disciplinas"),
    path("disciplinas/<int:disciplina_id>/favorito", views.favorito, name="favorito"),
]
