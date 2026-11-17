"""Divisão do texto de uma página em trechos (MAT-RF-04). Funções puras, sem banco."""

# Um token tem cerca de 4 caracteres; 500 tokens são cerca de 2.000 caracteres (arquitetura.md).
TAMANHO_PADRAO = 2000
SOBREPOSICAO_PADRAO = 200
ESPACOS = (" ", "\n", "\t")


def _ultimo_espaco(texto: str, inicio: int, fim: int) -> int:
    return max(texto.rfind(espaco, inicio, fim) for espaco in ESPACOS)


def _primeiro_espaco(texto: str, inicio: int, fim: int) -> int:
    achados = [i for i in (texto.find(espaco, inicio, fim) for espaco in ESPACOS) if i != -1]
    return min(achados) if achados else -1


def dividir_em_trechos(
    texto: str, tamanho: int = TAMANHO_PADRAO, sobreposicao: int = SOBREPOSICAO_PADRAO
) -> list[tuple[int, int, str]]:
    """Divide o texto em trechos de até `tamanho` caracteres, com `sobreposicao` entre vizinhos.

    Devolve (início, fim, texto) de cada trecho, onde texto == original[início:fim]. A divisão é
    feita entre palavras sempre que possível, para nenhuma frase ser cortada no meio de uma palavra.
    """
    if not texto.strip():
        return []
    if len(texto) <= tamanho:
        return [(0, len(texto), texto)]

    trechos = []
    inicio = 0
    total = len(texto)
    while inicio < total:
        fim = min(inicio + tamanho, total)
        if fim < total:
            corte = _ultimo_espaco(texto, inicio + tamanho // 2, fim)
            if corte != -1:
                fim = corte
        trechos.append((inicio, fim, texto[inicio:fim]))
        if fim >= total:
            break
        proximo = fim - sobreposicao
        espaco = _primeiro_espaco(texto, proximo, fim)
        if espaco != -1:
            proximo = espaco + 1
        inicio = max(proximo, inicio + 1)
    return trechos
