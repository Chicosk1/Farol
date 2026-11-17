from django.urls import path

from . import views

urlpatterns = [
    path("disciplinas/<int:disciplina_id>/tutor", views.estado, name="tutor"),
    path(
        "disciplinas/<int:disciplina_id>/tutor/perguntas",
        views.perguntar,
        name="tutor-perguntas",
    ),
    path(
        "disciplinas/<int:disciplina_id>/tutor/configuracao",
        views.ConfiguracaoDoTutor.as_view(),
        name="tutor-configuracao",
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
    path("mensagens/<int:mensagem_id>/avaliacao", views.avaliar, name="mensagem-avaliacao"),
]
