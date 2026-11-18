"""Roda o conjunto de perguntas no tutor e calcula as métricas das metas (TUT-T13).

- TUT-CS-01: pelo menos 90% das respostas com base no material citam a página esperada.
- TUT-CS-03: nenhuma resposta sem citação é apresentada como afirmação.
- TUT-CS-04: todas as perguntas sem base recebem "Não encontrei isso no material da disciplina.".

Também mede a maior similaridade da busca de cada pergunta, para calibrar o limite do tutor.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from ia import servicos as ia
from materiais import servicos as materiais
from tutor import servicos

from . import Pergunta

META_DE_CITACAO = 0.9  # TUT-CS-01
META_DE_NAO_ENCONTREI = 1.0  # TUT-CS-04
TIPOS_DE_AFIRMACAO = {"resposta", "pistas"}


@dataclass(frozen=True)
class Resultado:
    pergunta: Pergunta
    tipo: str
    texto: str
    citadas: list[tuple[int, int]] = field(default_factory=list)  # (aula, página)
    similaridade: float = 0.0  # a maior similaridade da busca, de 0 a 1

    @property
    def cita_a_pagina_certa(self) -> bool:
        return (self.pergunta.aula, self.pergunta.pagina) in self.citadas

    @property
    def afirmacao_sem_citacao(self) -> bool:
        return self.tipo in TIPOS_DE_AFIRMACAO and not self.citadas


@dataclass
class Relatorio:
    resultados: list[Resultado]

    @property
    def com_base(self) -> list[Resultado]:
        return [r for r in self.resultados if not r.pergunta.sem_base]

    @property
    def sem_base(self) -> list[Resultado]:
        return [r for r in self.resultados if r.pergunta.sem_base]

    @property
    def citacoes_corretas(self) -> int:
        return sum(r.cita_a_pagina_certa for r in self.com_base)

    @property
    def afirmacoes_sem_citacao(self) -> int:
        return sum(r.afirmacao_sem_citacao for r in self.resultados)

    @property
    def nao_encontrei_sem_base(self) -> int:
        return sum(r.tipo == "nao_encontrado" for r in self.sem_base)

    @property
    def taxa_de_citacao(self) -> float:
        return self.citacoes_corretas / len(self.com_base) if self.com_base else 1.0

    @property
    def taxa_de_nao_encontrei(self) -> float:
        return self.nao_encontrei_sem_base / len(self.sem_base) if self.sem_base else 1.0

    @property
    def metas_atingidas(self) -> bool:
        return (
            self.taxa_de_citacao >= META_DE_CITACAO
            and self.afirmacoes_sem_citacao == 0
            and self.taxa_de_nao_encontrei >= META_DE_NAO_ENCONTREI
        )

    def limite_sugerido(self) -> float | None:
        """O limite de similaridade que mais separa as perguntas com base das sem base.

        Conta, para cada candidato, quantas com base ficam acima dele e quantas sem base ficam
        abaixo. No empate, fica o meio do intervalo, para sobrar margem dos dois lados.
        """
        com = [r.similaridade for r in self.com_base]
        sem = [r.similaridade for r in self.sem_base]
        if not com or not sem:
            return None
        valores = sorted(set(com + sem))
        candidatos = [(a + b) / 2 for a, b in zip(valores, valores[1:], strict=False)]
        if not candidatos:
            return None

        def acertos(limite: float) -> int:
            return sum(s >= limite for s in com) + sum(s < limite for s in sem)

        melhor = max(acertos(c) for c in candidatos)
        empatados = [c for c in candidatos if acertos(c) == melhor]
        return round((empatados[0] + empatados[-1]) / 2, 3)


def _maior_similaridade(disciplina_id: int, pergunta: str) -> float:
    try:
        vetor = ia.gerar_embedding_da_pergunta(pergunta)
    except ValueError:  # o adaptador falso recusa perguntas sem palavras úteis
        return 0.0
    trechos = materiais.buscar_trechos(disciplina_id, vetor, limite=1)
    return trechos[0].similaridade if trechos else 0.0


def responder(disciplina_id: int, pergunta: Pergunta) -> Resultado:
    """Faz a pergunta ao tutor, como o aluno faria, sem guardar conversa."""
    citadas: list[tuple[int, int]] = []
    fim = None
    for evento in servicos.responder_pergunta(disciplina_id, pergunta.texto, modo_pistas=False):
        if isinstance(evento, servicos.Citacao):
            citadas.append((evento.aula_numero, evento.pagina))
        elif isinstance(evento, servicos.Fim):
            fim = evento
    return Resultado(
        pergunta=pergunta,
        tipo=fim.tipo if fim else "erro",
        texto=fim.texto if fim else "",
        citadas=citadas,
        similaridade=_maior_similaridade(disciplina_id, pergunta.texto),
    )


def avaliar(
    disciplina_id: int,
    perguntas: list[Pergunta],
    ao_responder: Callable[[int, Resultado], None] | None = None,
) -> Relatorio:
    resultados = []
    for numero, pergunta in enumerate(perguntas, start=1):
        resultado = responder(disciplina_id, pergunta)
        resultados.append(resultado)
        if ao_responder:
            ao_responder(numero, resultado)
    return Relatorio(resultados)
