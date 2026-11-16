"""Projeto Django do Farol: configurações, rotas, pontos de entrada (WSGI e ASGI) e o app do Celery."""

# Carrega o Celery junto com o Django, para que as tarefas usem as mesmas configurações.
from .celery import app as celery_app

__all__ = ("celery_app",)
