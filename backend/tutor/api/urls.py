from django.urls import path

from . import views

urlpatterns = [
    path(
        "disciplinas/<int:disciplina_id>/tutor/perguntas",
        views.perguntar,
        name="tutor-perguntas",
    ),
]
