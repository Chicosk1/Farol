"""Janelas de prova: o tutor pausa na hora ou num horário agendado (TUT-T50, TUT-T51, TUT-RF-07).

Dados fictícios. A IA é o adaptador falso.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

from disciplinas.models import Disciplina, Matricula
from tutor import servicos
from tutor.models import JanelaProva, Mensagem

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
PAUSADO = "O tutor está pausado durante a prova."


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


def url_janelas(disciplina) -> str:
    return f"/api/disciplinas/{disciplina.id}/janelas-prova"


def perguntar(cliente, disciplina, texto="O que é uma pilha?"):
    return cliente.post(
        f"/api/disciplinas/{disciplina.id}/tutor/perguntas", {"texto": texto}, format="json"
    )


@pytest.mark.requisito("TUT-RF-07")
def test_modo_prova_imediato_pausa_o_tutor_e_o_aluno_nao_consegue_perguntar(
    cliente_professor, cliente_aluna, disciplina
):
    criada = cliente_professor.post(url_janelas(disciplina), {}, format="json")

    assert criada.status_code == 201
    assert criada.json()["fim"] is None  # imediato: começa agora e fica aberta
    resposta = perguntar(cliente_aluna, disciplina)
    assert resposta.status_code == 423
    assert resposta.json() == {"detail": PAUSADO}
    assert Mensagem.objects.count() == 0


@pytest.mark.requisito("TUT-RF-07")
def test_desligar_o_modo_prova_volta_a_liberar_o_tutor(
    cliente_professor, cliente_aluna, disciplina
):
    janela = cliente_professor.post(url_janelas(disciplina), {}, format="json").json()

    apagada = cliente_professor.delete(f"{url_janelas(disciplina)}/{janela['id']}")

    assert apagada.status_code == 204
    assert not JanelaProva.objects.exists()
    assert perguntar(cliente_aluna, disciplina).status_code == 200


@pytest.mark.requisito("TUT-RF-07")
def test_janela_agendada_de_quinta_das_19h_as_22h_pausa_so_dentro_do_horario(disciplina):
    quinta = datetime(2026, 11, 19, tzinfo=SAO_PAULO)
    JanelaProva.objects.create(
        disciplina=disciplina,
        inicio=quinta.replace(hour=19),
        fim=quinta.replace(hour=22),
    )

    def pausado_as(hora: int, minuto: int = 0) -> bool:
        return servicos.tutor_pausado(disciplina.id, quinta.replace(hour=hora, minute=minuto))

    assert not pausado_as(18, 59)
    assert pausado_as(19)
    assert pausado_as(21, 59)
    assert not pausado_as(22)  # às 22h volta a responder


@pytest.mark.requisito("TUT-RF-07")
def test_janela_que_comeca_no_meio_da_conversa_bloqueia_a_proxima_pergunta(
    cliente_aluna, disciplina
):
    assert perguntar(cliente_aluna, disciplina).status_code == 200

    JanelaProva.objects.create(disciplina=disciplina, inicio=timezone.now())

    resposta = perguntar(cliente_aluna, disciplina, "E uma fila?")
    assert resposta.status_code == 423
    assert resposta.json() == {"detail": PAUSADO}


def test_a_pausa_de_uma_disciplina_nao_afeta_as_outras(professor, disciplina):
    outra = Disciplina.objects.create(
        codigo="SINF202",
        nome="Banco de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    JanelaProva.objects.create(disciplina=outra, inicio=timezone.now())

    assert servicos.tutor_pausado(outra.id)
    assert not servicos.tutor_pausado(disciplina.id)


@pytest.mark.requisito("TUT-RF-07")
def test_o_professor_agenda_uma_janela_e_ve_as_janelas_atuais_e_futuras(
    cliente_professor, professor, disciplina
):
    agora = timezone.now()
    JanelaProva.objects.create(
        disciplina=disciplina, inicio=agora - timedelta(days=2), fim=agora - timedelta(days=1)
    )
    inicio, fim = agora + timedelta(days=3), agora + timedelta(days=3, hours=3)

    criada = cliente_professor.post(
        url_janelas(disciplina),
        {"inicio": inicio.isoformat(), "fim": fim.isoformat()},
        format="json",
    )

    assert criada.status_code == 201
    janela = JanelaProva.objects.get(id=criada.json()["id"])
    assert (janela.inicio, janela.fim, janela.criada_por) == (inicio, fim, professor)
    lista = cliente_professor.get(url_janelas(disciplina)).json()
    assert [j["id"] for j in lista] == [janela.id]  # a janela que já passou não aparece


def test_janela_com_fim_antes_do_inicio_recebe_400(cliente_professor, disciplina):
    agora = timezone.now()

    resposta = cliente_professor.post(
        url_janelas(disciplina),
        {"inicio": agora.isoformat(), "fim": (agora - timedelta(hours=1)).isoformat()},
        format="json",
    )

    assert resposta.status_code == 400
    assert "fim" in resposta.json()


def test_janela_de_outra_disciplina_nao_pode_ser_apagada_por_esta_rota(
    cliente_professor, professor, disciplina
):
    outra = Disciplina.objects.create(
        codigo="SINF202",
        nome="Banco de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    janela = JanelaProva.objects.create(disciplina=outra, inicio=timezone.now())

    resposta = cliente_professor.delete(f"{url_janelas(disciplina)}/{janela.id}")

    assert resposta.status_code == 404
    assert JanelaProva.objects.filter(id=janela.id).exists()


@pytest.mark.requisito("ACE-RF-05")
def test_so_o_professor_da_disciplina_mexe_nas_janelas(cliente_aluna, disciplina):
    assert cliente_aluna.post(url_janelas(disciplina), {}, format="json").status_code == 403
    assert cliente_aluna.get(url_janelas(disciplina)).status_code == 403
