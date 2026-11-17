"""As dúvidas da turma para o professor, sem dados do aluno (DUV-T20, DUV-T21). Dados fictícios."""

import json
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from duvidas.models import Duvida
from tutor.models import Conversa, Mensagem


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


def url(disciplina, status=None) -> str:
    base = f"/api/disciplinas/{disciplina.id}/duvidas"
    return base if status is None else f"{base}?status={status}"


def enviada_pela_aluna(cliente_aluna, aluna, disciplina, pergunta: str) -> None:
    conversa, _ = Conversa.objects.get_or_create(aluno=aluna, disciplina=disciplina)
    Mensagem.objects.create(conversa=conversa, autor="aluno", texto=pergunta)
    resposta = Mensagem.objects.create(
        conversa=conversa,
        autor="tutor",
        texto="Não encontrei isso no material da disciplina.",
        tipo="nao_encontrado",
    )
    assert cliente_aluna.post(f"/api/mensagens/{resposta.id}/duvida").status_code == 201


@pytest.mark.requisito("DUV-RF-05")
def test_o_professor_ve_as_duvidas_abertas_da_mais_recente_com_a_marca_nova(
    cliente_professor, disciplina
):
    hoje = timezone.localdate()
    Duvida.objects.create(disciplina=disciplina, texto="Antiga", data=hoje - timedelta(days=3))
    Duvida.objects.create(disciplina=disciplina, texto="Recente", data=hoje)
    Duvida.objects.create(disciplina=disciplina, texto="Já vista", data=hoje, vista=True)
    Duvida.objects.create(disciplina=disciplina, texto="Oculta", data=hoje, status="oculta")

    lista = cliente_professor.get(url(disciplina)).json()

    assert [(d["texto"], d["nova"]) for d in lista] == [
        ("Já vista", False),
        ("Recente", True),
        ("Antiga", True),
    ]
    assert lista[2]["data"] == (hoje - timedelta(days=3)).isoformat()


@pytest.mark.requisito("DUV-RF-05")
def test_depois_de_vistas_as_duvidas_deixam_de_ser_novas(cliente_professor, disciplina):
    Duvida.objects.create(disciplina=disciplina, texto="Pilha ou fila?")

    cliente_professor.get(url(disciplina))

    assert [d["nova"] for d in cliente_professor.get(url(disciplina)).json()] == [False]


def test_a_aba_respondidas_lista_so_as_respondidas(cliente_professor, disciplina):
    Duvida.objects.create(disciplina=disciplina, texto="Aberta")
    Duvida.objects.create(disciplina=disciplina, texto="Respondida", status="respondida")

    lista = cliente_professor.get(url(disciplina, "respondida")).json()

    assert [d["texto"] for d in lista] == ["Respondida"]
    assert cliente_professor.get(url(disciplina, "oculta")).status_code == 400


@pytest.mark.requisito("DUV-RF-03")
@pytest.mark.requisito("DUV-RNF-01")
def test_nenhuma_rota_do_professor_devolve_dado_do_aluno(
    cliente_aluna, aluna, cliente_professor, disciplina
):
    enviada_pela_aluna(cliente_aluna, aluna, disciplina, "A prova cobre árvores AVL?")

    corpo = cliente_professor.get(url(disciplina)).content.decode()
    (duvida,) = json.loads(corpo)

    assert set(duvida) == {"id", "texto", "data", "status", "nova"}
    assert "T" not in duvida["data"]  # só o dia, sem a hora
    for dado in (aluna.nome, "Ana", aluna.email, str(aluna.id), "SINF2NA"):
        assert dado not in corpo


@pytest.mark.requisito("ACE-RF-05")
def test_so_o_professor_da_disciplina_ve_as_duvidas(cliente_aluna, disciplina):
    outro = Pessoa.objects.create_user(
        email="rita.lima@exemplo.edu.br", nome="Rita Lima", perfis=[Perfil.PROFESSOR]
    )
    cliente_do_outro = APIClient()
    cliente_do_outro.force_login(outro)

    assert cliente_aluna.get(url(disciplina)).status_code == 403
    assert cliente_do_outro.get(url(disciplina)).status_code == 403
