"""Tarefas do Celery do módulo disciplinas. Finas: só chamam serviços (ADR 0007)."""

from celery import shared_task

from . import servicos


@shared_task(name="disciplinas.processar_importacao")
def processar_importacao(importacao_id: int) -> str:
    """Importa o CSV de turmas em segundo plano e devolve o status final."""
    return servicos.processar_importacao(importacao_id).status
