"""Tarefas do Celery do módulo materiais. Finas: só chamam serviços (ADR 0007)."""

from celery import shared_task

from . import servicos


@shared_task(name="materiais.processar")
def processar(material_id: int) -> str:
    """Processa o PDF em segundo plano e devolve o status final do material."""
    return servicos.processar_material(material_id).status
