"""Gerador de PDFs de exemplo para os testes (sem binários no repositório). Dados fictícios.

O PDF com texto vem do núcleo (nucleo/pdf_de_texto.py), que a avaliação do tutor também usa.
"""

import io

from pypdf import PdfReader, PdfWriter

from nucleo.pdf_de_texto import montar_pdf, pdf_com_texto

__all__ = ["nao_e_pdf", "pdf_com_texto", "pdf_escaneado", "pdf_misto", "pdf_protegido"]


def pdf_escaneado(quantidade_de_paginas: int) -> bytes:
    """Um PDF só de imagens, como um livro escaneado: tem páginas, mas nenhum texto."""
    return montar_pdf([None] * quantidade_de_paginas)


def pdf_misto(paginas: list[str | None]) -> bytes:
    """Um PDF em que `None` marca uma página sem texto."""
    return montar_pdf(list(paginas))


def pdf_protegido(paginas: list[str], senha: str = "segredo") -> bytes:
    """Um PDF que exige senha para abrir."""
    escritor = PdfWriter(clone_from=PdfReader(io.BytesIO(montar_pdf(list(paginas)))))
    escritor.encrypt(senha, algorithm="RC4-128")
    saida = io.BytesIO()
    escritor.write(saida)
    return saida.getvalue()


def nao_e_pdf() -> bytes:
    """Um arquivo qualquer, com cara de planilha, para testar a recusa de formatos."""
    return b"ra,nome\n1,Ana\n"
