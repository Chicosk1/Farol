"""Rotas do Farol. Cada módulo publica as suas rotas da API em `<modulo>/api/urls.py`."""

from django.urls import include, path

urlpatterns = [
    path("api/", include("nucleo.api.urls")),
]
