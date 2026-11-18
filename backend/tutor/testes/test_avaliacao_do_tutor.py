"""Avaliação automática do tutor (TUT-T13). Com o adaptador falso: confere o caminho e as contas,
não a qualidade do modelo, que só um provedor real mede."""

import io

import pytest
from django.core.management import CommandError, call_command

from disciplinas.models import Disciplina
from materiais.models import Material, Trecho
from tutor.avaliacao import Pergunta
from tutor.avaliacao.avaliar import Relatorio, Resultado
from tutor.models import Conversa

PILHA = Pergunta("O que é uma pilha?", aula=4, pagina=1, resposta="LIFO")
DIJKSTRA = Pergunta("Como funciona o algoritmo de Dijkstra?")


def resultado(pergunta, tipo="resposta", citadas=(), similaridade=0.5):
    return Resultado(pergunta, tipo, "texto", list(citadas), similaridade)


@pytest.mark.requisito("TUT-CS-01")
def test_conta_a_citacao_da_pagina_certa():
    relatorio = Relatorio(
        [
            resultado(PILHA, citadas=[(4, 1)]),
            resultado(PILHA, citadas=[(4, 2), (4, 1)]),
            resultado(PILHA, citadas=[(5, 1)]),
            resultado(PILHA, tipo="nao_encontrado"),
        ]
    )

    assert relatorio.citacoes_corretas == 2
    assert relatorio.taxa_de_citacao == 0.5
    assert not relatorio.metas_atingidas


@pytest.mark.requisito("TUT-CS-03")
def test_conta_as_afirmacoes_sem_citacao():
    relatorio = Relatorio(
        [
            resultado(PILHA, tipo="resposta", citadas=[]),
            resultado(PILHA, tipo="pistas", citadas=[]),
            resultado(PILHA, tipo="nao_encontrado", citadas=[]),
        ]
    )

    assert relatorio.afirmacoes_sem_citacao == 2


@pytest.mark.requisito("TUT-CS-04")
def test_conta_o_nao_encontrei_nas_perguntas_sem_base():
    relatorio = Relatorio(
        [
            resultado(DIJKSTRA, tipo="nao_encontrado"),
            resultado(DIJKSTRA, tipo="resposta", citadas=[(13, 2)]),
        ]
    )

    assert relatorio.taxa_de_nao_encontrei == 0.5


def test_metas_atingidas_quando_as_tres_passam():
    relatorio = Relatorio(
        [resultado(PILHA, citadas=[(4, 1)]), resultado(DIJKSTRA, tipo="nao_encontrado")]
    )

    assert relatorio.metas_atingidas


def test_o_limite_sugerido_separa_as_perguntas_com_e_sem_base():
    relatorio = Relatorio(
        [
            resultado(PILHA, similaridade=0.62),
            resultado(PILHA, similaridade=0.55),
            resultado(DIJKSTRA, similaridade=0.41),
            resultado(DIJKSTRA, similaridade=0.35),
        ]
    )

    assert 0.41 < relatorio.limite_sugerido() < 0.55


def test_o_comando_roda_o_conjunto_inteiro_e_desfaz_tudo(db):
    saida = io.StringIO()

    call_command("avaliar_tutor", "--so-relatorio", stdout=saida)

    texto = saida.getvalue()
    assert "100 perguntas" in texto
    assert "(TUT-CS-01)" in texto
    assert "(TUT-CS-03)" in texto
    assert "(TUT-CS-04)" in texto
    assert "sugerido" in texto
    assert not Disciplina.objects.exists()
    assert not Material.objects.exists()
    assert not Trecho.objects.exists()
    assert not Conversa.objects.exists()


def test_o_limite_faz_so_as_primeiras_perguntas(db):
    saida = io.StringIO()

    call_command("avaliar_tutor", "--limite", "3", "--detalhes", "--so-relatorio", stdout=saida)

    assert "3 perguntas" in saida.getvalue()
    assert "  3. " in saida.getvalue()
    assert "  4. " not in saida.getvalue()


def test_meta_nao_atingida_termina_com_erro(db, monkeypatch):
    monkeypatch.setattr(Relatorio, "metas_atingidas", property(lambda self: False))

    with pytest.raises(CommandError, match="meta"):
        call_command("avaliar_tutor", "--limite", "2", stdout=io.StringIO())
