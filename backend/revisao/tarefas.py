"""Tarefas do Celery do módulo revisao. Finas: só chamam serviços (ADR 0007)."""

from celery import shared_task

from . import servicos


@shared_task(name="revisao.montar_sessoes")
def montar_sessoes() -> int:
    return servicos.montar_sessoes_do_dia()


@shared_task(name="revisao.enviar_lembretes")
def enviar_lembretes() -> int:
    return servicos.enviar_lembretes()
