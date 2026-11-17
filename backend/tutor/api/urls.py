from django.urls import path

from . import views

urlpatterns = [
    path(
        "disciplinas/<int:disciplina_id>/tutor/perguntas",
        views.perguntar,
        name="tutor-perguntas",
    ),
    path(
        "disciplinas/<int:disciplina_id>/janelas-prova",
        views.JanelasDeProva.as_view(),
        name="janelas-prova",
    ),
    path(
        "disciplinas/<int:disciplina_id>/janelas-prova/<int:janela_id>",
        views.apagar_janela,
        name="janela-prova",
    ),
]
