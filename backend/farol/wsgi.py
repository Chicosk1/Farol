"""Ponto de entrada WSGI, usado pelo servidor de aplicação em produção."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "farol.configuracoes.producao")

application = get_wsgi_application()
