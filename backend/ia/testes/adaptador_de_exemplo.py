"""Adaptador mínimo para testar a troca de adaptador pela configuração."""

from django.conf import settings


class Constante:
    def embeddings(self, textos: list[str]) -> list[list[float]]:
        return [[1.0] + [0.0] * (settings.FAROL_DIMENSAO_DO_VETOR - 1) for _ in textos]
