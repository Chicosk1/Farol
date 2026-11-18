"""Conversão das marcações de trecho em citações, descartando frases sem marcação (TUT-T22).

O modelo marca cada afirmação com o número do trecho, como [2]. O servidor só deixa passar as
frases marcadas (TUT-RF-03) e renumera as citações na ordem em que aparecem.
"""

import pytest

from tutor.citacoes import ConversorDeCitacoes


def converter(texto: str, validos=(1, 2, 3), pedacos: int | None = None) -> tuple[str, list[int]]:
    conversor = ConversorDeCitacoes(set(validos))
    frases: list[str] = []
    if pedacos:
        for i in range(0, len(texto), pedacos):
            frases += conversor.receber(texto[i : i + pedacos])
    else:
        frases += conversor.receber(texto)
    frases += conversor.terminar()
    return " ".join(frases), conversor.citados


@pytest.mark.requisito("TUT-RF-03")
def test_frase_sem_marcacao_e_descartada_e_a_marcada_passa():
    texto, citados = converter("Uma pilha é LIFO. [1] Isso cai na prova com certeza. Fim. [2]")

    assert texto == "Uma pilha é LIFO. [1] Fim. [2]"
    assert citados == [1, 2]


@pytest.mark.requisito("TUT-RF-02")
def test_as_citacoes_sao_renumeradas_na_ordem_em_que_aparecem():
    texto, citados = converter("Primeiro fato. [3] Segundo fato. [1] De novo o primeiro. [3]")

    assert texto == "Primeiro fato. [1] Segundo fato. [2] De novo o primeiro. [1]"
    assert citados == [3, 1]


@pytest.mark.requisito("TUT-RF-03")
def test_marcacao_de_trecho_que_nao_foi_enviado_nao_vale_como_citacao():
    texto, citados = converter("Fato inventado. [9] Fato do material. [2]")

    assert texto == "Fato do material. [1]"
    assert citados == [2]


def test_a_marcacao_pode_vir_antes_do_ponto():
    texto, _ = converter("Uma fila é FIFO [2]. Outra frase sem fonte.")

    assert texto == "Uma fila é FIFO [1]."


def test_uma_frase_com_duas_marcacoes_cita_os_dois_trechos():
    texto, citados = converter("Lista e pilha guardam elementos. [1][2]")

    assert texto == "Lista e pilha guardam elementos. [1][2]"
    assert citados == [1, 2]


@pytest.mark.requisito("TUT-RF-13")
@pytest.mark.parametrize("tamanho", [1, 3, 7])
def test_em_streaming_o_resultado_e_o_mesmo_de_receber_tudo_de_uma_vez(tamanho):
    resposta = "Uma pilha é LIFO. [1] Sem fonte aqui. Uma fila é FIFO. [2] Fim sem fonte."

    assert converter(resposta, pedacos=tamanho) == converter(resposta)


@pytest.mark.requisito("TUT-RF-13")
def test_a_frase_marcada_sai_assim_que_a_seguinte_comeca_sem_esperar_o_fim():
    conversor = ConversorDeCitacoes({1, 2})

    assert conversor.receber("Uma pilha é LIFO. [1]") == []  # ainda pode vir outra marcação
    assert conversor.receber(" Uma fila") == ["Uma pilha é LIFO. [1]"]


@pytest.mark.requisito("TUT-RF-03")
def test_sem_nenhuma_frase_marcada_nada_e_apresentado():
    texto, citados = converter("Acho que cai na prova. Estude bastante!")

    assert (texto, citados) == ("", [])


# Conferência da citação (TUT-T19): a frase que claramente vem de outro trecho passa a citá-lo.
TRECHOS = {
    1: "A busca binária só funciona em vetores ordenados. Ela compara o valor procurado com o "
    "elemento do meio.",
    2: "Para verificar se os parênteses de uma expressão estão balanceados, empilha-se cada "
    "abertura e desempilha-se a cada fechamento; a expressão está balanceada se a pilha terminar "
    "vazia.",
    3: "Uma fila segue a política FIFO.",
}


def conferir(texto: str, pedacos: int | None = None) -> tuple[str, list[int]]:
    conversor = ConversorDeCitacoes(set(TRECHOS), TRECHOS)
    frases: list[str] = []
    passo = pedacos or len(texto)
    for i in range(0, len(texto), passo):
        frases += conversor.receber(texto[i : i + passo])
    frases += conversor.terminar()
    return " ".join(frases), conversor.citados


@pytest.mark.requisito("TUT-RF-02")
def test_frase_que_claramente_vem_de_outro_trecho_passa_a_cita_lo():
    texto, citados = conferir(
        "Empilha-se cada abertura e desempilha-se a cada fechamento; a expressão está "
        "balanceada se a pilha terminar vazia. [1]"
    )

    assert citados == [2]
    assert texto.endswith("vazia. [1]")  # a citação é renumerada como sempre


def test_a_conferencia_vale_tambem_com_a_resposta_em_pedacos():
    _, citados = conferir(
        "A busca binária só funciona em vetores ordenados. [1] Empilha-se cada abertura e "
        "desempilha-se a cada fechamento, até a pilha terminar vazia. [3]",
        pedacos=7,
    )

    assert citados == [1, 2]


def test_citacao_certa_nao_muda():
    _, citados = conferir("A busca binária só funciona em vetores ordenados. [1]")

    assert citados == [1]


def test_frase_curta_fica_com_a_citacao_do_modelo():
    _, citados = conferir("Isso vale sempre. [3]")

    assert citados == [3]


def test_frase_que_nao_vem_de_nenhum_trecho_fica_com_a_citacao_do_modelo():
    _, citados = conferir("O quicksort escolhe um pivô e particiona o vetor recursivamente. [1]")

    assert citados == [1]


def test_frase_que_ja_cita_o_trecho_certo_junto_com_outro_nao_muda():
    _, citados = conferir(
        "Empilha-se cada abertura e desempilha-se a cada fechamento, até a pilha terminar "
        "vazia. [1][2]"
    )

    assert citados == [1, 2]


def test_sem_os_textos_dos_trechos_nao_ha_conferencia():
    texto, citados = converter(
        "Empilha-se cada abertura e desempilha-se a cada fechamento, até a pilha terminar "
        "vazia. [1]"
    )

    assert citados == [1]
