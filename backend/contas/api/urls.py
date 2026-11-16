from django.urls import path

from . import views

urlpatterns = [
    path("eu", views.eu, name="eu"),
    path("eu/perfil-ativo", views.perfil_ativo, name="perfil-ativo"),
    path("sair", views.sair, name="sair"),
]
