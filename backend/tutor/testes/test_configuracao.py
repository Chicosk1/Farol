"""Configuração do tutor pelo professor: modo pistas, limite diário e política (TUT-T42, TUT-RF-06).

A IA é o adaptador falso. Dados fictícios.
"""

import json

import pytest
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from ia import servicos as ia
from materiais.models import Material, Trecho
from tutor.models import ConfiguracaoTutor

PILHA = "Uma pilha segue a ordem LIFO: o último elemento inserido é o primeiro a sair."


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
    material = Material.objects.create(
        disciplina=disciplina,
        aula_numero=5,
        aula_titulo="Pilhas",
        arquivo="x.pdf",
        status=Material.Status.PRONTO,
    )
    Trecho.objects.create(
        material=material,
        pagina=3,
        ordem=0,
        texto=PILHA,
        inicio=0,
        fim=len(PILHA),
        vetor=ia.gerar_embedding(PILHA),
    )
    return disciplina


def url(disciplina) -> str:
    return f"/api/disciplinas/{disciplina.id}/tutor/configuracao"


def resposta_do_tutor(cliente, disciplina, texto: str) -> tuple[str, str]:
    """O tipo da resposta e o texto completo, lidos dos eventos SSE."""
    resposta = cliente.post(
        f"/api/disciplinas/{disciplina.id}/tutor/perguntas", {"texto": texto}, format="json"
    )
    tipo, partes = "", []
    for bloco in b"".join(resposta.streaming_content).decode().strip().split("\n\n"):
        evento, dados = (linha.split(": ", 1)[1] for linha in bloco.split("\n"))
        if evento == "texto":
            partes.append(json.loads(dados)["texto"])
        if evento == "fim":
            tipo = json.loads(dados)["tipo"]
    return tipo, "".join(partes)


@pytest.mark.requisito("TUT-RF-06")
def test_o_padrao_e_modo_pistas_ligado_limite_40_e_sem_politica(cliente_professor, disciplina):
    resposta = cliente_professor.get(url(disciplina))

    assert resposta.status_code == 200
    assert resposta.json() == {"modo_pistas": True, "limite_diario": 40, "politica": ""}


@pytest.mark.requisito("TUT-RF-06")
def test_o_professor_desliga_o_modo_pistas_e_o_tutor_explica_a_solucao_com_citacao(
    cliente_professor, cliente_aluna, disciplina
):
    pedido = "Me dá a resposta do exercício de pilha"
    assert resposta_do_tutor(cliente_aluna, disciplina, pedido)[0] == "pistas"

    alterada = cliente_professor.patch(url(disciplina), {"modo_pistas": False}, format="json")

    assert alterada.status_code == 200
    assert alterada.json()["modo_pistas"] is False
    tipo, texto = resposta_do_tutor(cliente_aluna, disciplina, pedido)
    assert tipo == "resposta"
    assert "LIFO" in texto and "[1]" in texto


@pytest.mark.requisito("TUT-RF-05")
def test_com_o_modo_pistas_ligado_a_pergunta_conceitual_tem_resposta_normal(
    cliente_aluna, disciplina
):
    tipo, texto = resposta_do_tutor(cliente_aluna, disciplina, "O que é uma pilha?")

    assert tipo == "resposta"
    assert "LIFO" in texto


@pytest.mark.requisito("TUT-RF-08")
def test_o_professor_muda_o_limite_diario_e_a_politica(cliente_professor, disciplina):
    resposta = cliente_professor.patch(
        url(disciplina),
        {"limite_diario": 60, "politica": "Use o tutor para estudar, não para copiar."},
        format="json",
    )

    assert resposta.status_code == 200
    configuracao = ConfiguracaoTutor.objects.get(disciplina=disciplina)
    assert configuracao.limite_diario == 60
    assert configuracao.politica == "Use o tutor para estudar, não para copiar."
    assert configuracao.modo_pistas is True  # o que não veio continua igual


@pytest.mark.requisito("TUT-RF-08")
def test_limite_fora_de_20_40_e_60_recebe_400(cliente_professor, disciplina):
    resposta = cliente_professor.patch(url(disciplina), {"limite_diario": 100}, format="json")

    assert resposta.status_code == 400
    assert "limite_diario" in resposta.json()


@pytest.mark.requisito("ACE-RF-05")
def test_so_o_professor_da_disciplina_ve_e_muda_a_configuracao(
    cliente_aluna, professor, disciplina
):
    outro = Pessoa.objects.create_user(
        email="rita.lima@exemplo.edu.br", nome="Rita Lima", perfis=[Perfil.PROFESSOR]
    )
    cliente_do_outro = APIClient()
    cliente_do_outro.force_login(outro)

    assert cliente_aluna.get(url(disciplina)).status_code == 403
    desligar = {"modo_pistas": False}
    assert cliente_aluna.patch(url(disciplina), desligar, format="json").status_code == 403
    assert cliente_do_outro.patch(url(disciplina), desligar, format="json").status_code == 403
    assert not ConfiguracaoTutor.objects.filter(modo_pistas=False).exists()
