"""Rotas de pedido de geração e de acompanhamento (QUE-T22). Dados fictícios."""

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from materiais.models import Material, Trecho
from questoes.models import PedidoGeracao, Questao

TEXTO = "A pilha segue a regra LIFO: o último elemento a entrar é o primeiro a sair dela."


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


def aula(disciplina, status=Material.Status.PRONTO) -> Material:
    material = Material.objects.create(
        disciplina=disciplina,
        aula_numero=3,
        aula_titulo="Pilhas e filas",
        arquivo="materiais/aula-3.pdf",
        status=status,
    )
    Trecho.objects.create(
        material=material,
        pagina=1,
        ordem=0,
        texto=TEXTO,
        inicio=0,
        fim=len(TEXTO),
        vetor=[1.0] + [0.0] * (settings.FAROL_DIMENSAO_DO_VETOR - 1),
    )
    return material


@pytest.fixture
def material(disciplina) -> Material:
    return aula(disciplina)


def pedir(cliente, material, quantidade=5):
    return cliente.post(
        f"/api/materiais/{material.id}/geracoes", {"quantidade": quantidade}, format="json"
    )


@pytest.mark.requisito("QUE-RF-01")
def test_o_professor_pede_rascunhos_de_uma_aula_pronta_e_acompanha_o_pedido(
    cliente_professor, material
):
    resposta = pedir(cliente_professor, material, quantidade=8)

    assert resposta.status_code == 202
    pedido = resposta.json()
    assert pedido["material"] == material.id
    assert pedido["quantidade"] == 8
    # Nos testes o Celery roda na hora: o pedido já volta terminado.
    assert pedido["status"] == "pronto"
    assert pedido["geradas"] == 8
    assert Questao.objects.filter(pedido_id=pedido["id"]).count() == 8

    acompanhamento = cliente_professor.get(f"/api/geracoes/{pedido['id']}")
    assert acompanhamento.status_code == 200
    assert acompanhamento.json()["status"] == "pronto"


@pytest.mark.requisito("QUE-RF-01")
@pytest.mark.parametrize("quantidade", [4, 21, "dez"])
def test_quantidade_fora_de_5_a_20_e_recusada(cliente_professor, material, quantidade):
    resposta = pedir(cliente_professor, material, quantidade=quantidade)

    assert resposta.status_code == 400
    assert "quantidade" in resposta.json()
    assert not PedidoGeracao.objects.exists()


@pytest.mark.requisito("QUE-RF-01")
@pytest.mark.parametrize(
    "status", [Material.Status.PROCESSANDO, Material.Status.ERRO, Material.Status.RETIRADO]
)
def test_aula_que_nao_esta_pronta_recebe_409(cliente_professor, disciplina, status):
    resposta = pedir(cliente_professor, aula(disciplina, status=status))

    assert resposta.status_code == 409
    assert "não está pronta" in resposta.json()["detail"]
    assert not PedidoGeracao.objects.exists()


def test_o_aluno_nao_pede_rascunhos(cliente_aluna, material):
    assert pedir(cliente_aluna, material).status_code == 403
    assert not PedidoGeracao.objects.exists()


def test_professor_de_outra_disciplina_nao_pede_nem_acompanha(cliente_professor, material):
    outro = Pessoa.objects.create_user(
        email="paula.lima@exemplo.edu.br", nome="Paula Lima", perfis=[Perfil.PROFESSOR]
    )
    cliente = APIClient()
    cliente.force_login(outro)
    pedido_id = pedir(cliente_professor, material).json()["id"]

    assert pedir(cliente, material).status_code == 403
    assert cliente.get(f"/api/geracoes/{pedido_id}").status_code == 403


def test_o_aluno_nao_acompanha_o_pedido(cliente_professor, cliente_aluna, material):
    pedido_id = pedir(cliente_professor, material).json()["id"]

    assert cliente_aluna.get(f"/api/geracoes/{pedido_id}").status_code == 403


def test_aula_ou_pedido_que_nao_existe_recebe_404(cliente_professor):
    assert (
        cliente_professor.post(
            "/api/materiais/999/geracoes", {"quantidade": 5}, format="json"
        ).status_code
        == 404
    )
    assert cliente_professor.get("/api/geracoes/999").status_code == 404


def test_sem_login_nada_feito(cliente, material):
    assert pedir(cliente, material).status_code in (401, 403)


def test_pedido_em_andamento_e_devolvido_em_vez_de_criar_outro(
    cliente_professor, material, professor
):
    andamento = PedidoGeracao.objects.create(material=material, quantidade=5, pedido_por=professor)

    resposta = pedir(cliente_professor, material, quantidade=10)

    assert resposta.json()["id"] == andamento.id
    assert PedidoGeracao.objects.count() == 1
