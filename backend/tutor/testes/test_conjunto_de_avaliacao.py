"""O conjunto de avaliação do tutor está bem formado (TUT-T12)."""

import pytest

from tutor.avaliacao import carregar


@pytest.fixture(scope="module")
def conjunto():
    return carregar()


@pytest.mark.requisito("TUT-CS-01")
def test_tem_100_perguntas_sem_repeticao(conjunto):
    textos = [p.texto for p in conjunto.perguntas]

    assert len(textos) == 100
    assert len(set(textos)) == 100


@pytest.mark.requisito("TUT-CS-04")
def test_tem_perguntas_sem_base_no_material(conjunto):
    assert sum(p.sem_base for p in conjunto.perguntas) >= 10


def test_cada_pergunta_com_base_aponta_para_uma_pagina_que_existe(conjunto):
    paginas = {(a.numero, i) for a in conjunto.aulas for i in range(1, len(a.paginas) + 1)}

    for pergunta in conjunto.perguntas:
        if not pergunta.sem_base:
            assert (pergunta.aula, pergunta.pagina) in paginas, pergunta.texto
            assert pergunta.resposta, pergunta.texto


def test_toda_pagina_do_material_tem_ao_menos_uma_pergunta(conjunto):
    perguntadas = {(p.aula, p.pagina) for p in conjunto.perguntas if not p.sem_base}

    for aula in conjunto.aulas:
        for numero in range(1, len(aula.paginas) + 1):
            assert (aula.numero, numero) in perguntadas, (aula.titulo, numero)


def test_as_aulas_estao_numeradas_em_sequencia(conjunto):
    assert [a.numero for a in conjunto.aulas] == list(range(1, len(conjunto.aulas) + 1))
