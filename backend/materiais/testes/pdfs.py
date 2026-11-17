"""Gerador de PDFs de exemplo para os testes (sem binários no repositório). Dados fictícios."""

import io

from pypdf import PdfReader, PdfWriter


def _escapar(linha: str) -> bytes:
    """Uma linha como string literal de PDF (WinAnsi, com parênteses e barras escapados)."""
    bruto = linha.encode("cp1252")
    for original, escapado in ((b"\\", rb"\\"), (b"(", rb"\("), (b")", rb"\)")):
        bruto = bruto.replace(original, escapado)
    return bruto


def _fluxo_da_pagina(texto: str | None) -> bytes:
    if texto is None:
        # Uma página "escaneada": só um desenho, sem nenhum texto selecionável.
        return b"0.8 g 72 72 451 698 re f"
    partes = []
    for i, linha in enumerate(texto.split("\n")):
        partes.append(
            b"BT /F1 12 Tf 72 "
            + str(770 - 18 * i).encode()
            + b" Td ("
            + _escapar(linha)
            + b") Tj ET"
        )
    return b"\n".join(partes)


def _montar(paginas: list[str | None]) -> bytes:
    n = len(paginas)
    primeiro_id = 4
    ids_das_paginas = [primeiro_id + 2 * i for i in range(n)]
    kids = " ".join(f"{i} 0 R" for i in ids_das_paginas)
    objetos: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    for i, texto in enumerate(paginas):
        id_conteudo = ids_das_paginas[i] + 1
        objetos.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 3 0 R >> >> /Contents " + f"{id_conteudo} 0 R >>".encode()
        )
        fluxo = _fluxo_da_pagina(texto)
        objetos.append(f"<< /Length {len(fluxo)} >>\nstream\n".encode() + fluxo + b"\nendstream")

    saida = io.BytesIO()
    saida.write(b"%PDF-1.4\n")
    posicoes = []
    for numero, corpo in enumerate(objetos, start=1):
        posicoes.append(saida.tell())
        saida.write(f"{numero} 0 obj\n".encode() + corpo + b"\nendobj\n")
    inicio_da_tabela = saida.tell()
    saida.write(f"xref\n0 {len(objetos) + 1}\n".encode() + b"0000000000 65535 f \n")
    for posicao in posicoes:
        saida.write(f"{posicao:010d} 00000 n \n".encode())
    saida.write(
        f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\n"
        f"startxref\n{inicio_da_tabela}\n%%EOF\n".encode()
    )
    return saida.getvalue()


def pdf_com_texto(paginas: list[str]) -> bytes:
    """Um PDF com uma página por texto (linhas separadas por quebra de linha), selecionável."""
    return _montar(list(paginas))


def pdf_escaneado(quantidade_de_paginas: int) -> bytes:
    """Um PDF só de imagens, como um livro escaneado: tem páginas, mas nenhum texto."""
    return _montar([None] * quantidade_de_paginas)


def pdf_misto(paginas: list[str | None]) -> bytes:
    """Um PDF em que `None` marca uma página sem texto."""
    return _montar(list(paginas))


def pdf_protegido(paginas: list[str], senha: str = "segredo") -> bytes:
    """Um PDF que exige senha para abrir."""
    escritor = PdfWriter(clone_from=PdfReader(io.BytesIO(_montar(list(paginas)))))
    escritor.encrypt(senha, algorithm="RC4-128")
    saida = io.BytesIO()
    escritor.write(saida)
    return saida.getvalue()


def nao_e_pdf() -> bytes:
    """Um arquivo qualquer, com cara de planilha, para testar a recusa de formatos."""
    return b"ra,nome\n1,Ana\n"
