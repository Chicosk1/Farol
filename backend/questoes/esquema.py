"""O formato das questões que o modelo devolve, conferido antes de virar rascunho (QUE-RF-03).

Cada questão é validada sozinha: uma questão fora do formato, ou citando um trecho que não foi
enviado, é descartada, e as outras seguem.
"""

import json
import re
from dataclasses import dataclass
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
)


def _texto(minimo: int, maximo: int):
    return Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=minimo, max_length=maximo)
    ]


class QuestaoGerada(BaseModel):
    model_config = ConfigDict(extra="ignore")

    enunciado: _texto(10, 1000)
    alternativas: list[_texto(1, 300)] = Field(min_length=4, max_length=4)
    correta: int = Field(ge=0, le=3)
    justificativa: _texto(10, 1500)
    topico: _texto(2, 120)
    trecho: int = Field(ge=1)

    @field_validator("alternativas")
    @classmethod
    def sem_alternativas_repetidas(cls, alternativas: list[str]) -> list[str]:
        if len({a.casefold() for a in alternativas}) != len(alternativas):
            raise ValueError("Há alternativas repetidas.")
        return alternativas


@dataclass(frozen=True)
class Leitura:
    aceitas: list[QuestaoGerada]
    descartadas: int


# Alguns modelos cercam o JSON com ```json ... ```, mesmo quando se pede só o JSON.
CERCA = re.compile(r"^```(?:json)?\s*|\s*```$")


def ler_questoes(texto: str, trechos_enviados: set[int], limite: int) -> Leitura:
    """As questões válidas, até o limite pedido, e quantas foram descartadas.

    JSON ilegível conta como o pedido inteiro descartado. Questões além do limite são ignoradas.
    """
    try:
        dados = json.loads(CERCA.sub("", texto.strip()))
    except json.JSONDecodeError:
        return Leitura([], limite)
    itens = dados.get("questoes") if isinstance(dados, dict) else dados
    if not isinstance(itens, list):
        return Leitura([], limite)
    aceitas: list[QuestaoGerada] = []
    descartadas = 0
    for item in itens:
        if len(aceitas) == limite:
            break
        try:
            questao = QuestaoGerada.model_validate(item)
        except ValidationError:
            descartadas += 1
            continue
        if questao.trecho not in trechos_enviados:  # trecho de origem inválido (QUE-RF-03)
            descartadas += 1
            continue
        aceitas.append(questao)
    return Leitura(aceitas, descartadas)
