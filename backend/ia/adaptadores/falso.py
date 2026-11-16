"""Adaptador falso: vetores previsíveis, sem internet e sem custo (docs/qualidade-e-testes.md).

Cada palavra cai numa posição do vetor, escolhida pelo hash dela, então textos que compartilham
palavras ficam próximos, e textos sem palavras em comum ficam distantes. Serve para testar a
busca por proximidade de verdade, sem chamar um modelo.
"""

import hashlib
import math
import re
import unicodedata

from django.conf import settings

TAMANHO_MINIMO_DA_PALAVRA = 3  # ignora "de", "o", "a", que não dizem do que o texto trata


def _palavras(texto: str) -> list[str]:
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return [
        p
        for p in re.findall(r"[a-z0-9]+", sem_acentos.lower())
        if len(p) >= TAMANHO_MINIMO_DA_PALAVRA
    ]


def _vetor(texto: str, dimensao: int) -> list[float]:
    palavras = _palavras(texto)
    if not palavras:
        raise ValueError("O texto não tem palavras suficientes para gerar o vetor.")
    vetor = [0.0] * dimensao
    for palavra in palavras:
        posicao = int(hashlib.sha256(palavra.encode()).hexdigest()[:8], 16) % dimensao
        vetor[posicao] += 1.0
    comprimento = math.sqrt(sum(x * x for x in vetor))
    return [x / comprimento for x in vetor]


class ProvedorFalso:
    def embeddings(self, textos: list[str]) -> list[list[float]]:
        return [_vetor(texto, settings.FAROL_DIMENSAO_DO_VETOR) for texto in textos]
