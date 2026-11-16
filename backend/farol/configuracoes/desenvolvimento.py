"""Configurações do ambiente de desenvolvimento (Docker Compose). Padrão do manage.py."""

from . import ambiente
from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = ambiente.opcional("DJANGO_SECRET_KEY", "desenvolvimento-inseguro-nao-use-em-producao")

ALLOWED_HOSTS = ambiente.lista(ambiente.opcional("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,backend"))
