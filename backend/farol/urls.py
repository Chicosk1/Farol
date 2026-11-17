"""Rotas do Farol. Cada módulo publica as suas rotas da API em `<modulo>/api/urls.py`."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Administração do Farol"
admin.site.site_title = "Farol"
admin.site.index_title = "Administração"

urlpatterns = [
    path("api/", include("nucleo.api.urls")),
    path("api/", include("contas.api.urls")),
    path("api/", include("disciplinas.api.urls")),
    path("api/", include("materiais.api.urls")),
    path("api/", include("notificacoes.api.urls")),
    path("admin/", admin.site.urls),
]

# O atalho de login só existe onde a configuração o liga (desenvolvimento e teste): em produção,
# a rota nem é registrada (ACE-RNF-03).
if settings.FAROL_LOGIN_DESENVOLVIMENTO:
    urlpatterns.append(path("api/dev/", include("contas.api.urls_desenvolvimento")))
