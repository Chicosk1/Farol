from django.urls import path

from . import views

urlpatterns = [
    path("mensagens/<int:mensagem_id>/duvida/previa", views.previa, name="duvida-previa"),
    path("mensagens/<int:mensagem_id>/duvida", views.enviar, name="duvida"),
    path(
        "disciplinas/<int:disciplina_id>/duvidas",
        views.da_disciplina,
        name="duvidas-da-disciplina",
    ),
]
