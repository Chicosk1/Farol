"""O SM-2 da revisão do dia, em casos de tabela (REV-T11). Função pura, sem banco."""

from datetime import date, timedelta

import pytest

from revisao.agenda import agendar, quando_volta

HOJE = date(2026, 11, 18)


@pytest.mark.requisito("REV-RF-04")
@pytest.mark.parametrize("avaliacao", ["dificil", "bom", "facil"])
def test_resposta_errada_volta_amanha_e_recomeca(avaliacao):
    agenda = agendar(2.5, 10, 4, acerto=False, avaliacao=avaliacao, hoje=HOJE)

    assert agenda.proxima_data == HOJE + timedelta(days=1)
    assert agenda.repeticoes == 0
    assert agenda.facilidade < 2.5


@pytest.mark.requisito("REV-RF-04")
@pytest.mark.parametrize(("avaliacao", "dias"), [("dificil", 1), ("bom", 3), ("facil", 4)])
def test_primeiro_acerto_segue_os_intervalos_do_prototipo(avaliacao, dias):
    agenda = agendar(2.5, 0, 0, acerto=True, avaliacao=avaliacao, hoje=HOJE)

    assert agenda.intervalo_dias == dias
    assert agenda.repeticoes == 1


@pytest.mark.requisito("REV-RF-04")
def test_facil_varias_vezes_seguidas_o_intervalo_cresce_a_cada_vez():
    facilidade, intervalo, repeticoes = 2.5, 0, 0
    intervalos = []
    for _ in range(5):
        agenda = agendar(facilidade, intervalo, repeticoes, True, "facil", HOJE)
        facilidade, intervalo, repeticoes = (
            agenda.facilidade,
            agenda.intervalo_dias,
            agenda.repeticoes,
        )
        intervalos.append(intervalo)

    assert intervalos == sorted(intervalos)
    assert len(set(intervalos)) == len(intervalos)


def test_dificil_volta_antes_que_facil():
    dificil = agendar(2.5, 6, 2, True, "dificil", HOJE)
    facil = agendar(2.5, 6, 2, True, "facil", HOJE)

    assert dificil.proxima_data < facil.proxima_data


def test_a_facilidade_nunca_cai_abaixo_de_1_3():
    agenda = agendar(1.3, 1, 0, acerto=False, avaliacao="bom", hoje=HOJE)

    assert agenda.facilidade == 1.3


def test_avaliacao_desconhecida_e_recusada():
    with pytest.raises(ValueError):
        agendar(2.5, 0, 0, True, "otimo", HOJE)


@pytest.mark.requisito("REV-RF-05")
def test_o_texto_diz_quando_o_cartao_volta():
    assert quando_volta(HOJE + timedelta(days=1), HOJE) == "Este cartão volta amanhã."
    assert quando_volta(HOJE + timedelta(days=3), HOJE) == "Este cartão volta em 3 dias."
