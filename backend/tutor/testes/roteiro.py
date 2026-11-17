"""Provedor de IA roteirizado para os testes do tutor: responde o texto que o teste mandar.

Guarda as regras, os trechos e a pergunta que recebeu, para os testes conferirem o prompt.
"""

from ia.adaptadores.falso import ProvedorFalso
from ia.porta import EventoFim, EventoTexto

RESPOSTA: list[str] = []  # pedaços da próxima resposta
CHAMADAS: list[dict] = []


def preparar(*pedacos: str) -> None:
    RESPOSTA[:] = list(pedacos)
    CHAMADAS.clear()


class ProvedorRoteirizado(ProvedorFalso):
    def responder(self, regras, trechos, pergunta):
        CHAMADAS.append({"regras": regras, "trechos": list(trechos), "pergunta": pergunta})
        for pedaco in RESPOSTA:
            yield EventoTexto(pedaco)
        yield EventoFim(tokens_entrada=1000, tokens_saida=100)
