"""Filtro de dados pessoais das perguntas (TUT-RF-11, princípio IV da constituição).

Antes de a pergunta ser guardada, exibida ao professor ou enviada ao provedor de IA, o que
identifica o aluno é trocado por uma marca: CPF, e-mail, telefone, registro acadêmico (RA) e o
nome da própria pessoa. O núcleo não depende de nenhum módulo: quem chama passa os nomes.

O filtro é uma proteção em camadas, e não uma garantia: ele não adivinha nomes de terceiros. Por
isso o prompt enviado ao provedor também nunca leva nome, RA, e-mail nem turma do aluno.
"""

import re
import unicodedata
from collections.abc import Iterable

TAMANHO_MINIMO_DE_UM_NOME = 3  # "de", "da" e "do" não identificam ninguém e estragariam a pergunta

_CPF = re.compile(r"(?<!\d)\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}(?!\d)")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_RA = re.compile(r"\bra\b[\s:.-]*\d{5,}", re.IGNORECASE)
# Telefone brasileiro: com +55 e/ou DDD, ou o número de 8 ou 9 dígitos com hífen. Número solto sem
# DDD nem hífen não vale como telefone, para não apagar contas e valores da pergunta.
_TELEFONE = re.compile(
    r"(?<![\w-])(?:\+?55[\s-]?)?(?:\(\d{2}\)|\b\d{2})[\s-]?9?\d{4}[\s-]?\d{4}(?![\w-])"
    r"|(?<![\w-])9?\d{4}-\d{4}(?![\w-])"
)


def _sem_acentos(texto: str) -> str:
    """O texto sem acentos, com o mesmo comprimento (cada letra vira uma letra)."""
    return "".join(
        unicodedata.normalize("NFKD", letra)[0] if unicodedata.category(letra)[0] == "L" else letra
        for letra in texto
    )


def _remover_nomes(texto: str, nomes: Iterable[str]) -> str:
    partes = {
        _sem_acentos(parte).lower()
        for nome in nomes
        for parte in re.findall(r"\w+", nome)
        if len(parte) >= TAMANHO_MINIMO_DE_UM_NOME
    }
    if not partes:
        return texto
    padrao = re.compile(r"\b(?:" + "|".join(map(re.escape, sorted(partes))) + r")\b", re.IGNORECASE)
    comparavel = _sem_acentos(texto)  # mesmas posições do texto original
    resultado = []
    fim_anterior = 0
    for achado in padrao.finditer(comparavel):
        resultado.append(texto[fim_anterior : achado.start()])
        resultado.append("[nome]")
        fim_anterior = achado.end()
    resultado.append(texto[fim_anterior:])
    return "".join(resultado)


def remover_dados_pessoais(texto: str, nomes: Iterable[str] = ()) -> str:
    """Troca por marcas o CPF, o e-mail, o telefone, o RA e os nomes informados."""
    texto = _EMAIL.sub("[e-mail]", texto)
    texto = _RA.sub("[RA]", texto)
    # O telefone vem antes: DDD + celular (11 dígitos seguidos) também parece um CPF sem pontuação.
    texto = _TELEFONE.sub("[telefone]", texto)
    texto = _CPF.sub("[CPF]", texto)
    return _remover_nomes(texto, nomes)


_MARCAS = re.compile(r"\[(?:CPF|e-mail|telefone|RA|nome)\]")


def sem_marcas(texto: str) -> str:
    """O texto filtrado sem as marcas dos dados removidos, que só atrapalhariam a busca."""
    return re.sub(r"\s{2,}", " ", _MARCAS.sub(" ", texto)).strip()
