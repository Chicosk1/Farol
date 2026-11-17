"""Rotas só de desenvolvimento e de teste. farol/urls.py só as registra com
FAROL_LOGIN_DESENVOLVIMENTO ligado (ACE-RNF-03)."""

from django.urls import path

from . import views

urlpatterns = [
    path("entrar", views.entrar_em_desenvolvimento, name="dev-entrar"),
]
