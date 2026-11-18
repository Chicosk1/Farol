from django.urls import path

from . import views

urlpatterns = [
    path("disciplinas/<int:disciplina_id>/radar", views.radar, name="radar"),
    path("disciplinas/<int:disciplina_id>/radar/semanas", views.semanas, name="radar-semanas"),
    path(
        "disciplinas/<int:disciplina_id>/radar/exemplos-ocultos",
        views.ocultar_exemplo,
        name="radar-exemplos-ocultos",
    ),
]
