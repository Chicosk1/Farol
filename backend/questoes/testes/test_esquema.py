"""Validação das questões que o modelo devolve (QUE-T11). Dados fictícios."""

import json

import pytest

from ia import servicos as ia
from ia.porta import TrechoNumerado
from questoes.esquema import ler_questoes


def valida(**campos) -> dict:
    return {
        "enunciado": "Qual regra a pilha segue?",
        "alternativas": ["LIFO", "FIFO", "Por prioridade", "Aleatória"],
        "correta": 0,
        "justificativa": "Na pilha, o último a entrar é o primeiro a sair.",
        "topico": "Pilhas",
        "trecho": 1,
    } | campos


def ler(*questoes, trechos=frozenset({1, 2}), limite=10):
    return ler_questoes(json.dumps({"questoes": list(questoes)}), set(trechos), limite)


@pytest.mark.requisito("QUE-RF-02")
def test_questao_no_formato_e_aceita():
    leitura = ler(valida())

    assert leitura.descartadas == 0
    [questao] = leitura.aceitas
    assert questao.alternativas[questao.correta] == "LIFO"
    assert questao.trecho == 1


@pytest.mark.requisito("QUE-RF-03")
def test_questao_citando_trecho_que_nao_foi_enviado_e_descartada():
    leitura = ler(valida(trecho=9), valida())

    assert (len(leitura.aceitas), leitura.descartadas) == (1, 1)


@pytest.mark.requisito("QUE-RF-03")
@pytest.mark.parametrize(
    "defeito",
    [
        {"alternativas": ["LIFO", "FIFO", "Aleatória"]},
        {"alternativas": ["LIFO", "FIFO", "Aleatória", "Por prioridade", "Outra"]},
        {"alternativas": ["LIFO", "lifo", "FIFO", "Aleatória"]},
        {"correta": 4},
        {"correta": -1},
        {"enunciado": "   "},
        {"justificativa": ""},
        {"trecho": None},
        {"topico": "x"},
    ],
    ids=[
        "3-alternativas",
        "5-alternativas",
        "repetidas",
        "gabarito-4",
        "gabarito-negativo",
        "sem-enunciado",
        "sem-justificativa",
        "sem-trecho",
        "topico-curto",
    ],
)
def test_questao_fora_do_formato_e_descartada_e_as_outras_seguem(defeito):
    leitura = ler(valida(**defeito), valida())

    assert (len(leitura.aceitas), leitura.descartadas) == (1, 1)


def test_questao_sem_um_campo_e_descartada():
    sem_gabarito = valida()
    del sem_gabarito["correta"]

    assert ler(sem_gabarito).descartadas == 1


@pytest.mark.requisito("QUE-RF-03")
@pytest.mark.parametrize("texto", ["não é JSON", '{"outra": 1}', '"texto"', ""])
def test_resposta_ilegivel_descarta_o_pedido_inteiro(texto):
    leitura = ler_questoes(texto, {1}, 5)

    assert (leitura.aceitas, leitura.descartadas) == ([], 5)


def test_json_cercado_por_marcacao_de_codigo_e_aceito():
    texto = "```json\n" + json.dumps({"questoes": [valida()]}) + "\n```"

    assert len(ler_questoes(texto, {1}, 5).aceitas) == 1


def test_lista_sem_o_objeto_em_volta_tambem_e_aceita():
    assert len(ler_questoes(json.dumps([valida()]), {1}, 5).aceitas) == 1


def test_questoes_alem_do_limite_sao_ignoradas():
    leitura = ler(*[valida() for _ in range(7)], limite=5)

    assert (len(leitura.aceitas), leitura.descartadas) == (5, 0)


def test_espacos_em_volta_dos_textos_sao_tirados():
    [questao] = ler(valida(enunciado="  Qual regra a pilha segue?  ")).aceitas

    assert questao.enunciado == "Qual regra a pilha segue?"


def test_as_questoes_do_provedor_falso_passam_na_validacao():
    trechos = [
        TrechoNumerado(1, "Uma pilha segue a ordem LIFO. O último a entrar é o primeiro a sair."),
        TrechoNumerado(2, "Uma fila segue a ordem FIFO. O primeiro a entrar é o primeiro a sair."),
    ]

    leitura = ler_questoes(ia.gerar_questoes("regras", trechos, 10), {1, 2}, 10)

    assert (len(leitura.aceitas), leitura.descartadas) == (10, 0)
