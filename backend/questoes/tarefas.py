"""Tarefas do Celery do módulo questoes. Finas: só chamam serviços (ADR 0007)."""

from celery import shared_task

from . import servicos


@shared_task(name="questoes.gerar")
def gerar(pedido_id: int) -> str:
    """Gera os rascunhos do pedido em segundo plano e devolve o status final."""
    return servicos.processar_pedido(pedido_id).status
