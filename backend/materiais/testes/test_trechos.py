"""Divisão do texto de uma página em trechos de cerca de 500 tokens, com sobreposição (MAT-T22)."""

import pytest

from materiais.trechos import dividir_em_trechos


def palavras(n: int) -> str:
    return " ".join(f"palavra{i}" for i in range(n))


def test_texto_curto_vira_um_so_trecho_com_a_posicao_inteira():
    assert dividir_em_trechos("Uma lista encadeada.") == [(0, 20, "Uma lista encadeada.")]


def test_texto_vazio_ou_so_com_espacos_nao_gera_trechos():
    assert dividir_em_trechos("") == []
    assert dividir_em_trechos("  \n ") == []


@pytest.mark.requisito("MAT-RF-04")
def test_cada_trecho_e_exatamente_o_pedaco_do_texto_entre_inicio_e_fim():
    texto = palavras(900)

    trechos = dividir_em_trechos(texto, tamanho=500, sobreposicao=60)

    assert len(trechos) > 1
    for inicio, fim, pedaco in trechos:
        assert texto[inicio:fim] == pedaco


def test_os_trechos_respeitam_o_tamanho_e_cobrem_o_texto_do_comeco_ao_fim():
    texto = palavras(900)

    trechos = dividir_em_trechos(texto, tamanho=500, sobreposicao=60)

    assert all(len(pedaco) <= 500 for _, _, pedaco in trechos)
    assert trechos[0][0] == 0
    assert trechos[-1][1] == len(texto)


def test_trechos_vizinhos_se_sobrepoem_para_nao_perder_o_contexto_da_divisa():
    trechos = dividir_em_trechos(palavras(900), tamanho=500, sobreposicao=60)

    for (_, fim_anterior, _), (inicio_seguinte, _, _) in zip(trechos, trechos[1:], strict=False):
        assert inicio_seguinte < fim_anterior  # há sobreposição
        assert fim_anterior - inicio_seguinte <= 60 + 20  # e ela é pequena


def test_a_divisao_acontece_entre_palavras_e_nao_no_meio_delas():
    texto = palavras(900)

    for inicio, fim, _ in dividir_em_trechos(texto, tamanho=500, sobreposicao=60):
        assert inicio == 0 or texto[inicio - 1] == " "
        assert fim == len(texto) or texto[fim] == " "


def test_palavra_gigante_sem_espacos_ainda_e_dividida_sem_travar():
    trechos = dividir_em_trechos("x" * 1300, tamanho=500, sobreposicao=50)

    assert trechos[-1][1] == 1300
    assert all(len(pedaco) <= 500 for _, _, pedaco in trechos)


def test_o_tamanho_padrao_equivale_a_cerca_de_500_tokens():
    texto = palavras(1000)  # cerca de 9.000 caracteres

    trechos = dividir_em_trechos(texto)

    assert 3 <= len(trechos) <= 7
    assert max(len(pedaco) for _, _, pedaco in trechos) <= 2000
