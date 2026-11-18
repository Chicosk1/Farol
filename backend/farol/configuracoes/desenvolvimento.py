"""Configurações do ambiente de desenvolvimento (Docker Compose). Padrão do manage.py."""

from . import ambiente
from .base import *  # noqa: F403

DEBUG = True

FAROL_LOGIN_DESENVOLVIMENTO = True

SECRET_KEY = ambiente.opcional("DJANGO_SECRET_KEY", "desenvolvimento-inseguro-nao-use-em-producao")

ALLOWED_HOSTS = ambiente.lista(
    ambiente.opcional("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,backend")
)

# No computador de desenvolvimento, o padrão é o adaptador falso com as aulas da demonstração, que
# são páginas longas: o limite de 0,3, calibrado com os trechos curtos dos testes, fazia o tutor
# responder "não encontrei" até para o que está no material. O avaliar_tutor sugere 0,17 para o
# falso; com o Ollama, o .env.exemplo traz 0,35 (TUT-T18).
FAROL_TUTOR_SIMILARIDADE_MINIMA = ambiente.fracao("FAROL_TUTOR_SIMILARIDADE_MINIMA", "0.15")
