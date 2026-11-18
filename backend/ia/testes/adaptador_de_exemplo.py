"""Adaptador mínimo para testar a troca de adaptador pela configuração."""

from django.conf import settings


class Constante:
    finalidades: list[str] = []  # o que cada pedido de vetores informou, para os testes conferirem

    def embeddings(self, textos: list[str], finalidade: str = "trecho") -> list[list[float]]:
        Constante.finalidades.append(finalidade)
        return [[1.0] + [0.0] * (settings.FAROL_DIMENSAO_DO_VETOR - 1) for _ in textos]
