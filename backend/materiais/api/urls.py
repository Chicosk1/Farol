from django.urls import path

from . import views

urlpatterns = [
    path("disciplinas/<int:disciplina_id>/materiais", views.enviar, name="materiais"),
]
