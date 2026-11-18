"""GET /api/disciplinas/{id}/tutor: o que a tela do tutor mostra ao abrir (TUT-T26).

A IA é o adaptador falso. Dados fictícios.
"""

import pytest
from django.utils import timezone

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from ia import servicos as ia
from materiais.models import Material, Trecho
from tutor import contador
from tutor.models import ConfiguracaoTutor, Conversa, JanelaProva, Mensagem

LISTA = "Uma lista encadeada é formada por nós com ponteiros para o próximo nó."


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
        aula_numero=4,
        aula_titulo="Listas encadeadas",
        arquivo="x.pdf",
        status=Material.Status.PRONTO,
    )
    Trecho.objects.create(
        material=material,
        pagina=5,
        ordem=0,
        texto=LISTA,
        inicio=0,
        fim=len(LISTA),
        vetor=ia.gerar_embedding(LISTA),
    )
    return disciplina


def url(disciplina) -> str:
    return f"/api/disciplinas/{disciplina.id}/tutor"


def perguntar(cliente, disciplina, texto: str) -> None:
    resposta = cliente.post(f"{url(disciplina)}/perguntas", {"texto": texto}, format="json")
    b"".join(resposta.streaming_content)


@pytest.mark.requisito("TUT-RF-08")
def test_tutor_novo_mostra_o_padrao_sem_conversa_e_com_o_uso_zerado(cliente_aluna, disciplina):
    resposta = cliente_aluna.get(url(disciplina))

    assert resposta.status_code == 200
    assert resposta.json() == {
        "modo_pistas": True,
        "politica": "",
        "pausado": False,
        "uso": {"usadas": 0, "limite": 40},
        "conversa_id": None,
        "mensagens": [],
        "sugestoes": ["Quais são as ideias principais da aula 4, Listas encadeadas?"],
    }


@pytest.mark.requisito("TUT-RF-12")
def test_a_conversa_guardada_volta_com_as_citacoes_e_o_uso_do_dia(cliente_aluna, disciplina):
    perguntar(cliente_aluna, disciplina, "O que é uma lista encadeada?")

    dados = cliente_aluna.get(url(disciplina)).json()

    conversa = Conversa.objects.get()
    pergunta, resposta = conversa.mensagens.all()
    trecho = Trecho.objects.get()
    assert dados["conversa_id"] == conversa.id
    assert dados["uso"] == {"usadas": 1, "limite": 40}
    assert [m["id"] for m in dados["mensagens"]] == [pergunta.id, resposta.id]
    primeira, segunda = dados["mensagens"]
    assert (primeira["autor"], primeira["texto"], primeira["citacoes"]) == (
        "aluno",
        "O que é uma lista encadeada?",
        [],
    )
    assert (segunda["autor"], segunda["tipo"], segunda["avaliacao"]) == ("tutor", "resposta", "")
    assert segunda["texto"] == resposta.texto
    assert segunda["citacoes"] == [
        {
            "ordem": 1,
            "rotulo": "Aula 4, p. 5",
            "trecho_id": trecho.id,
            "material_id": trecho.material_id,
            "pagina": 5,
        }
    ]


@pytest.mark.requisito("TUT-RF-07")
def test_em_prova_o_tutor_aparece_pausado(cliente_aluna, disciplina):
    JanelaProva.objects.create(disciplina=disciplina, inicio=timezone.now())

    assert cliente_aluna.get(url(disciplina)).json()["pausado"] is True


@pytest.mark.requisito("TUT-RF-10")
def test_a_tela_recebe_a_politica_o_modo_pistas_e_o_limite_do_professor(
    cliente_aluna, aluna, disciplina
):
    ConfiguracaoTutor.objects.create(
        disciplina=disciplina,
        modo_pistas=False,
        limite_diario=60,
        politica="Use o tutor para estudar, não para copiar.",
    )
    for _ in range(12):
        contador.reservar(disciplina.id, aluna.id, limite=60)

    dados = cliente_aluna.get(url(disciplina)).json()

    assert dados["modo_pistas"] is False
    assert dados["politica"] == "Use o tutor para estudar, não para copiar."
    assert dados["uso"] == {"usadas": 12, "limite": 60}  # "12 de 60 perguntas hoje"


def test_o_aluno_so_ve_a_propria_conversa(cliente_aluna, professor, disciplina):
    colega = Pessoa.objects.create_user(
        email="bruno.dias@exemplo.edu.br", nome="Bruno Dias", perfis=[Perfil.ALUNO]
    )
    Matricula.objects.create(aluno=colega, disciplina=disciplina)
    conversa = Conversa.objects.create(aluno=colega, disciplina=disciplina)
    Mensagem.objects.create(conversa=conversa, autor="aluno", texto="Pergunta do colega")

    dados = cliente_aluna.get(url(disciplina)).json()

    assert dados["conversa_id"] is None
    assert dados["mensagens"] == []


@pytest.mark.requisito("ACE-RF-05")
def test_professor_recebe_403_e_sem_login_recebe_401(cliente_professor, cliente, disciplina):
    assert cliente_professor.get(url(disciplina)).status_code == 403
    assert cliente.get(url(disciplina)).status_code == 401
