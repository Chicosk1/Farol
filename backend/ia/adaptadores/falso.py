"""Adaptador falso: vetores previsíveis, sem internet e sem custo (docs/qualidade-e-testes.md).

Cada palavra cai numa posição do vetor, escolhida pelo hash dela, então textos que compartilham
palavras ficam próximos, e textos sem palavras em comum ficam distantes. Serve para testar a
busca por proximidade de verdade, sem chamar um modelo.
"""

import hashlib
import json
import math
import re
import unicodedata
from collections.abc import Iterator

from django.conf import settings

from ..porta import EventoFim, EventoResposta, EventoTexto, TrechoNumerado

TAMANHO_MINIMO_DA_PALAVRA = 3  # ignora "de", "o", "a", que não dizem do que o texto trata
# Palavras comuns que não dizem do que o texto trata. "nós" (nodos) fica de fora de propósito.
PALAVRAS_COMUNS = frozenset(
    [
        *("uma", "uns", "umas", "que", "com", "para", "por", "pelo", "pela", "dos", "das"),
        *("mais", "como", "qual", "quais", "isso", "esse", "essa", "este", "esta", "sao"),
        *("foi", "ser", "tem", "cada", "sobre", "entre", "quando", "onde", "seu", "sua"),
    ]
)


def _palavras(texto: str) -> list[str]:
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return [
        p
        for p in re.findall(r"[a-z0-9]+", sem_acentos.lower())
        if len(p) >= TAMANHO_MINIMO_DA_PALAVRA and p not in PALAVRAS_COMUNS
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
    def embeddings(self, textos: list[str], finalidade: str = "trecho") -> list[list[float]]:
        # O falso não usa instruções de busca: pergunta e trecho geram o vetor do mesmo jeito.
        return [_vetor(texto, settings.FAROL_DIMENSAO_DO_VETOR) for texto in textos]


PEDIDO_DE_EXERCICIO = re.compile(
    r"resposta d[oa]|resolv|me d[aá] a (?:resposta|solu)|gabarito|c[oó]digo d[oa] exerc",
    re.IGNORECASE,
)
PALAVRAS_POR_PEDACO = 4  # o streaming do falso entrega a resposta em pedaços pequenos


def _frases(texto: str) -> list[str]:
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto) if f.strip()]


def _sobreposicao(frase: str, pergunta: str) -> int:
    return len(set(_palavras(frase)) & set(_palavras(pergunta)))


class _Respostas:
    """Monta a resposta só com frases dos trechos recebidos, citando o número de cada um."""

    def montar(self, regras: str, trechos: list[TrechoNumerado], pergunta: str) -> str:
        pistas = "MODO PISTAS" in regras and PEDIDO_DE_EXERCICIO.search(pergunta)
        candidatos = []
        for trecho in trechos:
            frases = _frases(trecho.texto)
            melhor = max(frases, key=lambda f: _sobreposicao(f, pergunta), default="")
            if _sobreposicao(melhor, pergunta) > 0:
                candidatos.append((trecho, melhor))
        if pistas and candidatos:
            numero = candidatos[0][0].numero
            return (
                f"[PISTAS] Vamos por etapas: releia o trecho [{numero}] e me diga qual é o "
                "primeiro passo para resolver o exercício."
            )
        if not candidatos:  # o servidor só chama o modelo com trechos relevantes; por segurança
            return f"Veja o trecho [{trechos[0].numero}]."
        return " ".join(f"{frase} [{trecho.numero}]" for trecho, frase in candidatos)


def _responder(
    regras: str, trechos: list[TrechoNumerado], pergunta: str
) -> Iterator[EventoResposta]:
    texto = _Respostas().montar(regras, trechos, pergunta)
    palavras = texto.split(" ")
    for i in range(0, len(palavras), PALAVRAS_POR_PEDACO):
        pedaco = " ".join(palavras[i : i + PALAVRAS_POR_PEDACO])
        yield EventoTexto(pedaco if i == 0 else " " + pedaco)
    entrada = regras + pergunta + "".join(t.texto for t in trechos)
    yield EventoFim(tokens_entrada=max(1, len(entrada) // 4), tokens_saida=max(1, len(texto) // 4))


ProvedorFalso.responder = lambda self, regras, trechos, pergunta: _responder(  # type: ignore[attr-defined]
    regras, trechos, pergunta
)


# Alternativas erradas de reserva, quando a aula tem poucos trechos para servir de distrator.
DISTRATORES = (
    "O material da aula não trata deste assunto.",
    "Todas as outras alternativas estão corretas.",
    "Isso só vale quando os dados já estão ordenados.",
)
TAMANHO_DA_ALTERNATIVA = 300


def _alternativa(frase: str) -> str:
    if len(frase) <= TAMANHO_DA_ALTERNATIVA:
        return frase
    return frase[: TAMANHO_DA_ALTERNATIVA - 1].rstrip() + "…"


def _topico(frase: str) -> str:
    """As três primeiras palavras da frase: basta para agrupar as questões no falso."""
    palavras = re.findall(r"[^\W_]+", frase)
    return " ".join(palavras[:3]).capitalize() or "Material da aula"


def _gerar_questoes(trechos: list[TrechoNumerado], quantidade: int) -> str:
    """Questões montadas só com frases dos trechos: a correta sai do trecho citado, e as erradas,
    dos outros trechos ou da reserva. O resultado é sempre o mesmo para a mesma entrada."""
    principais = []
    for trecho in trechos:
        frases = _frases(trecho.texto) or [trecho.texto.strip()]
        principais.append((trecho, _alternativa(frases[0])))
    questoes = []
    for i in range(quantidade):
        trecho, certa = principais[i % len(principais)]
        erradas: list[str] = []
        for candidata in [f for _, f in principais] + list(DISTRATORES):
            if candidata.casefold() != certa.casefold() and candidata not in erradas:
                erradas.append(candidata)
        erradas = erradas[:3]
        correta = (trecho.numero + i) % 4
        alternativas = erradas[:correta] + [certa] + erradas[correta:]
        questoes.append(
            {
                "enunciado": f"Questão {i + 1}: de acordo com a aula, qual afirmação está correta?",
                "alternativas": alternativas,
                "correta": correta,
                "justificativa": f"O trecho [{trecho.numero}] do material diz: {certa}",
                "topico": _topico(certa),
                "trecho": trecho.numero,
            }
        )
    return json.dumps({"questoes": questoes}, ensure_ascii=False)


ProvedorFalso.gerar_questoes = lambda self, regras, trechos, quantidade: _gerar_questoes(  # type: ignore[attr-defined]
    trechos, quantidade
)
