from django.urls import path

from . import views

urlpatterns = [
    path("materiais/<int:material_id>/geracoes", views.pedir, name="geracoes-da-aula"),
    path("geracoes/<int:pedido_id>", views.geracao, name="geracao"),
]
