"""ia.gerar_questoes com o provedor falso (QUE-T11). Sem internet e sem custo. Dados fictícios."""

import json

import pytest

from ia import servicos
from ia.porta import TrechoNumerado

TRECHOS = [
    TrechoNumerado(1, "Uma pilha segue a ordem LIFO. O último a entrar é o primeiro a sair."),
    TrechoNumerado(2, "Uma fila segue a ordem FIFO. O primeiro a entrar é o primeiro a sair."),
]


def questoes(trechos=TRECHOS, quantidade=5) -> list[dict]:
    return json.loads(servicos.gerar_questoes("regras", trechos, quantidade))["questoes"]


def test_o_falso_devolve_a_quantidade_pedida_em_json():
    assert len(questoes(quantidade=7)) == 7


@pytest.mark.requisito("QUE-RF-02")
def test_cada_questao_tem_4_alternativas_distintas_gabarito_justificativa_e_trecho():
    for questao in questoes():
        assert len(questao["alternativas"]) == 4
        assert len({a.casefold() for a in questao["alternativas"]}) == 4
        assert questao["correta"] in range(4)
        assert questao["justificativa"]
        assert questao["topico"]
        assert questao["trecho"] in {1, 2}


def test_a_alternativa_correta_sai_do_trecho_citado():
    textos = {t.numero: t.texto for t in TRECHOS}
    for questao in questoes():
        assert questao["alternativas"][questao["correta"]] in textos[questao["trecho"]]


def test_com_um_trecho_so_as_erradas_vem_da_reserva():
    unica = questoes(trechos=TRECHOS[:1], quantidade=5)[0]

    assert len(set(unica["alternativas"])) == 4


def test_a_mesma_entrada_gera_sempre_as_mesmas_questoes():
    assert questoes() == questoes()


def test_sem_trechos_o_modelo_nao_e_chamado():
    with pytest.raises(ValueError):
        servicos.gerar_questoes("regras", [], 5)


def test_quantidade_zero_e_recusada():
    with pytest.raises(ValueError):
        servicos.gerar_questoes("regras", TRECHOS, 0)
