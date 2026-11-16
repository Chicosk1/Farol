"""Configurações de produção. Tudo o que é sensível vem de variáveis de ambiente obrigatórias:
sem elas, o Django não sobe e diz qual variável falta.
"""

from . import ambiente
from .base import *  # noqa: F403
from .base import DATABASES

DEBUG = False

# Em produção, a única forma de entrar é o login institucional (ACE-RNF-03).
# Fixo no código, de propósito: nenhuma variável de ambiente liga o atalho.
FAROL_LOGIN_DESENVOLVIMENTO = False

SECRET_KEY = ambiente.obrigatoria("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = ambiente.lista(ambiente.obrigatoria("DJANGO_ALLOWED_HOSTS"))

DATABASES = {
    "default": {
        **DATABASES["default"],
        "NAME": ambiente.obrigatoria("POSTGRES_DB"),
        "USER": ambiente.obrigatoria("POSTGRES_USER"),
        "PASSWORD": ambiente.obrigatoria("POSTGRES_PASSWORD"),
        "HOST": ambiente.obrigatoria("POSTGRES_HOST"),
    }
}
