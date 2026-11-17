"""Prévia e envio da dúvida ao professor (DUV-T10, DUV-T11). Dados fictícios."""

import pytest
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from duvidas.models import Duvida, EnvioDuvida
from notificacoes.models import Notificacao
from tutor.models import Conversa, Mensagem

NAO_ENCONTREI = "Não encontrei isso no material da disciplina."


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


def conversa_com(aluno, disciplina, pergunta: str, tipo="nao_encontrado") -> Mensagem:
    conversa, _ = Conversa.objects.get_or_create(aluno=aluno, disciplina=disciplina)
    Mensagem.objects.create(conversa=conversa, autor="aluno", texto=pergunta)
    texto = NAO_ENCONTREI if tipo == "nao_encontrado" else "Uma pilha é LIFO. [1]"
    return Mensagem.objects.create(conversa=conversa, autor="tutor", texto=texto, tipo=tipo)


@pytest.fixture
def resposta(aluna, disciplina) -> Mensagem:
    return conversa_com(aluna, disciplina, "Sou [nome], a prova cobre árvores AVL?")


def previa(cliente, mensagem):
    return cliente.post(f"/api/mensagens/{mensagem.id}/duvida/previa")


def enviar(cliente, mensagem):
    return cliente.post(f"/api/mensagens/{mensagem.id}/duvida")


@pytest.mark.requisito("DUV-RF-02")
def test_a_previa_mostra_o_texto_exato_sem_dados_pessoais(cliente_aluna, resposta):
    dados = previa(cliente_aluna, resposta)

    assert dados.status_code == 200
    assert dados.json() == {"texto_filtrado": "Sou [nome], a prova cobre árvores AVL?"}
    assert not Duvida.objects.exists()  # a prévia não envia nada


@pytest.mark.requisito("DUV-RF-01")
def test_enviar_cria_a_duvida_da_disciplina_sem_ligacao_com_o_aluno(
    cliente_aluna, resposta, disciplina
):
    criada = enviar(cliente_aluna, resposta)

    assert criada.status_code == 201
    duvida = Duvida.objects.get()
    assert criada.json() == {"duvida_id": duvida.id, "status": "aberta"}
    assert (duvida.disciplina, duvida.texto, duvida.status) == (
        disciplina,
        "Sou [nome], a prova cobre árvores AVL?",
        "aberta",
    )
    assert duvida.vista is False
    assert not hasattr(duvida, "aluno")  # só o EnvioDuvida, do lado do aluno, sabe quem enviou
    assert EnvioDuvida.objects.get().mensagem == resposta


@pytest.mark.requisito("DUV-RF-04")
def test_a_mesma_duvida_nao_e_enviada_duas_vezes(cliente_aluna, resposta):
    enviar(cliente_aluna, resposta)

    assert enviar(cliente_aluna, resposta).status_code == 409
    assert previa(cliente_aluna, resposta).status_code == 409
    assert Duvida.objects.count() == 1


@pytest.mark.requisito("DUV-RF-01")
def test_so_a_resposta_nao_encontrei_vira_duvida(cliente_aluna, aluna, disciplina):
    respondida = conversa_com(aluna, disciplina, "O que é uma pilha?", tipo="resposta")
    pergunta = Mensagem.objects.get(autor="aluno")

    assert previa(cliente_aluna, respondida).status_code == 400
    assert enviar(cliente_aluna, respondida).status_code == 400
    assert enviar(cliente_aluna, pergunta).status_code == 400


def test_a_mensagem_de_outro_aluno_recebe_404(resposta):
    colega = Pessoa.objects.create_user(
        email="bruno.dias@exemplo.edu.br", nome="Bruno Dias", perfis=[Perfil.ALUNO]
    )
    cliente = APIClient()
    cliente.force_login(colega)

    assert previa(cliente, resposta).status_code == 404
    assert enviar(cliente, resposta).status_code == 404


def test_cada_aluno_envia_no_maximo_5_duvidas_por_disciplina_por_dia(
    cliente_aluna, aluna, disciplina
):
    respostas = [conversa_com(aluna, disciplina, f"Dúvida {n}?") for n in range(6)]
    for resposta in respostas[:5]:
        assert enviar(cliente_aluna, resposta).status_code == 201

    sexta = enviar(cliente_aluna, respostas[5])

    assert sexta.status_code == 429
    assert sexta.json() == {
        "detail": "Você já enviou 5 dúvidas hoje nesta disciplina. Tente de novo amanhã."
    }
    assert Duvida.objects.count() == 5


def test_o_professor_nao_envia_duvida(cliente_professor, resposta):
    assert enviar(cliente_professor, resposta).status_code == 403


@pytest.mark.requisito("DUV-RF-06")
def test_a_duvida_nova_avisa_o_professor_no_sino_sem_o_nome_do_aluno(
    cliente_aluna, resposta, professor, disciplina
):
    enviar(cliente_aluna, resposta)

    aviso = Notificacao.objects.get()
    assert aviso.pessoa == professor
    assert aviso.tipo == "duvida_nova"
    assert aviso.texto == (
        "Nova dúvida em Estruturas de Dados: Sou [nome], a prova cobre árvores AVL?"
    )
    assert aviso.link == f"/disciplinas/{disciplina.id}/duvidas"
    assert "Ana" not in aviso.texto
