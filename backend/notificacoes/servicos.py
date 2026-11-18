"""Notificações das pessoas. Os outros módulos avisam por notificar() (ADR 0007)."""

from .models import Notificacao

Tipo = Notificacao.Tipo
QUANTAS_NA_LISTA = 50


class NotificacaoNaoEncontrada(LookupError):
    """A notificação não existe ou é de outra pessoa."""


def notificar(pessoa, tipo: str, texto: str, link: str = "") -> Notificacao:
    """Cria o aviso para a pessoa; ele aparece no sino até ser marcado como lido."""
    return Notificacao.objects.create(pessoa=pessoa, tipo=tipo, texto=texto, link=link)


def notificacoes_de(pessoa) -> tuple[list[Notificacao], int]:
    """As notificações mais recentes da pessoa e quantas ainda não foram lidas."""
    minhas = Notificacao.objects.filter(pessoa=pessoa)
    return list(minhas[:QUANTAS_NA_LISTA]), minhas.filter(lida=False).count()


def marcar_como_lida(pessoa, notificacao_id: int) -> None:
    atualizadas = Notificacao.objects.filter(id=notificacao_id, pessoa=pessoa).update(lida=True)
    if not atualizadas:
        raise NotificacaoNaoEncontrada(notificacao_id)
