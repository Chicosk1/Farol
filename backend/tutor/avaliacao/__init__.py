"""Conjunto de avaliação do tutor (TUT-T12, TUT-CS-01, TUT-CS-04).

Cada conjunto é um JSON com o material da disciplina, aula por aula e página por página, e as
perguntas: as que têm base no material dizem a aula e a página que a resposta deve citar; as sem
base (`sem_base`) esperam "Não encontrei isso no material da disciplina.". Os dados são fictícios.
"""

import json
from dataclasses import dataclass
from pathlib import Path

PASTA = Path(__file__).parent
CONJUNTO_PADRAO = "estruturas_de_dados"


@dataclass(frozen=True)
class Aula:
    numero: int
    titulo: str
    paginas: list[str]


@dataclass(frozen=True)
class Pergunta:
    texto: str
    aula: int | None = None  # None nas perguntas sem base no material
    pagina: int | None = None
    resposta: str = ""

    @property
    def sem_base(self) -> bool:
        return self.aula is None


@dataclass(frozen=True)
class Conjunto:
    disciplina: str
    aulas: list[Aula]
    perguntas: list[Pergunta]


def carregar(nome: str = CONJUNTO_PADRAO) -> Conjunto:
    dados = json.loads((PASTA / f"{nome}.json").read_text(encoding="utf-8"))
    return Conjunto(
        disciplina=dados["disciplina"],
        aulas=[Aula(a["numero"], a["titulo"], list(a["paginas"])) for a in dados["aulas"]],
        perguntas=[
            Pergunta(texto=p["pergunta"])
            if p.get("sem_base")
            else Pergunta(p["pergunta"], p["aula"], p["pagina"], p.get("resposta", ""))
            for p in dados["perguntas"]
        ],
    )
