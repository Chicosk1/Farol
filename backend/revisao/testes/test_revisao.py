"""A revisão do dia: montagem da sessão, resposta, avaliação, retomada e sequência
(REV-T20, REV-T21, REV-T22, REV-T30, REV-T40). Dados fictícios."""

from datetime import timedelta

import pytest
from django.conf import settings
from django.core import mail
from django.utils import timezone

from disciplinas.models import Disciplina, Matricula
from materiais.models import Material, Trecho
from questoes.models import Questao, RespostaQuiz
from revisao import servicos
from revisao.models import Cartao, PreferenciaLembrete, SessaoRevisao
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
def trecho(disciplina) -> Trecho:
    material = Material.objects.create(
        disciplina=disciplina,
        aula_numero=3,
        aula_titulo="Pilhas e filas",
        arquivo="materiais/aula-3.pdf",
        status=Material.Status.PRONTO,
    )
    return Trecho.objects.create(
        material=material,
        pagina=2,
        ordem=0,
        texto=TEXTO,
        inicio=0,
        fim=len(TEXTO),
        vetor=[1.0] + [0.0] * (settings.FAROL_DIMENSAO_DO_VETOR - 1),
    )


def questao(trecho, n=1, status="publicada") -> Questao:
    return Questao.objects.create(
        material=trecho.material,
        enunciado=f"Qual regra a pilha segue? ({n})",
        alternativas=["LIFO", "FIFO", "Por prioridade", "Aleatória"],
        correta=0,
        justificativa="Na pilha, o último a entrar é o primeiro a sair.",
        topico="Pilhas",
        trecho=trecho,
        status=status,
    )


def hoje(cliente):
    return cliente.get("/api/revisao/hoje").json()


def responder(cliente, cartao_id, alternativa):
    return cliente.post(
        f"/api/revisao/cartoes/{cartao_id}/resposta", {"alternativa": alternativa}, format="json"
    )


def avaliar(cliente, cartao_id, avaliacao):
    return cliente.post(
        f"/api/revisao/cartoes/{cartao_id}/avaliacao", {"avaliacao": avaliacao}, format="json"
    )


@pytest.mark.requisito("REV-RF-01", "REV-RF-06")
def test_cada_questao_publicada_vira_um_cartao_na_revisao_de_hoje(cliente_aluna, aluna, trecho):
    questao(trecho, 1)
    questao(trecho, 2)
    questao(trecho, 3, status="pendente")

    dados = hoje(cliente_aluna)

    assert len(dados["cartoes"]) == 2
    assert Cartao.objects.filter(aluno=aluna).count() == 2
    assert dados["disciplinas"] == ["Estruturas de Dados"]
    assert dados["minutos"] == 1
    assert "correta" not in dados["cartoes"][0]
    assert dados["tem_questoes"] is True


@pytest.mark.requisito("REV-RF-02")
def test_a_sessao_tem_no_maximo_10_cartoes_e_os_dificeis_e_atrasados_primeiro(
    cliente_aluna, aluna, trecho
):
    for n in range(14):
        questao(trecho, n)
    servicos._garantir_cartoes(aluna, set(Questao.objects.values_list("id", flat=True)))
    cartoes = list(Cartao.objects.filter(aluno=aluna).order_by("id"))
    dia = servicos.dia_da_revisao()
    cartoes[5].ultima_avaliacao = "dificil"
    cartoes[5].save()
    cartoes[9].proxima_data = dia - timedelta(days=10)
    cartoes[9].save()

    ids = [c["id"] for c in hoje(cliente_aluna)["cartoes"]]

    assert len(ids) == 10
    assert ids[:2] == [cartoes[5].id, cartoes[9].id]


@pytest.mark.requisito("REV-RF-03", "REV-RF-04", "REV-RF-05")
def test_responder_e_avaliar_mostra_o_retorno_e_quando_o_cartao_volta(cliente_aluna, aluna, trecho):
    questao(trecho)
    cartao_id = hoje(cliente_aluna)["cartoes"][0]["id"]

    retorno = responder(cliente_aluna, cartao_id, 0).json()
    assert retorno["acerto"] is True
    assert retorno["trecho"]["rotulo"] == "Aula 3, p. 2"
    agenda = avaliar(cliente_aluna, cartao_id, "bom").json()

    assert agenda["texto"] == "Este cartão volta em 3 dias."
    cartao = Cartao.objects.get(id=cartao_id)
    assert cartao.proxima_data == servicos.dia_da_revisao() + timedelta(days=3)
    assert RespostaQuiz.objects.get().contexto == "revisao"


def test_errar_faz_o_cartao_voltar_amanha(cliente_aluna, trecho):
    questao(trecho)
    cartao_id = hoje(cliente_aluna)["cartoes"][0]["id"]

    responder(cliente_aluna, cartao_id, 2)

    assert avaliar(cliente_aluna, cartao_id, "facil").json()["texto"] == "Este cartão volta amanhã."


@pytest.mark.requisito("REV-RF-06", "REV-RF-07")
def test_ao_voltar_continua_e_ao_terminar_a_sequencia_conta_o_dia(cliente_aluna, aluna, trecho):
    questao(trecho, 1)
    questao(trecho, 2)
    primeiro, segundo = (c["id"] for c in hoje(cliente_aluna)["cartoes"])
    responder(cliente_aluna, primeiro, 0)
    avaliar(cliente_aluna, primeiro, "facil")

    no_meio = hoje(cliente_aluna)
    assert [r["cartao"] for r in no_meio["respostas"]] == [primeiro]
    assert no_meio["concluida"] is False

    responder(cliente_aluna, segundo, 0)
    avaliar(cliente_aluna, segundo, "bom")
    fim = hoje(cliente_aluna)

    assert fim["concluida"] is True
    assert fim["dias_seguidos"] == 1
    assert fim["sequencia"][-1]["feita"] is True
    assert len(fim["sequencia"]) == 7


def test_dias_seguidos_contam_os_dias_anteriores(cliente_aluna, aluna, trecho):
    dia = servicos.dia_da_revisao()
    for d in (1, 2, 4):
        SessaoRevisao.objects.create(aluno=aluna, data=dia - timedelta(days=d), concluida=True)

    assert hoje(cliente_aluna)["dias_seguidos"] == 2


def test_nao_responde_duas_vezes_nem_avalia_sem_responder(cliente_aluna, trecho):
    questao(trecho)
    cartao_id = hoje(cliente_aluna)["cartoes"][0]["id"]

    assert avaliar(cliente_aluna, cartao_id, "bom").status_code == 409
    responder(cliente_aluna, cartao_id, 0)
    assert responder(cliente_aluna, cartao_id, 1).status_code == 409


def test_cartao_de_fora_da_sessao_recebe_404(cliente_aluna, trecho):
    assert responder(cliente_aluna, 999, 0).status_code == 404


def test_questao_despublicada_sai_da_revisao(cliente_aluna, trecho):
    alvo = questao(trecho)
    assert len(hoje(cliente_aluna)["cartoes"]) == 1

    alvo.status = "pendente"
    alvo.save()

    assert hoje(cliente_aluna)["cartoes"] == []


def test_no_modo_prova_os_cartoes_da_disciplina_ficam_de_fora(
    cliente_aluna, professor, disciplina, trecho
):
    questao(trecho)
    JanelaProva.objects.create(
        disciplina=disciplina, inicio=timezone.now() - timedelta(minutes=5), criada_por=professor
    )

    assert hoje(cliente_aluna)["cartoes"] == []


def test_sem_questoes_publicadas_explica_que_a_revisao_ainda_nao_comecou(cliente_aluna, trecho):
    dados = hoje(cliente_aluna)

    assert dados["cartoes"] == []
    assert dados["tem_questoes"] is False


def test_a_sessao_das_6h_e_montada_para_cada_aluno(aluna, trecho):
    questao(trecho)

    assert servicos.montar_sessoes_do_dia() == 1
    assert SessaoRevisao.objects.filter(aluno=aluna).count() == 1


def test_o_professor_nao_tem_revisao(cliente_professor):
    assert cliente_professor.get("/api/revisao/hoje").status_code == 403


@pytest.mark.requisito("REV-RF-09")
def test_o_lembrete_comeca_desligado_e_pode_ser_ligado(cliente_aluna):
    assert cliente_aluna.get("/api/eu/lembrete").json() == {"ligado": False, "horario": "19:00"}

    resposta = cliente_aluna.put(
        "/api/eu/lembrete", {"ligado": True, "horario": "07:00"}, format="json"
    )

    assert resposta.json() == {"ligado": True, "horario": "07:00"}


@pytest.mark.requisito("REV-RF-09")
def test_o_lembrete_so_vai_para_quem_ligou_e_tem_cartoes(aluna, trecho):
    import datetime

    agora = timezone.localtime().replace(hour=20, minute=0)
    PreferenciaLembrete.objects.create(aluno=aluna, ligado=False, horario=datetime.time(19, 0))
    assert servicos.enviar_lembretes(agora) == 0

    PreferenciaLembrete.objects.filter(aluno=aluna).update(ligado=True)
    assert servicos.enviar_lembretes(agora) == 0  # sem questões publicadas, nada a revisar

    questao(trecho)
    assert servicos.enviar_lembretes(agora) == 1
    assert mail.outbox[0].to == [aluna.email]
    assert servicos.enviar_lembretes(agora) == 0  # um por dia
