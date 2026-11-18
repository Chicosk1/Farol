from django.urls import path

from . import views

urlpatterns = [
    path("revisao/hoje", views.hoje, name="revisao-de-hoje"),
    path("revisao/cartoes/<int:cartao_id>/resposta", views.responder, name="resposta-do-cartao"),
    path("revisao/cartoes/<int:cartao_id>/avaliacao", views.avaliar, name="avaliacao-do-cartao"),
    path("eu/lembrete", views.lembrete, name="lembrete"),
]
