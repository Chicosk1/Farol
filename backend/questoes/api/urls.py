from django.urls import path

from . import views

urlpatterns = [
    path("materiais/<int:material_id>/geracoes", views.pedir, name="geracoes-da-aula"),
    path("geracoes/<int:pedido_id>", views.geracao, name="geracao"),
    path(
        "disciplinas/<int:disciplina_id>/questoes",
        views.da_disciplina,
        name="questoes-da-disciplina",
    ),
    path("questoes/<int:questao_id>", views.mudar, name="questao"),
]
