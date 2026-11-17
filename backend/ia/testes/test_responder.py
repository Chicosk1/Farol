"""ia.responder: a resposta em streaming com regras, trechos numerados e a pergunta (TUT-T10).

Os testes usam o provedor falso, que monta a resposta só com o texto dos trechos recebidos, sem
internet e sem custo. Dados fictícios.
"""

import re

import pytest

from ia import servicos
from ia.porta import EventoFim, EventoTexto, TrechoNumerado

LISTA = TrechoNumerado(
    1,
    "Uma lista encadeada é formada por nós. Cada nó guarda um valor e um ponteiro para o próximo.",
)
PILHA = TrechoNumerado(
    2, "Uma pilha segue a ordem LIFO: o último elemento a entrar é o primeiro a sair."
)
BANCO = TrechoNumerado(3, "A chave primária identifica cada linha de uma tabela relacional.")


def resposta(regras: str, trechos: list[TrechoNumerado], pergunta: str) -> tuple[str, EventoFim]:
    eventos = list(servicos.responder(regras, trechos, pergunta))
    texto = "".join(e.texto for e in eventos if isinstance(e, EventoTexto))
    fim = eventos[-1]
    assert isinstance(fim, EventoFim)
    return texto, fim


def test_a_resposta_vem_em_pedacos_e_termina_com_o_evento_de_fim():
    eventos = list(servicos.responder("Regras.", [LISTA], "O que é uma lista encadeada?"))

    assert len([e for e in eventos if isinstance(e, EventoTexto)]) > 1  # streaming de verdade
    assert isinstance(eventos[-1], EventoFim)
    assert all(isinstance(e, EventoTexto) for e in eventos[:-1])


def test_a_resposta_cita_o_numero_do_trecho_que_responde_a_pergunta():
    texto, _ = resposta("Regras.", [LISTA, PILHA, BANCO], "O que é uma lista encadeada?")

    assert "[1]" in texto
    assert "[2]" not in texto and "[3]" not in texto


def test_pergunta_que_toca_em_dois_trechos_cita_os_dois():
    texto, _ = resposta("Regras.", [LISTA, PILHA, BANCO], "Compare lista encadeada e pilha")

    assert "[1]" in texto and "[2]" in texto


def test_a_resposta_usa_so_o_que_esta_nos_trechos_recebidos():
    texto, _ = resposta("Regras.", [LISTA, PILHA], "O que é uma pilha?")

    frases = [f.strip() for f in re.split(r"\s*\[\d+\]\s*", texto) if f.strip()]
    trechos = LISTA.texto + " " + PILHA.texto
    assert frases and all(frase in trechos for frase in frases)


def test_o_fim_traz_a_contagem_de_tokens_para_o_custo():
    _, fim = resposta("Regras fixas do servidor.", [LISTA], "O que é uma lista encadeada?")

    assert fim.tokens_entrada > 0 and fim.tokens_saida > 0


def test_com_o_modo_pistas_nas_regras_e_pedido_de_exercicio_responde_com_pista_e_citacao():
    regras = "Você é o tutor. MODO PISTAS: não entregue o resultado de exercícios."

    texto, _ = resposta(regras, [PILHA], "Me dá a resposta do exercício de pilha")

    assert texto.startswith("[PISTAS] Vamos por etapas")  # a marca que o servidor reconhece
    assert "[2]" in texto
    assert "LIFO" not in texto  # a pista não entrega o conteúdo pronto


def test_com_modo_pistas_uma_pergunta_conceitual_continua_sendo_respondida_normalmente():
    regras = "Você é o tutor. MODO PISTAS: não entregue o resultado de exercícios."

    texto, _ = resposta(regras, [PILHA], "O que é uma pilha?")

    assert "LIFO" in texto and "[PISTAS]" not in texto


def test_sem_modo_pistas_o_pedido_de_exercicio_e_respondido_com_o_conteudo():
    texto, _ = resposta("Você é o tutor.", [PILHA], "Me dá a resposta do exercício de pilha")

    assert "LIFO" in texto


def test_a_mesma_entrada_gera_sempre_a_mesma_resposta():
    argumentos = ("Regras.", [LISTA, PILHA], "Compare lista encadeada e pilha")

    assert resposta(*argumentos) == resposta(*argumentos)


def test_sem_trechos_o_modelo_nao_deve_ser_chamado():
    with pytest.raises(ValueError, match="trechos"):
        list(servicos.responder("Regras.", [], "Qualquer coisa"))


def test_pergunta_vazia_e_recusada():
    with pytest.raises(ValueError, match="pergunta"):
        list(servicos.responder("Regras.", [LISTA], "  "))
