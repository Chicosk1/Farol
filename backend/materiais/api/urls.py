from django.urls import path

from . import views

urlpatterns = [
    path(
        "disciplinas/<int:disciplina_id>/materiais",
        views.MateriaisDaDisciplina.as_view(),
        name="materiais",
    ),
    path("materiais/<int:material_id>/arquivo", views.arquivo, name="material-arquivo"),
    path("materiais/<int:material_id>", views.retirar, name="material"),
    path("materiais/<int:material_id>/versoes", views.nova_versao, name="material-versoes"),
]
