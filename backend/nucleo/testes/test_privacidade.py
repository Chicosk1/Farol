"""Filtro de dados pessoais das perguntas (TUT-T90, TUT-RF-11, princípio IV da constituição).

O texto das perguntas passa por aqui antes de ser guardado, exibido ou enviado ao provedor de IA.
Todos os dados abaixo são inventados.
"""

import pytest

from nucleo.privacidade import remover_dados_pessoais, sem_marcas


@pytest.mark.requisito("TUT-RF-11")
@pytest.mark.parametrize(
    "cpf",
    ["123.456.789-09", "12345678909", "123.456.78909", "123 456 789 09"],
)
def test_remove_cpf_com_ou_sem_pontuacao(cpf):
    resultado = remover_dados_pessoais(f"Meu CPF é {cpf}, pode conferir?")

    assert cpf not in resultado
    assert "[CPF]" in resultado


@pytest.mark.requisito("TUT-RF-11")
def test_remove_email():
    resultado = remover_dados_pessoais(
        "Mande para ana.souza@exemplo.edu.br ou ANA@Aluno.Exemplo.com"
    )

    assert "@" not in resultado
    assert resultado.count("[e-mail]") == 2


@pytest.mark.requisito("TUT-RF-11")
@pytest.mark.parametrize(
    "telefone",
    [
        "(11) 91234-5678",
        "11 91234-5678",
        "11912345678",
        "+55 11 91234-5678",
        "(11) 1234-5678",
        "91234-5678",
        "1234-5678",
    ],
)
def test_remove_telefone_brasileiro_em_varios_formatos(telefone):
    resultado = remover_dados_pessoais(f"Me liga em {telefone} depois da aula")

    assert "1234" not in resultado
    assert "[telefone]" in resultado


@pytest.mark.requisito("TUT-RF-11")
def test_remove_registro_academico_quando_vem_identificado():
    resultado = remover_dados_pessoais("Sou o RA 20261234 e tenho uma dúvida; meu ra: 987654")

    assert "20261234" not in resultado and "987654" not in resultado
    assert resultado.count("[RA]") == 2


@pytest.mark.requisito("TUT-RF-11")
def test_remove_o_nome_da_pessoa_sem_diferenciar_acentos_nem_maiusculas():
    resultado = remover_dados_pessoais(
        "Oi, aqui é a ANA souza. Ana pergunta: o que é uma pilha?", nomes=["Ana Souza"]
    )

    assert "ana" not in resultado.lower().replace("pergunta", "")
    assert "souza" not in resultado.lower()
    assert "[nome]" in resultado
    assert "o que é uma pilha?" in resultado


@pytest.mark.requisito("TUT-RF-11")
def test_o_nome_com_acento_e_encontrado_escrito_sem_acento():
    resultado = remover_dados_pessoais("Aqui é o joao antonio", nomes=["João Antônio"])

    assert "joao" not in resultado.lower() and "antonio" not in resultado.lower()


@pytest.mark.requisito("TUT-RF-11")
def test_nome_nao_apaga_pedacos_de_outras_palavras():
    resultado = remover_dados_pessoais("A banana e a manana", nomes=["Ana"])

    assert resultado == "A banana e a manana"


@pytest.mark.requisito("TUT-RF-11")
def test_partes_curtas_do_nome_sao_ignoradas_para_nao_estragar_a_pergunta():
    resultado = remover_dados_pessoais(
        "A lista de Souza e da Silva", nomes=["Ana de Souza da Silva"]
    )

    assert "de" in resultado and "da" in resultado  # preposições ficam
    assert "[nome]" in resultado


@pytest.mark.requisito("TUT-RF-11")
def test_varios_dados_no_mesmo_texto_saem_todos():
    texto = "Sou Ana Souza (RA 123456), cpf 123.456.789-09, ana@exemplo.edu.br, (11) 91234-5678."

    resultado = remover_dados_pessoais(texto, nomes=["Ana Souza"])

    for dado in ("Ana", "Souza", "123456", "123.456.789-09", "@", "91234"):
        assert dado not in resultado


@pytest.mark.requisito("TUT-RF-11")
@pytest.mark.parametrize(
    "texto",
    [
        "O que é uma lista encadeada?",
        "Quantos nós tem uma árvore binária completa de altura 3?",
        "Explique o algoritmo da página 12 da aula 4.",
        "Em 2026 o vetor tem 1000 posições e a busca binária faz log2(1000) passos.",
        "O resultado de 1234 + 5678 é 6912.",
        "int x[3] = {123, 456, 789};",
    ],
)
def test_pergunta_sem_dado_pessoal_nao_muda(texto):
    assert remover_dados_pessoais(texto) == texto


def test_filtrar_de_novo_nao_muda_o_resultado():
    uma_vez = remover_dados_pessoais("cpf 123.456.789-09 e ana@exemplo.edu.br", nomes=["Ana"])

    assert remover_dados_pessoais(uma_vez, nomes=["Ana"]) == uma_vez


def test_sem_nomes_nem_dados_o_texto_vazio_continua_vazio():
    assert remover_dados_pessoais("") == ""
    assert remover_dados_pessoais("   ") == "   "


def test_sem_marcas_tira_as_marcas_dos_dados_removidos_para_a_busca():
    filtrado = remover_dados_pessoais("Sou Ana, cpf 123.456.789-09: o que é pilha?", nomes=["Ana"])

    assert sem_marcas(filtrado) == "Sou , cpf : o que é pilha?"
