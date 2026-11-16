"""Os PDFs de exemplo usados nos testes do módulo (MAT-T12).

Gerados por código, sem binários no repositório: um PDF com texto, um escaneado (páginas sem texto
selecionável), um misto, um protegido por senha e um com muitas páginas. Os testes abaixo garantem
que cada um é o que diz ser, lendo-os com o pypdf, a mesma biblioteca do processamento.
"""

import io

import pytest
from pypdf import PdfReader

from materiais.testes import pdfs


def ler(conteudo: bytes) -> PdfReader:
    return PdfReader(io.BytesIO(conteudo))


def test_pdf_com_texto_tem_uma_pagina_por_texto_e_o_texto_extraivel():
    leitor = ler(pdfs.pdf_com_texto(["Listas encadeadas", "Pilhas e filas\nsegunda linha"]))

    assert len(leitor.pages) == 2
    assert "Listas encadeadas" in leitor.pages[0].extract_text()
    texto = leitor.pages[1].extract_text()
    assert "Pilhas e filas" in texto and "segunda linha" in texto


def test_o_texto_com_acentos_e_pontuacao_sai_certo():
    texto = r"Árvores binárias (nós) e recursão: 100% \ ok"
    leitor = ler(pdfs.pdf_com_texto([texto]))

    assert texto in leitor.pages[0].extract_text()


def test_pdf_escaneado_tem_paginas_mas_nenhum_texto():
    leitor = ler(pdfs.pdf_escaneado(3))

    assert len(leitor.pages) == 3
    assert all(not pagina.extract_text().strip() for pagina in leitor.pages)


def test_pdf_misto_alterna_paginas_com_e_sem_texto():
    leitor = ler(pdfs.pdf_misto(["Texto da página 1", None, "Texto da página 3", None]))

    textos = [pagina.extract_text().strip() for pagina in leitor.pages]
    assert textos[0] == "Texto da página 1"
    assert textos[1] == "" and textos[3] == ""
    assert textos[2] == "Texto da página 3"


def test_pdf_protegido_pede_senha():
    leitor = ler(pdfs.pdf_protegido(["Conteúdo secreto"], senha="segredo"))

    assert leitor.is_encrypted
    with pytest.raises(Exception, match="(?i)password|senha|decrypt"):
        leitor.pages[0].extract_text()


def test_pdf_grande_tem_o_numero_de_paginas_pedido():
    assert len(ler(pdfs.pdf_com_texto([f"Página {i}" for i in range(1, 302)])).pages) == 301


def test_arquivo_que_nao_e_pdf_nao_e_lido_como_pdf():
    with pytest.raises(Exception):  # noqa: B017 - o tipo exato do erro é da biblioteca
        ler(pdfs.nao_e_pdf()).pages[0]
