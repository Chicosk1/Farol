"""Modelos Material e Trecho, com a busca vetorial do pgvector (MAT-T10).

Os testes rodam no PostgreSQL com pgvector do Docker, e não em SQLite, para a busca por
proximidade e o índice serem testados de verdade (docs/qualidade-e-testes.md). Dados fictícios.
"""

import pytest
from django.conf import settings
from django.db import IntegrityError, connection, transaction
from pgvector.django import CosineDistance

from disciplinas.models import Disciplina
from materiais.models import Material, Trecho

DIM = settings.FAROL_DIMENSAO_DO_VETOR


def vetor(*posicoes_com_valor: tuple[int, float]) -> list[float]:
    """Um vetor de zeros com valores em algumas posições, para controlar a proximidade."""
    v = [0.0] * DIM
    for posicao, valor in posicoes_com_valor:
        v[posicao] = valor
    return v


@pytest.fixture(autouse=True)
def busca_exata(db):
    """Os testes deste módulo conferem a ordem exata pela distância. O índice HNSW, que é
    aproximado, fica de fora: no banco de testes ele acumula entradas mortas dos testes desfeitos
    e pode pular trechos (TUT-T28). A busca do tutor não usa o índice."""
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL enable_indexscan = off")


@pytest.fixture
def disciplina(professor) -> Disciplina:
    return Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )


@pytest.fixture
def material(disciplina, professor) -> Material:
    return Material.objects.create(
        disciplina=disciplina,
        aula_numero=4,
        aula_titulo="Listas encadeadas",
        arquivo="materiais/aula-4.pdf",
        enviado_por=professor,
    )


def test_material_novo_comeca_processando_na_primeira_etapa_e_na_versao_1(material):
    material.refresh_from_db()

    assert material.status == Material.Status.PROCESSANDO
    assert material.etapa == Material.Etapa.ENVIANDO
    assert material.versao == 1
    assert material.paginas == 0
    assert material.paginas_sem_texto == []
    assert material.substitui is None


def test_material_guarda_disciplina_aula_e_arquivo(material, disciplina):
    assert (material.disciplina, material.aula_numero, material.aula_titulo) == (
        disciplina,
        4,
        "Listas encadeadas",
    )
    assert str(material) == "Aula 4: Listas encadeadas (Estruturas de Dados)"


@pytest.mark.requisito("MAT-RF-04")
def test_cada_trecho_guarda_o_material_a_pagina_e_a_posicao_de_origem(material):
    trecho = Trecho.objects.create(
        material=material,
        pagina=5,
        ordem=0,
        texto="Uma lista encadeada é uma sequência de nós.",
        inicio=0,
        fim=43,
        vetor=vetor((0, 1.0)),
    )

    trecho.refresh_from_db()
    assert trecho.material.aula_numero == 4  # a aula e o arquivo vêm do material
    assert trecho.material.arquivo.name == "materiais/aula-4.pdf"
    assert (trecho.pagina, trecho.inicio, trecho.fim) == (5, 0, 43)
    assert len(trecho.vetor) == DIM


@pytest.mark.requisito("MAT-RF-04")
def test_a_busca_vetorial_devolve_primeiro_o_trecho_mais_proximo(material):
    perto = Trecho.objects.create(
        material=material,
        pagina=1,
        ordem=0,
        texto="perto",
        inicio=0,
        fim=5,
        vetor=vetor((0, 1.0), (1, 0.1)),
    )
    meio = Trecho.objects.create(
        material=material,
        pagina=2,
        ordem=0,
        texto="meio",
        inicio=0,
        fim=4,
        vetor=vetor((0, 1.0), (1, 1.0)),
    )
    longe = Trecho.objects.create(
        material=material,
        pagina=3,
        ordem=0,
        texto="longe",
        inicio=0,
        fim=5,
        vetor=vetor((1, 1.0)),
    )

    # A ordem pela distância é exata. O índice HNSW, que é aproximado, fica de fora: no banco de
    # testes ele acumula entradas mortas dos testes desfeitos e pode pular trechos (TUT-T28).
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL enable_indexscan = off")
        resultado = list(
            Trecho.objects.order_by(CosineDistance("vetor", vetor((0, 1.0)))).values_list(
                "id", flat=True
            )
        )

    assert resultado == [perto.id, meio.id, longe.id]


def test_a_busca_pode_ser_filtrada_pela_disciplina_do_material(material, professor):
    outra = Disciplina.objects.create(
        codigo="SINF202",
        nome="Banco de Dados I",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    de_outra = Material.objects.create(
        disciplina=outra, aula_numero=1, aula_titulo="Modelo relacional", arquivo="x.pdf"
    )
    Trecho.objects.create(
        material=material, pagina=1, ordem=0, texto="a", inicio=0, fim=1, vetor=vetor((0, 1.0))
    )
    Trecho.objects.create(
        material=de_outra, pagina=1, ordem=0, texto="b", inicio=0, fim=1, vetor=vetor((0, 1.0))
    )

    achados = Trecho.objects.filter(material__disciplina=outra).order_by(
        CosineDistance("vetor", vetor((0, 1.0)))
    )

    assert [t.texto for t in achados] == ["b"]


def test_o_banco_recusa_vetor_de_outro_tamanho(material):
    with pytest.raises(Exception, match="dimensions"), transaction.atomic():
        Trecho.objects.create(
            material=material, pagina=1, ordem=0, texto="x", inicio=0, fim=1, vetor=[1.0, 2.0]
        )


def test_a_mesma_pagina_e_ordem_nao_se_repetem_no_mesmo_material(material):
    dados = dict(material=material, pagina=1, ordem=0, texto="x", inicio=0, fim=1, vetor=vetor())
    Trecho.objects.create(**dados)

    with pytest.raises(IntegrityError), transaction.atomic():
        Trecho.objects.create(**dados)


def test_apagar_o_material_apaga_os_trechos(material):
    Trecho.objects.create(
        material=material, pagina=1, ordem=0, texto="x", inicio=0, fim=1, vetor=vetor()
    )

    material.delete()

    assert Trecho.objects.count() == 0


@pytest.mark.django_db
def test_existe_o_indice_hnsw_para_a_busca_por_proximidade():
    with connection.cursor() as cursor:
        restricoes = connection.introspection.get_constraints(cursor, Trecho._meta.db_table)

    indice = restricoes.get("trecho_vetor_hnsw")
    assert indice is not None
    assert indice["columns"] == ["vetor"]


@pytest.mark.requisito("TUT-RF-01")
def test_a_conexao_liga_a_varredura_iterativa_do_indice_hnsw(db):
    """Sem ela, o índice HNSW para nos 40 candidatos mais próximos, mesmo que sejam entradas
    mortas ou de outra disciplina, e a busca devolve menos trechos do que existem (TUT-T28)."""
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SHOW hnsw.iterative_scan")
        (valor,) = cursor.fetchone()

    assert valor == "strict_order"
