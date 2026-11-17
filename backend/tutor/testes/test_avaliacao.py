"""Avaliação das respostas e fila de revisão da equipe (TUT-T70, TUT-RF-09). Dados fictícios."""

import pytest
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from tutor.models import Conversa, Mensagem, RevisaoResposta


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


@pytest.fixture
def resposta(aluna, disciplina) -> Mensagem:
    conversa = Conversa.objects.create(aluno=aluna, disciplina=disciplina)
    Mensagem.objects.create(conversa=conversa, autor="aluno", texto="O que é uma pilha?")
    return Mensagem.objects.create(
        conversa=conversa, autor="tutor", texto="Uma pilha segue a ordem FIFO. [1]"
    )


def avaliar(cliente, mensagem, avaliacao: str):
    return cliente.put(
        f"/api/mensagens/{mensagem.id}/avaliacao", {"avaliacao": avaliacao}, format="json"
    )


@pytest.mark.requisito("TUT-RF-09")
@pytest.mark.parametrize("avaliacao", ["util", "nao_util", "incorreta"])
def test_o_aluno_marca_a_resposta_e_a_marcacao_fica_registrada(cliente_aluna, resposta, avaliacao):
    assert avaliar(cliente_aluna, resposta, avaliacao).status_code == 204

    resposta.refresh_from_db()
    assert resposta.avaliacao == avaliacao


@pytest.mark.requisito("TUT-RF-09")
def test_um_novo_toque_desfaz_a_marcacao(cliente_aluna, resposta):
    avaliar(cliente_aluna, resposta, "util")

    assert avaliar(cliente_aluna, resposta, "").status_code == 204

    resposta.refresh_from_db()
    assert resposta.avaliacao == ""


@pytest.mark.requisito("TUT-RF-09")
def test_resposta_marcada_como_incorreta_entra_na_fila_de_revisao(cliente_aluna, resposta):
    avaliar(cliente_aluna, resposta, "incorreta")
    avaliar(cliente_aluna, resposta, "incorreta")  # marcar de novo não duplica

    revisao = RevisaoResposta.objects.get()
    assert (revisao.mensagem, revisao.status) == (resposta, "pendente")


@pytest.mark.requisito("TUT-RF-09")
def test_desfazer_o_incorreta_tira_da_fila_o_que_a_equipe_ainda_nao_revisou(
    cliente_aluna, resposta
):
    avaliar(cliente_aluna, resposta, "incorreta")
    avaliar(cliente_aluna, resposta, "util")

    assert not RevisaoResposta.objects.exists()


def test_a_revisao_ja_feita_pela_equipe_fica_guardada(cliente_aluna, resposta):
    avaliar(cliente_aluna, resposta, "incorreta")
    RevisaoResposta.objects.update(status="revisada", nota_da_equipe="Trecho corrigido.")

    avaliar(cliente_aluna, resposta, "")

    assert RevisaoResposta.objects.get().status == "revisada"


def test_avaliacao_invalida_ou_da_pergunta_do_aluno_recebe_400(cliente_aluna, resposta):
    pergunta = Mensagem.objects.get(autor="aluno")

    assert avaliar(cliente_aluna, resposta, "otima").status_code == 400
    assert avaliar(cliente_aluna, pergunta, "util").status_code == 400


def test_mensagem_de_outro_aluno_recebe_404(resposta):
    colega = Pessoa.objects.create_user(
        email="bruno.dias@exemplo.edu.br", nome="Bruno Dias", perfis=[Perfil.ALUNO]
    )
    cliente = APIClient()
    cliente.force_login(colega)

    assert avaliar(cliente, resposta, "incorreta").status_code == 404
    assert not RevisaoResposta.objects.exists()


@pytest.fixture
def cliente_equipe(db) -> Client:
    equipe = Pessoa.objects.create_user(
        email="ti@exemplo.edu.br", nome="Equipe de TI", perfis=[Perfil.ADMIN], is_staff=True
    )
    cliente = Client()
    cliente.force_login(equipe)
    return cliente


@pytest.mark.requisito("TUT-RF-09")
def test_a_equipe_ve_a_fila_com_a_pergunta_e_a_resposta_sem_o_nome_do_aluno(
    cliente_equipe, cliente_aluna, resposta
):
    avaliar(cliente_aluna, resposta, "incorreta")
    revisao = RevisaoResposta.objects.get()

    lista = cliente_equipe.get(reverse("admin:tutor_revisaoresposta_changelist"))
    pagina = cliente_equipe.get(reverse("admin:tutor_revisaoresposta_change", args=[revisao.id]))

    assert lista.status_code == 200 and pagina.status_code == 200
    html = pagina.content.decode()
    assert "O que é uma pilha?" in html
    assert "Uma pilha segue a ordem FIFO. [1]" in html
    assert "Ana Souza" not in html and "ana.souza@exemplo.edu.br" not in html
    assert "Ana Souza" not in lista.content.decode()


@pytest.mark.requisito("TUT-RF-09")
def test_a_equipe_marca_a_resposta_como_revisada_com_uma_nota(
    cliente_equipe, cliente_aluna, resposta
):
    avaliar(cliente_aluna, resposta, "incorreta")
    revisao = RevisaoResposta.objects.get()

    cliente_equipe.post(
        reverse("admin:tutor_revisaoresposta_change", args=[revisao.id]),
        {"status": "revisada", "nota_da_equipe": "O trecho fala em LIFO."},
    )

    revisao.refresh_from_db()
    assert (revisao.status, revisao.nota_da_equipe) == ("revisada", "O trecho fala em LIFO.")


def test_quem_nao_e_administrador_nao_ve_a_fila(cliente_aluna, resposta):
    professor_da_equipe = Pessoa.objects.create_user(
        email="rita.lima@exemplo.edu.br",
        nome="Rita Lima",
        perfis=[Perfil.PROFESSOR],
        is_staff=True,
    )
    cliente = Client()
    cliente.force_login(professor_da_equipe)

    resposta_http = cliente.get(reverse("admin:tutor_revisaoresposta_changelist"))

    assert resposta_http.status_code == 403
