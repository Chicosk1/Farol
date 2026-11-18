"""Modelos das questões e dos quizzes (QUE-T10). Rodam no PostgreSQL do Docker. Dados fictícios."""

import pytest
from django.conf import settings
from django.db import IntegrityError, connection, transaction

from disciplinas.models import Disciplina
from materiais.models import Material, Trecho
from questoes.models import PedidoGeracao, ProgressoQuiz, Questao, RespostaQuiz


@pytest.fixture
def material(professor) -> Material:
    disciplina = Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    return Material.objects.create(
        disciplina=disciplina,
        aula_numero=3,
        aula_titulo="Pilhas e filas",
        arquivo="materiais/aula-3.pdf",
        enviado_por=professor,
        status=Material.Status.PRONTO,
    )


@pytest.fixture
def trecho(material) -> Trecho:
    return Trecho.objects.create(
        material=material,
        pagina=2,
        ordem=0,
        texto="A pilha segue a regra LIFO: o último a entrar é o primeiro a sair.",
        inicio=0,
        fim=66,
        vetor=[1.0] + [0.0] * (settings.FAROL_DIMENSAO_DO_VETOR - 1),
    )


def questao(material, trecho, **campos) -> Questao:
    dados = {
        "material": material,
        "enunciado": "Qual regra a pilha segue?",
        "alternativas": ["LIFO", "FIFO", "Por prioridade", "Aleatória"],
        "correta": 0,
        "justificativa": "Na pilha, o último a entrar é o primeiro a sair.",
        "topico": "Pilhas",
        "trecho": trecho,
    }
    return Questao.objects.create(**(dados | campos))


def test_questao_nova_comeca_pendente_e_marcada_como_novo_rascunho(material, trecho):
    nova = questao(material, trecho)
    nova.refresh_from_db()

    assert nova.status == Questao.Status.PENDENTE
    assert nova.nova is True
    assert nova.editada is False
    assert nova.pedido is None


@pytest.mark.parametrize("quantidade", [4, 21])
def test_o_banco_recusa_pedido_fora_de_5_a_20_questoes(material, professor, quantidade):
    with pytest.raises(IntegrityError), transaction.atomic():
        PedidoGeracao.objects.create(material=material, quantidade=quantidade, pedido_por=professor)


def test_pedido_novo_comeca_gerando(material, professor):
    pedido = PedidoGeracao.objects.create(material=material, quantidade=10, pedido_por=professor)
    pedido.refresh_from_db()

    assert pedido.status == PedidoGeracao.Status.PROCESSANDO
    assert (pedido.geradas, pedido.descartadas) == (0, 0)


def test_o_banco_recusa_questao_sem_quatro_alternativas(material, trecho):
    with pytest.raises(IntegrityError), transaction.atomic():
        questao(material, trecho, alternativas=["Sim", "Não", "Talvez"])


def test_o_banco_recusa_gabarito_fora_das_alternativas(material, trecho):
    with pytest.raises(IntegrityError), transaction.atomic():
        questao(material, trecho, correta=4)


def test_apagar_a_aula_apaga_as_questoes_e_as_respostas(material, trecho):
    nova = questao(material, trecho)
    RespostaQuiz.objects.create(questao=nova, aluno_pseudonimo="abc", alternativa=1, acerto=False)

    material.delete()

    assert not Questao.objects.exists()
    assert not RespostaQuiz.objects.exists()


@pytest.mark.requisito("QUE-RF-11")
def test_a_resposta_guarda_o_pseudonimo_e_o_dia_sem_a_hora_nem_o_aluno(material, trecho):
    campos = {campo.name for campo in RespostaQuiz._meta.get_fields()}

    assert "aluno" not in campos
    assert RespostaQuiz._meta.get_field("respondida_em").get_internal_type() == "DateField"
    assert "aluno_pseudonimo" in campos


def test_o_aluno_tem_um_progresso_por_aula(material, aluna):
    ProgressoQuiz.objects.create(aluno=aluna, material=material)

    with pytest.raises(IntegrityError), transaction.atomic():
        ProgressoQuiz.objects.create(aluno=aluna, material=material)


@pytest.mark.django_db
def test_existe_o_indice_das_questoes_por_aula_e_status():
    with connection.cursor() as cursor:
        indices = connection.introspection.get_constraints(cursor, Questao._meta.db_table)

    assert indices["questao_material_status"]["columns"] == ["material_id", "status"]
