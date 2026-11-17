from django.urls import path

from . import views

urlpatterns = [
    path("notificacoes", views.listar, name="notificacoes"),
    path(
        "notificacoes/<int:notificacao_id>/lida",
        views.marcar_como_lida,
        name="notificacao-lida",
    ),
]
