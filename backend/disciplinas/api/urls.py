from django.urls import path

from . import views

urlpatterns = [
    path("disciplinas", views.listar, name="disciplinas"),
    path("disciplinas/<int:disciplina_id>/favorito", views.favorito, name="favorito"),
    path("importacoes", views.enviar_importacao, name="importacoes"),
    path("importacoes/<int:importacao_id>", views.ver_importacao, name="importacao"),
]
