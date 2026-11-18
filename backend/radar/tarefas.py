"""Tarefas do Celery do módulo radar. Finas: só chamam serviços (ADR 0007)."""

from celery import shared_task

from . import servicos


@shared_task(name="radar.calcular")
def calcular() -> int:
    return servicos.calcular_todos()


@shared_task(name="radar.enviar_resumos")
def enviar_resumos() -> int:
    return servicos.enviar_resumos()
