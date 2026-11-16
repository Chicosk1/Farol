"""Ponto de entrada ASGI, para quando o chat do tutor precisar de streaming (spec 003)."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "farol.configuracoes.producao")

application = get_asgi_application()
