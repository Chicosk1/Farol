"""Limite diário de perguntas por aluno e disciplina (TUT-T60, TUT-T61, TUT-RF-08).

O contador fica no Redis do Docker (banco separado para os testes). Dados fictícios.
"""

from datetime import UTC, date, datetime
from unittest import mock

import pytest
from django.utils import timezone

from disciplinas.models import Disciplina, Matricula
from tutor import contador, servicos
from tutor.models import ConfiguracaoTutor, JanelaProva, Mensagem


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
    ConfiguracaoTutor.objects.create(disciplina=disciplina, limite_diario=20)
    return disciplina


def perguntar(cliente, disciplina, texto="O que é uma pilha?"):
    resposta = cliente.post(
        f"/api/disciplinas/{disciplina.id}/tutor/perguntas", {"texto": texto}, format="json"
    )
    if resposta.status_code == 200:
        b"".join(resposta.streaming_content)  # consome o streaming, como o navegador
    return resposta


def ja_fez(aluna, disciplina, quantas: int) -> None:
    for _ in range(quantas):
        contador.reservar(disciplina.id, aluna.id, limite=1000)


@pytest.mark.requisito("TUT-RF-08")
def test_com_limite_20_a_21a_pergunta_do_dia_e_recusada_e_nao_e_enviada(
    cliente_aluna, aluna, disciplina
):
    ja_fez(aluna, disciplina, 19)
    assert perguntar(cliente_aluna, disciplina).status_code == 200  # a 20ª ainda vale

    with mock.patch.object(servicos.ia, "responder") as modelo:
        resposta = perguntar(cliente_aluna, disciplina, "E uma fila?")

    assert resposta.status_code == 429
    assert resposta.json() == {
        "detail": "Você chegou ao limite de 20 perguntas de hoje. O limite volta amanhã."
    }
    modelo.assert_not_called()
    assert Mensagem.objects.filter(texto="E uma fila?").count() == 0
    assert contador.usadas(disciplina.id, aluna.id) == 20


@pytest.mark.requisito("TUT-RF-08")
def test_cada_pergunta_aceita_conta_uma_no_uso_do_dia(cliente_aluna, aluna, disciplina):
    perguntar(cliente_aluna, disciplina)
    perguntar(cliente_aluna, disciplina, "E uma fila?")

    assert contador.usadas(disciplina.id, aluna.id) == 2


@pytest.mark.requisito("TUT-RF-08")
def test_quando_o_professor_muda_o_limite_para_60_o_novo_limite_ja_vale(
    cliente_aluna, aluna, disciplina
):
    ja_fez(aluna, disciplina, 20)
    assert perguntar(cliente_aluna, disciplina).status_code == 429

    ConfiguracaoTutor.objects.filter(disciplina=disciplina).update(limite_diario=60)

    assert perguntar(cliente_aluna, disciplina).status_code == 200


@pytest.mark.requisito("TUT-RF-08")
def test_o_contador_zera_na_virada_do_dia_no_horario_de_brasilia(aluna, disciplina):
    with mock.patch.object(contador, "hoje", return_value=date(2026, 11, 19)):
        ja_fez(aluna, disciplina, 20)
        assert not contador.reservar(disciplina.id, aluna.id, limite=20)

    with mock.patch.object(contador, "hoje", return_value=date(2026, 11, 20)):
        assert contador.usadas(disciplina.id, aluna.id) == 0
        assert contador.reservar(disciplina.id, aluna.id, limite=20)


def test_o_dia_e_o_de_brasilia_e_a_chave_expira_em_48_horas(aluna, disciplina, settings):
    settings.TIME_ZONE = "America/Sao_Paulo"
    with mock.patch("django.utils.timezone.now") as agora:
        agora.return_value = datetime(2026, 11, 20, 2, 30, tzinfo=UTC)  # 23h30 em Brasília
        assert contador.hoje() == date(2026, 11, 19)

    contador.reservar(disciplina.id, aluna.id, limite=20)
    chave = contador.chave(disciplina.id, aluna.id, contador.hoje())
    assert 0 < contador.cliente().ttl(chave) <= 48 * 3600


def test_o_limite_e_por_disciplina(professor, aluna, disciplina):
    outra = Disciplina.objects.create(
        codigo="SINF202",
        nome="Banco de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    ja_fez(aluna, disciplina, 20)

    assert contador.reservar(outra.id, aluna.id, limite=20)


def test_pergunta_recusada_por_provedor_fora_do_ar_nao_gasta_o_limite(
    cliente_aluna, aluna, disciplina
):
    # O vetor da pergunta também vem do provedor: fora do ar, nada é respondido.
    fora_do_ar = RuntimeError("fora do ar")
    with mock.patch.object(servicos.ia, "gerar_embedding", side_effect=fora_do_ar):
        assert perguntar(cliente_aluna, disciplina).status_code == 503

    assert contador.usadas(disciplina.id, aluna.id) == 0


def test_pergunta_invalida_ou_em_prova_nao_gasta_o_limite(cliente_aluna, aluna, disciplina):
    assert perguntar(cliente_aluna, disciplina, "").status_code == 400
    JanelaProva.objects.create(disciplina=disciplina, inicio=timezone.now())
    assert perguntar(cliente_aluna, disciplina).status_code == 423

    assert contador.usadas(disciplina.id, aluna.id) == 0
