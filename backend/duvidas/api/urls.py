from django.urls import path

from . import views

urlpatterns = [
    path("mensagens/<int:mensagem_id>/duvida/previa", views.previa, name="duvida-previa"),
    path("mensagens/<int:mensagem_id>/duvida", views.enviar, name="duvida"),
]
