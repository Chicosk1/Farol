"""Tarefas do Celery do módulo tutor. Finas: só chamam serviços (ADR 0007)."""

from celery import shared_task

from . import servicos


@shared_task(name="tutor.verificar_orcamento")
def verificar_orcamento() -> int:
    """Uma vez por dia: avisa a equipe das disciplinas acima do orçamento de IA no mês."""
    return servicos.verificar_orcamento()
