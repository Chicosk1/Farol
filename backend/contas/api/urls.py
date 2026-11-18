from django.urls import path

from . import views

urlpatterns = [
    path("entrada", views.formas_de_entrar, name="formas-de-entrar"),
    path("eu", views.eu, name="eu"),
    path("eu/perfil-ativo", views.perfil_ativo, name="perfil-ativo"),
    path("sair", views.sair, name="sair"),
    path("aviso-privacidade", views.aviso_de_privacidade, name="aviso-privacidade"),
    path("eu/ciencia-privacidade", views.ciencia_de_privacidade, name="ciencia-privacidade"),
]
