"""Serviços do módulo ia: a única entrada para o provedor de IA."""

from collections.abc import Iterator

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .porta import EventoFim as EventoFim  # reexportados: os outros módulos usam os tipos
from .porta import EventoResposta, ProvedorDeIA, TrechoNumerado
from .porta import EventoTexto as EventoTexto


def _provedor() -> ProvedorDeIA:
    caminho = settings.FAROL_IA["ADAPTADOR"]
    try:
        return import_string(caminho)()
    except ImportError as erro:
        raise ImproperlyConfigured(f"O adaptador de IA {caminho!r} não existe: {erro}") from erro


def gerar_embeddings(textos: list[str]) -> list[list[float]]:
    """Os vetores de busca de vários textos, na mesma ordem."""
    if any(not texto.strip() for texto in textos):
        raise ValueError("Não dá para gerar o vetor de um texto vazio.")
    return _provedor().embeddings(textos)


def gerar_embedding(texto: str) -> list[float]:
    """O vetor de busca de um texto (MAT-RF-04, TUT-RF-01)."""
    return gerar_embeddings([texto])[0]


def responder(
    regras: str, trechos: list[TrechoNumerado], pergunta: str
) -> Iterator[EventoResposta]:
    """A resposta do modelo, em streaming, com as regras fixas, os trechos numerados e a pergunta.

    Só se chama o modelo quando há trechos: sem eles, o tutor responde "não encontrei" sozinho
    (TUT-RF-04), o que também economiza custo.
    """
    if not trechos:
        raise ValueError("Sem trechos do material, o modelo não deve ser chamado.")
    if not pergunta.strip():
        raise ValueError("A pergunta está vazia.")
    return _provedor().responder(regras, trechos, pergunta)
