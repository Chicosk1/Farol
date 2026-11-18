"""Módulo ia: a porta única para o provedor de IA e o adaptador falso dos testes (MAT-T13).

Os testes nunca acessam a internet nem geram custo: usam sempre o adaptador falso
(docs/qualidade-e-testes.md). Dados fictícios.
"""

import math

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from ia import servicos

DIM = settings.FAROL_DIMENSAO_DO_VETOR


def cosseno(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))  # os vetores já são unitários


def test_o_vetor_tem_o_tamanho_do_banco_e_comprimento_1():
    vetor = servicos.gerar_embedding("Uma lista encadeada é uma sequência de nós.")

    assert len(vetor) == DIM
    assert math.isclose(math.sqrt(sum(x * x for x in vetor)), 1.0, rel_tol=1e-9)


def test_o_mesmo_texto_gera_sempre_o_mesmo_vetor():
    texto = "Pilhas seguem a ordem LIFO."

    assert servicos.gerar_embedding(texto) == servicos.gerar_embedding(texto)


def test_acentos_maiusculas_e_pontuacao_nao_mudam_o_vetor():
    assert servicos.gerar_embedding("Árvores binárias!") == servicos.gerar_embedding(
        "arvores   BINARIAS"
    )


def test_textos_parecidos_ficam_mais_proximos_que_textos_diferentes():
    lista = servicos.gerar_embedding("lista encadeada de nós com ponteiros")
    parecido = servicos.gerar_embedding("os nós da lista encadeada apontam para o próximo")
    diferente = servicos.gerar_embedding("banco de dados relacional e chaves estrangeiras")

    assert cosseno(lista, parecido) > 0.3
    assert cosseno(lista, diferente) < 0.15
    assert cosseno(lista, parecido) > cosseno(lista, diferente)


def test_gerar_varios_de_uma_vez_da_o_mesmo_resultado_que_um_por_um():
    textos = ["lista encadeada", "pilha e fila", "árvore binária"]

    assert servicos.gerar_embeddings(textos) == [servicos.gerar_embedding(t) for t in textos]


@pytest.mark.parametrize("texto", ["", "   ", "\n", "a b"])
def test_texto_sem_palavras_uteis_e_recusado_em_vez_de_gerar_vetor_nulo(texto):
    with pytest.raises(ValueError, match="texto"):
        servicos.gerar_embedding(texto)


def test_o_adaptador_vem_da_configuracao_e_pode_ser_trocado():
    with override_settings(FAROL_IA={"ADAPTADOR": "ia.testes.adaptador_de_exemplo.Constante"}):
        assert servicos.gerar_embedding("qualquer coisa")[0] == 1.0


@pytest.mark.requisito("TUT-RF-01")
def test_o_vetor_da_pergunta_e_pedido_com_a_finalidade_pergunta_e_o_do_trecho_com_trecho():
    """Modelos como o embeddinggemma buscam melhor quando sabem o que é cada texto (TUT-T17)."""
    from ia.testes import adaptador_de_exemplo

    adaptador_de_exemplo.Constante.finalidades.clear()
    with override_settings(FAROL_IA={"ADAPTADOR": "ia.testes.adaptador_de_exemplo.Constante"}):
        servicos.gerar_embedding_da_pergunta("O que é uma pilha?")
        servicos.gerar_embeddings(["Uma pilha segue a ordem LIFO."])
        servicos.gerar_embedding("Uma fila segue a ordem FIFO.")

    assert adaptador_de_exemplo.Constante.finalidades == ["pergunta", "trecho", "trecho"]


def test_com_o_adaptador_falso_a_finalidade_nao_muda_o_vetor():
    texto = "lista encadeada de nós"

    assert servicos.gerar_embedding_da_pergunta(texto) == servicos.gerar_embedding(texto)


def test_pergunta_sem_palavras_uteis_tambem_e_recusada():
    with pytest.raises(ValueError):
        servicos.gerar_embedding_da_pergunta("   ")


def test_adaptador_que_nao_existe_e_erro_de_configuracao():
    with (
        override_settings(FAROL_IA={"ADAPTADOR": "ia.adaptadores.nao_existe.Provedor"}),
        pytest.raises(ImproperlyConfigured, match="ia.adaptadores.nao_existe"),
    ):
        servicos.gerar_embedding("texto")
