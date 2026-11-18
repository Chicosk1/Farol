"""Quiz do aluno: gabarito escondido até a resposta, retorno e progresso (QUE-T40, QUE-T41)."""

import pytest
from django.conf import settings
from django.utils import timezone

from disciplinas.models import Disciplina, Matricula
from materiais.models import Material, Trecho
from nucleo.pseudonimo import pseudonimo_do_aluno
from questoes.models import ProgressoQuiz, Questao, RespostaQuiz
from tutor.models import JanelaProva

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


@pytest.fixture
def material(disciplina) -> Material:
    return Material.objects.create(
        disciplina=disciplina,
        aula_numero=3,
        aula_titulo="Pilhas e filas",
        arquivo="materiais/aula-3.pdf",
        status=Material.Status.PRONTO,
    )


@pytest.fixture
def trecho(material) -> Trecho:
    return Trecho.objects.create(
        material=material,
        pagina=2,
        ordem=0,
        texto=TEXTO,
        inicio=0,
        fim=len(TEXTO),
        vetor=[1.0] + [0.0] * (settings.FAROL_DIMENSAO_DO_VETOR - 1),
    )


def questao(material, trecho, status="publicada", **campos) -> Questao:
    dados = {
        "material": material,
        "enunciado": "Qual regra a pilha segue?",
        "alternativas": ["LIFO", "FIFO", "Por prioridade", "Aleatória"],
        "correta": 0,
        "justificativa": "Na pilha, o último a entrar é o primeiro a sair.",
        "topico": "Pilhas",
        "trecho": trecho,
        "status": status,
    }
    return Questao.objects.create(**(dados | campos))


def responder(cliente, alvo, alternativa):
    return cliente.post(
        f"/api/questoes/{alvo.id}/respostas", {"alternativa": alternativa}, format="json"
    )


@pytest.mark.requisito("QUE-RF-04", "QUE-RF-07")
def test_o_quiz_traz_so_as_publicadas_e_sem_o_gabarito(cliente_aluna, material, trecho):
    publicada = questao(material, trecho)
    questao(material, trecho, status="pendente", enunciado="Rascunho escondido da pilha?")
    questao(material, trecho, status="descartada")

    resposta = cliente_aluna.get(f"/api/materiais/{material.id}/quiz")

    assert resposta.status_code == 200
    dados = resposta.json()
    assert [q["id"] for q in dados["questoes"]] == [publicada.id]
    assert set(dados["questoes"][0]) == {"id", "enunciado", "alternativas", "topico"}
    assert b"Rascunho escondido" not in resposta.content
    assert b"justificativa" not in resposta.content.replace(b'"respostas":[]', b"")
    assert dados["respostas"] == []
    assert dados["concluido"] is False


@pytest.mark.requisito("QUE-RF-08", "QUE-RF-11")
def test_responder_devolve_o_retorno_e_registra_com_pseudonimo(
    cliente_aluna, aluna, material, trecho
):
    alvo = questao(material, trecho)

    retorno = responder(cliente_aluna, alvo, 1).json()

    assert retorno["acerto"] is False
    assert retorno["correta"] == 0
    assert retorno["justificativa"].startswith("Na pilha")
    assert retorno["trecho"] == {"id": trecho.id, "rotulo": "Aula 3, p. 2"}
    [registro] = RespostaQuiz.objects.all()
    assert registro.acerto is False
    assert registro.contexto == "quiz"
    assert registro.aluno_pseudonimo == pseudonimo_do_aluno(aluna.id, material.disciplina_id)
    assert registro.aluno_pseudonimo != str(aluna.id)
    assert registro.respondida_em == timezone.localdate()


@pytest.mark.requisito("QUE-RF-08")
def test_ao_voltar_o_aluno_continua_de_onde_parou(cliente_aluna, material, trecho):
    primeira = questao(material, trecho)
    questao(material, trecho, enunciado="Qual regra a fila segue?")
    responder(cliente_aluna, primeira, 0)

    dados = cliente_aluna.get(f"/api/materiais/{material.id}/quiz").json()

    assert [r["questao"] for r in dados["respostas"]] == [primeira.id]
    assert dados["respostas"][0]["acerto"] is True
    assert dados["concluido"] is False


def test_responder_duas_vezes_nao_registra_de_novo(cliente_aluna, material, trecho):
    alvo = questao(material, trecho)

    responder(cliente_aluna, alvo, 1)
    segundo = responder(cliente_aluna, alvo, 0).json()

    assert segundo["alternativa"] == 1  # vale a primeira resposta
    assert RespostaQuiz.objects.count() == 1


def test_terminar_e_reiniciar_o_quiz(cliente_aluna, aluna, material, trecho):
    alvo = questao(material, trecho)
    responder(cliente_aluna, alvo, 0)
    assert cliente_aluna.get(f"/api/materiais/{material.id}/quiz").json()["concluido"] is True

    assert cliente_aluna.post(f"/api/materiais/{material.id}/quiz/reiniciar").status_code == 204

    assert not ProgressoQuiz.objects.filter(aluno=aluna).exists()
    assert RespostaQuiz.objects.count() == 1  # o registro do radar fica


@pytest.mark.requisito("QUE-RF-04")
def test_rascunho_nao_pode_ser_respondido(cliente_aluna, material, trecho):
    rascunho = questao(material, trecho, status="pendente")

    assert responder(cliente_aluna, rascunho, 0).status_code == 404
    assert not RespostaQuiz.objects.exists()


def test_a_lista_de_quizzes_mostra_as_aulas_com_publicadas_e_o_andamento(
    cliente_aluna, disciplina, material, trecho
):
    alvo = questao(material, trecho)
    questao(material, trecho)
    vazia = Material.objects.create(
        disciplina=disciplina,
        aula_numero=4,
        aula_titulo="Árvores",
        arquivo="materiais/a4.pdf",
        status=Material.Status.PRONTO,
    )
    questao(vazia, trecho, status="pendente")
    responder(cliente_aluna, alvo, 0)

    lista = cliente_aluna.get(f"/api/disciplinas/{disciplina.id}/quizzes").json()

    assert lista == [
        {
            "material": material.id,
            "aula_numero": 3,
            "aula_titulo": "Pilhas e filas",
            "questoes": 2,
            "respondidas": 1,
            "acertos": 1,
        }
    ]


def test_aluno_de_fora_da_disciplina_nao_ve_o_quiz(material, trecho, db):
    from rest_framework.test import APIClient

    from contas.models import Perfil, Pessoa

    outro = Pessoa.objects.create_user(
        email="bruno.lima@exemplo.edu.br", nome="Bruno Lima", perfis=[Perfil.ALUNO]
    )
    cliente = APIClient()
    cliente.force_login(outro)
    alvo = questao(material, trecho)

    assert cliente.get(f"/api/materiais/{material.id}/quiz").status_code == 403
    assert responder(cliente, alvo, 0).status_code == 403


def test_o_professor_nao_responde_quiz(cliente_professor, material, trecho):
    assert responder(cliente_professor, questao(material, trecho), 0).status_code == 403


def test_no_modo_prova_o_quiz_fica_pausado(cliente_aluna, professor, disciplina, material, trecho):
    alvo = questao(material, trecho)
    JanelaProva.objects.create(
        disciplina=disciplina,
        inicio=timezone.now() - timezone.timedelta(minutes=5),
        criada_por=professor,
    )

    dados = cliente_aluna.get(f"/api/materiais/{material.id}/quiz").json()

    assert dados["pausado"] is True
    assert dados["questoes"] == []
    assert responder(cliente_aluna, alvo, 0).status_code == 409
    assert cliente_aluna.get(f"/api/disciplinas/{disciplina.id}/quizzes").json() == []
