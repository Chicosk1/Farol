"""Ver e apagar o próprio histórico com o tutor (ACE-T52, ACE-RF-09). Dados fictícios."""

import pytest

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from duvidas.models import Duvida
from tutor.models import Conversa, Mensagem, RegistroUso

URL = "/api/eu/historico"


@pytest.fixture
def disciplina(professor, aluna) -> Disciplina:
    disciplina = Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)
    return disciplina


def conversa_de(aluno, disciplina, *textos: str) -> Conversa:
    conversa = Conversa.objects.create(aluno=aluno, disciplina=disciplina)
    for texto in textos:
        Mensagem.objects.create(conversa=conversa, autor="aluno", texto=texto)
    return conversa


@pytest.mark.requisito("ACE-RF-09")
def test_o_aluno_ve_as_suas_conversas_por_disciplina(cliente_aluna, aluna, disciplina):
    conversa_de(aluna, disciplina, "O que é uma pilha?", "E uma fila?")

    (item,) = cliente_aluna.get(URL).json()

    assert item["disciplina_id"] == disciplina.id
    assert item["disciplina_nome"] == "Estruturas de Dados"
    assert item["mensagens"] == 2
    assert item["ultima_em"]


@pytest.mark.requisito("ACE-RF-09")
def test_apagar_o_historico_exclui_as_conversas_do_banco(cliente_aluna, aluna, disciplina):
    conversa_de(aluna, disciplina, "O que é uma pilha?")

    assert cliente_aluna.delete(URL).status_code == 204

    assert not Conversa.objects.exists()
    assert not Mensagem.objects.exists()
    assert cliente_aluna.get(URL).json() == []


def test_apagar_nao_mexe_no_historico_de_outro_aluno(cliente_aluna, disciplina):
    colega = Pessoa.objects.create_user(
        email="bruno.dias@exemplo.edu.br", nome="Bruno Dias", perfis=[Perfil.ALUNO]
    )
    conversa_de(colega, disciplina, "Pergunta do colega")

    cliente_aluna.delete(URL)

    assert Conversa.objects.filter(aluno=colega).count() == 1


@pytest.mark.requisito("ACE-RF-09")
def test_a_duvida_enviada_e_o_registro_anonimo_continuam(cliente_aluna, aluna, disciplina):
    conversa = conversa_de(aluna, disciplina, "Isso cai na prova?")
    resposta = Mensagem.objects.create(
        conversa=conversa,
        autor="tutor",
        texto="Não encontrei isso no material da disciplina.",
        tipo="nao_encontrado",
    )
    assert cliente_aluna.post(f"/api/mensagens/{resposta.id}/duvida").status_code == 201
    RegistroUso.objects.create(
        aluno_pseudonimo="x",
        disciplina=disciplina,
        pergunta_filtrada="Isso cai na prova?",
        tipo="nao_encontrado",
    )

    cliente_aluna.delete(URL)

    assert Duvida.objects.count() == 1  # já não tem ligação com a aluna (spec 004)
    assert RegistroUso.objects.count() == 1  # só o pseudônimo, sem ligação com a conversa


def test_so_o_aluno_usa_o_historico(cliente_professor, cliente):
    assert cliente_professor.get(URL).status_code == 403
    assert cliente.delete(URL).status_code == 401
