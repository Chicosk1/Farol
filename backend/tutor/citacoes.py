"""Conversão das marcações de trecho em citações (TUT-RF-02 e TUT-RF-03). Sem banco.

O modelo marca cada afirmação com o número do trecho em que ela se apoia, como [2]. Aqui, a
resposta que chega em pedaços (streaming) é separada em frases; só passam as frases com pelo menos
uma marcação válida, e as marcações são renumeradas na ordem em que as citações aparecem.
"""

import re

MARCACAO = re.compile(r"\[(\d+)\]")
# Fim de frase: pontuação final, as marcações que vierem logo depois, e o começo da próxima frase.
FRONTEIRA = re.compile(r"[.!?](?:\s*\[\d+\])*(?=\s+[^\s\[])")


class ConversorDeCitacoes:
    def __init__(self, trechos_validos: set[int]):
        self._validos = trechos_validos
        self._pendente = ""
        self._ordem: dict[int, int] = {}  # número do trecho no prompt -> número da citação

    @property
    def citados(self) -> list[int]:
        """Os números dos trechos citados, na ordem das citações."""
        return list(self._ordem)

    def receber(self, pedaco: str) -> list[str]:
        """Recebe um pedaço da resposta e devolve as frases completas que podem ser mostradas."""
        self._pendente += pedaco
        frases = []
        inicio = 0
        for fronteira in FRONTEIRA.finditer(self._pendente):
            frases.append(self._pendente[inicio : fronteira.end()])
            inicio = fronteira.end()
        self._pendente = self._pendente[inicio:]
        return [convertida for frase in frases if (convertida := self._converter(frase))]

    def terminar(self) -> list[str]:
        """Devolve a última frase, se ela puder ser mostrada."""
        frase, self._pendente = self._pendente, ""
        convertida = self._converter(frase)
        return [convertida] if convertida else []

    def _converter(self, frase: str) -> str | None:
        numeros = [int(n) for n in MARCACAO.findall(frase) if int(n) in self._validos]
        if not numeros:
            return None  # afirmação sem citação não é apresentada (TUT-RF-03)
        for numero in numeros:
            self._ordem.setdefault(numero, len(self._ordem) + 1)

        def renumerar(marcacao: re.Match) -> str:
            numero = int(marcacao.group(1))
            return f"[{self._ordem[numero]}]" if numero in self._validos else ""

        return re.sub(r"\s{2,}", " ", MARCACAO.sub(renumerar, frase)).strip()
