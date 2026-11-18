"""Custo de IA por aluno e alerta de orçamento (TUT-T93, TUT-RNF-05). Dados fictícios."""

from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from django.test import Client

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina
from notificacoes.models import Notificacao
from tutor import servicos
from tutor.models import RegistroUso

SAO_PAULO = ZoneInfo("America/Sao_Paulo")


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
def equipe(db) -> Pessoa:
    return Pessoa.objects.create_user(
        email="ti@exemplo.edu.br", nome="Equipe de TI", perfis=[Perfil.ADMIN], is_staff=True
    )


def uso(disciplina, aluno: str, custo: str, dia=date(2026, 11, 10)) -> None:
    RegistroUso.objects.create(
        aluno_pseudonimo=aluno,
        disciplina=disciplina,
        pergunta_filtrada="O que é uma pilha?",
        tipo="resposta",
        custo=Decimal(custo),
        criado_em=datetime(dia.year, dia.month, dia.day, 12, tzinfo=SAO_PAULO),
    )


@pytest.mark.requisito("TUT-RNF-05")
def test_o_custo_por_aluno_conta_os_alunos_pelo_pseudonimo(disciplina):
    uso(disciplina, "a", "1.00")
    uso(disciplina, "a", "1.50")
    uso(disciplina, "b", "0.50")
    uso(disciplina, "c", "9.00", dia=date(2026, 10, 30))  # outro mês

    (custo,) = servicos.custos_do_mes(2026, 11)

    assert (custo.perguntas, custo.alunos) == (3, 2)
    assert custo.custo_total == Decimal("3.00")
    assert custo.custo_por_aluno == Decimal("1.5000")
    assert custo.acima_do_orcamento is False


@pytest.mark.requisito("TUT-RNF-05")
def test_acima_de_2_reais_por_aluno_a_equipe_e_avisada_uma_vez_no_mes(disciplina, equipe):
    uso(disciplina, "a", "2.50")

    assert servicos.verificar_orcamento(hoje=date(2026, 11, 20)) == 1
    assert servicos.verificar_orcamento(hoje=date(2026, 11, 21)) == 0  # não repete

    aviso = Notificacao.objects.get()
    assert aviso.pessoa == equipe
    assert aviso.tipo == "orcamento_ia"
    assert aviso.texto == (
        "Custo de IA acima do orçamento em Estruturas de Dados: R$ 2.50 por aluno em 11/2026."
    )


def test_dentro_do_orcamento_ninguem_e_avisado(disciplina, equipe):
    uso(disciplina, "a", "2.00")

    assert servicos.verificar_orcamento(hoje=date(2026, 11, 20)) == 0


@pytest.mark.requisito("TUT-RNF-05")
def test_a_equipe_ve_o_custo_por_disciplina_no_painel(disciplina, equipe):
    uso(disciplina, "a", "2.50")
    cliente = Client()
    cliente.force_login(equipe)

    resposta = cliente.get("/admin/tutor/registrouso/custos/?mes=2026-11")

    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Estruturas de Dados" in html
    assert "Acima do orçamento" in html
    assert "2,50" in html or "2.50" in html


def test_quem_nao_e_administrador_nao_ve_os_custos(professor):
    professor.is_staff = True
    professor.save()
    cliente = Client()
    cliente.force_login(professor)

    assert cliente.get("/admin/tutor/registrouso/custos/").status_code == 403


def test_a_verificacao_fica_agendada_uma_vez_por_dia(settings):
    agendada = settings.CELERY_BEAT_SCHEDULE["orcamento-de-ia"]

    assert agendada["task"] == "tutor.verificar_orcamento"
    assert agendada["schedule"] == 24 * 3600
