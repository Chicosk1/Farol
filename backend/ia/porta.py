"""A porta do módulo ia: o que um adaptador de provedor precisa saber fazer."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TrechoNumerado:
    """Um trecho do material enviado ao modelo, com o número que a resposta usa para citá-lo."""

    numero: int
    texto: str


@dataclass(frozen=True)
class EventoTexto:
    """Um pedaço da resposta, que chega aos poucos (streaming)."""

    texto: str


@dataclass(frozen=True)
class EventoFim:
    """O fim da resposta, com o uso do modelo, para o controle de custo."""

    tokens_entrada: int
    tokens_saida: int


EventoResposta = EventoTexto | EventoFim


class ProvedorDeIA(Protocol):
    def embeddings(self, textos: list[str]) -> list[list[float]]:
        """Um vetor para cada texto, com o tamanho FAROL_DIMENSAO_DO_VETOR e comprimento 1."""
        ...

    def responder(
        self, regras: str, trechos: list[TrechoNumerado], pergunta: str
    ) -> Iterator[EventoResposta]:
        """A resposta em streaming, citando os trechos pelo número entre colchetes, como [1]."""
        ...
