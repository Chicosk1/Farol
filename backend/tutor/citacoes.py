"""Conversão das marcações de trecho em citações (TUT-RF-02 e TUT-RF-03). Sem banco.

O modelo marca cada afirmação com o número do trecho em que ela se apoia, como [2]. Aqui, a
resposta que chega em pedaços (streaming) é separada em frases; só passam as frases com pelo menos
uma marcação válida, e as marcações são renumeradas na ordem em que as citações aparecem.

Com os textos dos trechos, cada frase também passa pela conferência da citação (plan.md): modelos
pequenos às vezes escrevem a frase de um trecho e marcam o número de outro. Se a frase claramente
vem de outro trecho enviado, a citação passa para ele.
"""

import re
import unicodedata

MARCACAO = re.compile(r"\[(\d+)\]")
# Fim de frase: pontuação final, as marcações que vierem logo depois, e o começo da próxima frase.
FRONTEIRA = re.compile(r"[.!?](?:\s*\[\d+\])*(?=\s+[^\s\[])")

# Conferência da citação: só troca quando não há dúvida.
PALAVRAS_MINIMAS = 3  # frase curta demais não diz de onde veio
PARTE_MINIMA_NO_TRECHO = 0.6  # das palavras da frase, quantas estão no trecho de onde ela veio
VANTAGEM_MINIMA = 0.3  # quanto a mais que no trecho que o modelo citou
TAMANHO_DO_RADICAL = 5  # "balanceada" e "balanceados" contam como a mesma palavra


def _radicais(texto: str) -> set[str]:
    """As palavras que dizem do que o texto trata, sem acento e reduzidas ao começo."""
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return {p[:TAMANHO_DO_RADICAL] for p in re.findall(r"[a-z0-9]+", sem_acentos) if len(p) >= 4}


class ConversorDeCitacoes:
    def __init__(self, trechos_validos: set[int], textos: dict[int, str] | None = None):
        self._validos = trechos_validos
        self._radicais = {
            n: _radicais(t) for n, t in (textos or {}).items() if n in trechos_validos
        }
        self._pendente = ""
        self._ordem: dict[int, int] = {}  # número do trecho no prompt -> número da citação

    @property
    def citados(self) -> list[int]:
        """Os números dos trechos citados, na ordem das citações."""
        return list(self._ordem)

    def receber(self, pedaco: str) -> list[str]:
        """Recebe um pedaço da resposta e devolve as frases completas que podem ser mostradas."""
        self._pendente += pedaco
        frases = []
        inicio = 0
        for fronteira in FRONTEIRA.finditer(self._pendente):
            frases.append(self._pendente[inicio : fronteira.end()])
            inicio = fronteira.end()
        self._pendente = self._pendente[inicio:]
        return [convertida for frase in frases if (convertida := self._converter(frase))]

    def terminar(self) -> list[str]:
        """Devolve a última frase, se ela puder ser mostrada."""
        frase, self._pendente = self._pendente, ""
        convertida = self._converter(frase)
        return [convertida] if convertida else []

    def _conferir(self, frase: str, numeros: list[int]) -> dict[int, int]:
        """As trocas de citação da frase: número que o modelo marcou -> trecho de onde ela veio."""
        palavras = _radicais(MARCACAO.sub(" ", frase))
        if not self._radicais or len(palavras) < PALAVRAS_MINIMAS:
            return {}

        def parte(numero: int) -> float:
            return len(palavras & self._radicais[numero]) / len(palavras)

        melhor = max(self._radicais, key=parte)
        if melhor in numeros or parte(melhor) < PARTE_MINIMA_NO_TRECHO:
            return {}
        return {
            numero: melhor for numero in numeros if parte(melhor) - parte(numero) >= VANTAGEM_MINIMA
        }

    def _converter(self, frase: str) -> str | None:
        numeros = [int(n) for n in MARCACAO.findall(frase) if int(n) in self._validos]
        if not numeros:
            return None  # afirmação sem citação não é apresentada (TUT-RF-03)
        trocas = self._conferir(frase, numeros)
        for numero in numeros:
            self._ordem.setdefault(trocas.get(numero, numero), len(self._ordem) + 1)

        def renumerar(marcacao: re.Match) -> str:
            numero = int(marcacao.group(1))
            if numero not in self._validos:
                return ""
            return f"[{self._ordem[trocas.get(numero, numero)]}]"

        return re.sub(r"\s{2,}", " ", MARCACAO.sub(renumerar, frase)).strip()
