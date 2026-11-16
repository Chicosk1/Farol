"""Favoritos: PUT e DELETE /api/disciplinas/{id}/favorito e o filtro Favoritas (ACE-T32).

Cenário 3 da História 2 da spec 001: marcar uma disciplina como favorita faz ela aparecer na
aba "Favoritas". Todos os dados são fictícios.
"""

import pytest
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Favorito, Matricula


@pytest.fixture
def disciplinas(professor) -> list[Disciplina]:
    nomes = ["Estruturas de Dados", "Banco de Dados I", "Matemática Discreta"]
    return [
        Disciplina.objects.create(
            codigo=f"SINF20{i}", nome=nome, turma="SINF2NA", semestre="2026/2", professor=professor
        )
        for i, nome in enumerate(nomes, start=1)
    ]


@pytest.fixture
def aluna_matriculada(aluna, disciplinas) -> Pessoa:
    for disciplina in disciplinas:
        Matricula.objects.create(aluno=aluna, disciplina=disciplina)
    return aluna


def url(disciplina: Disciplina) -> str:
    return f"/api/disciplinas/{disciplina.id}/favorito"


def nomes(resposta) -> list[str]:
    return [item["nome"] for item in resposta.json()]


@pytest.mark.requisito("ACE-RF-10")
def test_marcar_como_favorita_faz_a_disciplina_aparecer_na_aba_favoritas(
    cliente_aluna, aluna_matriculada, disciplinas
):
    estruturas = disciplinas[0]

    resposta = cliente_aluna.put(url(estruturas))

    assert resposta.status_code == 204
    favoritas = cliente_aluna.get("/api/disciplinas", {"filtro": "favoritas"})
    assert nomes(favoritas) == ["Estruturas de Dados"]
    assert len(cliente_aluna.get("/api/disciplinas", {"filtro": "todas"}).json()) == 3


@pytest.mark.requisito("ACE-RF-10")
def test_a_lista_diz_quais_disciplinas_sao_favoritas(cliente_aluna, aluna_matriculada, disciplinas):
    cliente_aluna.put(url(disciplinas[1]))

    lista = cliente_aluna.get("/api/disciplinas").json()

    assert {item["nome"]: item["favorita"] for item in lista} == {
        "Banco de Dados I": True,
        "Estruturas de Dados": False,
        "Matemática Discreta": False,
    }


@pytest.mark.requisito("ACE-RF-10")
def test_marcar_duas_vezes_nao_duplica(cliente_aluna, aluna_matriculada, disciplinas):
    assert cliente_aluna.put(url(disciplinas[0])).status_code == 204
    assert cliente_aluna.put(url(disciplinas[0])).status_code == 204

    assert Favorito.objects.count() == 1


@pytest.mark.requisito("ACE-RF-10")
def test_desmarcar_tira_a_disciplina_da_aba_favoritas(
    cliente_aluna, aluna_matriculada, disciplinas
):
    cliente_aluna.put(url(disciplinas[0]))

    resposta = cliente_aluna.delete(url(disciplinas[0]))

    assert resposta.status_code == 204
    assert cliente_aluna.get("/api/disciplinas", {"filtro": "favoritas"}).json() == []


@pytest.mark.requisito("ACE-RF-10")
def test_desmarcar_quem_nao_era_favorita_tambem_responde_204(
    cliente_aluna, aluna_matriculada, disciplinas
):
    assert cliente_aluna.delete(url(disciplinas[0])).status_code == 204


@pytest.mark.requisito("ACE-RF-10")
def test_a_busca_vale_dentro_da_aba_favoritas(cliente_aluna, aluna_matriculada, disciplinas):
    for disciplina in disciplinas[:2]:
        cliente_aluna.put(url(disciplina))

    resposta = cliente_aluna.get("/api/disciplinas", {"filtro": "favoritas", "busca": "banco"})

    assert nomes(resposta) == ["Banco de Dados I"]


@pytest.mark.requisito("ACE-RF-10")
def test_favoritos_sao_de_cada_pessoa(cliente_aluna, aluna_matriculada, disciplinas):
    colega = Pessoa.objects.create_user(
        email="bruno.dias@exemplo.edu.br", nome="Bruno Dias", perfis=[Perfil.ALUNO]
    )
    for disciplina in disciplinas:
        Matricula.objects.create(aluno=colega, disciplina=disciplina)
    cliente_do_colega = APIClient()
    cliente_do_colega.force_login(colega)

    cliente_aluna.put(url(disciplinas[0]))

    assert cliente_do_colega.get("/api/disciplinas", {"filtro": "favoritas"}).json() == []


@pytest.mark.requisito("ACE-RF-05")
def test_nao_matriculado_nao_favorita_e_recebe_403(cliente_aluna, aluna, disciplinas):
    resposta = cliente_aluna.put(url(disciplinas[0]))

    assert resposta.status_code == 403
    assert Favorito.objects.count() == 0


@pytest.mark.requisito("ACE-RF-05")
def test_nao_matriculado_tambem_nao_desfavorita(cliente_aluna, aluna, disciplinas):
    assert cliente_aluna.delete(url(disciplinas[0])).status_code == 403


@pytest.mark.requisito("ACE-RF-05")
def test_disciplina_que_nao_existe_recebe_403(cliente_aluna, aluna_matriculada):
    assert cliente_aluna.put("/api/disciplinas/999999/favorito").status_code == 403


@pytest.mark.requisito("ACE-RF-05")
def test_matricula_encerrada_esconde_o_favorito_e_nega_mudancas(
    cliente_aluna, aluna_matriculada, disciplinas
):
    cliente_aluna.put(url(disciplinas[0]))
    Matricula.objects.filter(disciplina=disciplinas[0]).update(situacao="encerrada")

    assert cliente_aluna.get("/api/disciplinas", {"filtro": "favoritas"}).json() == []
    assert cliente_aluna.delete(url(disciplinas[0])).status_code == 403


def test_exige_login(cliente, disciplinas):
    assert cliente.put(url(disciplinas[0])).status_code == 401
    assert cliente.delete(url(disciplinas[0])).status_code == 401


def test_so_aceita_put_e_delete(cliente_aluna, aluna_matriculada, disciplinas):
    assert cliente_aluna.get(url(disciplinas[0])).status_code == 405
    assert cliente_aluna.post(url(disciplinas[0])).status_code == 405
