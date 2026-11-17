"""Busca dos trechos mais próximos da pergunta, só da disciplina e só de material pronto (TUT-T21).

É a base do tutor: o que não é do professor da disciplina, ou não está pronto, nunca aparece
(princípio I da constituição). A IA é o adaptador falso. Dados fictícios.
"""

import pytest

from disciplinas.models import Disciplina
from ia import servicos as ia
from materiais import servicos
from materiais.models import Material, Trecho

TEXTOS = {
    "lista": "Uma lista encadeada é formada por nós com ponteiros para o próximo nó.",
    "pilha": "Uma pilha segue a ordem LIFO: o último elemento inserido é o primeiro a sair.",
    "fila": "Uma fila segue a ordem FIFO: o primeiro elemento inserido é o primeiro a sair.",
    "arvore": "Uma árvore binária tem no máximo dois filhos por nó, esquerdo e direito.",
    "grafo": "Um grafo é formado por vértices e arestas que ligam os vértices.",
    "hash": "Uma tabela hash usa uma função de espalhamento para achar a posição da chave.",
    "banco": "A chave primária identifica cada linha de uma tabela relacional.",
}


@pytest.fixture
def disciplina(professor) -> Disciplina:
    return Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )


def material(disciplina, aula: int, status=Material.Status.PRONTO) -> Material:
    return Material.objects.create(
        disciplina=disciplina,
        aula_numero=aula,
        aula_titulo=f"Aula {aula}",
        arquivo=f"x{aula}.pdf",
        status=status,
    )


def trecho(material: Material, pagina: int, texto: str) -> Trecho:
    return Trecho.objects.create(
        material=material,
        pagina=pagina,
        ordem=0,
        texto=texto,
        inicio=0,
        fim=len(texto),
        vetor=ia.gerar_embedding(texto),
    )


def buscar(disciplina, pergunta: str, **opcoes):
    return servicos.buscar_trechos(disciplina.id, ia.gerar_embedding(pergunta), **opcoes)


@pytest.mark.requisito("TUT-RF-01")
def test_o_trecho_que_trata_do_assunto_vem_primeiro(disciplina):
    aula = material(disciplina, 4)
    for pagina, chave in enumerate(["lista", "pilha", "fila", "banco"], start=1):
        trecho(aula, pagina, TEXTOS[chave])

    achados = buscar(disciplina, "O que é uma lista encadeada?")

    assert achados[0].texto == TEXTOS["lista"]
    assert achados[0].similaridade > 0.4
    assert achados[0].similaridade > achados[-1].similaridade


@pytest.mark.requisito("TUT-RF-01")
def test_cada_trecho_vem_com_a_aula_e_a_pagina_de_origem(disciplina):
    trecho(material(disciplina, 4), 5, TEXTOS["lista"])

    (achado,) = buscar(disciplina, "lista encadeada")

    assert (achado.aula_numero, achado.pagina) == (4, 5)
    assert achado.material_id
    assert achado.id


@pytest.mark.requisito("TUT-RF-01")
def test_devolve_no_maximo_6_trechos_por_padrao(disciplina):
    aula = material(disciplina, 1)
    for pagina, texto in enumerate(TEXTOS.values(), start=1):  # 7 trechos
        trecho(aula, pagina, texto)

    assert len(buscar(disciplina, "estrutura de dados")) == 6
    assert len(buscar(disciplina, "estrutura de dados", limite=3)) == 3


@pytest.mark.requisito("TUT-RF-01")
def test_so_busca_na_disciplina_pedida(disciplina, professor):
    outra = Disciplina.objects.create(
        codigo="SINF202",
        nome="Banco de Dados I",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    trecho(material(disciplina, 1), 1, TEXTOS["lista"])
    trecho(material(outra, 1), 1, TEXTOS["banco"])

    achados = buscar(disciplina, "chave primária tabela relacional lista encadeada")

    assert [a.texto for a in achados] == [TEXTOS["lista"]]


@pytest.mark.requisito("TUT-RF-01")
@pytest.mark.requisito("MAT-RF-07")
@pytest.mark.parametrize(
    "status",
    [
        Material.Status.PROCESSANDO,
        Material.Status.ERRO,
        Material.Status.ATENCAO,
        Material.Status.RETIRADO,
    ],
)
def test_material_que_nao_esta_pronto_nunca_aparece_na_busca(disciplina, status):
    trecho(material(disciplina, 1, status=status), 1, TEXTOS["lista"])
    trecho(material(disciplina, 2), 1, TEXTOS["pilha"])

    achados = buscar(disciplina, "lista encadeada pilha")

    assert [a.texto for a in achados] == [TEXTOS["pilha"]]


@pytest.mark.requisito("MAT-CS-03")
def test_retirar_o_material_o_tira_da_busca_na_pergunta_seguinte(disciplina):
    aula = material(disciplina, 1)
    trecho(aula, 1, TEXTOS["lista"])
    assert len(buscar(disciplina, "lista encadeada")) == 1

    Material.objects.filter(pk=aula.pk).update(status=Material.Status.RETIRADO)

    assert buscar(disciplina, "lista encadeada") == []


def test_sem_nenhum_material_pronto_a_busca_devolve_lista_vazia(disciplina):
    assert buscar(disciplina, "lista encadeada") == []
