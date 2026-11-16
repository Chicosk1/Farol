"""A porta do módulo ia: o que um adaptador de provedor precisa saber fazer."""

from typing import Protocol


class ProvedorDeIA(Protocol):
    def embeddings(self, textos: list[str]) -> list[list[float]]:
        """Um vetor para cada texto, com o tamanho FAROL_DIMENSAO_DO_VETOR e comprimento 1."""
        ...
