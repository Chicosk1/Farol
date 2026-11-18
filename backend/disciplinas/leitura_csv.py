"""Leitura e validação do CSV de turmas e matrículas (ACE-RF-06). Não toca no banco.

Formato (UTF-8, separador vírgula, uma linha por aluno e disciplina):
    ra,nome,email,codigo_disciplina,nome_disciplina,turma,semestre,email_professor

Dois tipos de problema, tratados de formas diferentes:
- do arquivo inteiro (coluna faltando, codificação, separador, vazio): `ArquivoRecusado`, e nada
  é importado, para nunca ficar pela metade;
- de uma linha (e-mail inválido, campo vazio, repetição): a linha é rejeitada com o motivo, e as
  outras valem.
"""

import csv
import io
import re
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

COLUNAS = (
    "ra",
    "nome",
    "email",
    "codigo_disciplina",
    "nome_disciplina",
    "turma",
    "semestre",
    "email_professor",
)
SEMESTRE = re.compile(r"^\d{4}/\d$")
LIMITE_DE_BYTES = 5 * 1024 * 1024


class ArquivoRecusado(ValueError):
    """O arquivo, como um todo, não pode ser importado. A mensagem explica o que corrigir."""


@dataclass(frozen=True)
class Linha:
    numero: int  # número da linha no arquivo, contando o cabeçalho como linha 1
    ra: str
    nome: str
    email: str
    codigo: str
    nome_disciplina: str
    turma: str
    semestre: str
    email_professor: str

    @property
    def disciplina(self) -> tuple[str, str, str]:
        return (self.codigo, self.turma, self.semestre)


def ler(conteudo: bytes) -> list[tuple[int, dict]]:
    """Decodifica o CSV e devolve (número da linha, campos) de cada linha de dados.

    Levanta ArquivoRecusado para os problemas do arquivo inteiro.
    """
    if len(conteudo) > LIMITE_DE_BYTES:
        raise ArquivoRecusado("O arquivo passa de 5 MB. Divida a planilha em arquivos menores.")
    try:
        texto = conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ArquivoRecusado(
            "O arquivo não está em UTF-8. Salve a planilha como CSV UTF-8 e envie de novo."
        ) from None
    if not texto.strip():
        raise ArquivoRecusado("O arquivo está vazio.")

    primeira = texto.lstrip().splitlines()[0]
    if ";" in primeira and "," not in primeira:
        raise ArquivoRecusado(
            "O separador do arquivo é ponto e vírgula. Use vírgula como separador."
        )

    leitor = csv.reader(io.StringIO(texto))
    cabecalho = [coluna.strip().lower() for coluna in next(leitor)]
    faltando = [coluna for coluna in COLUNAS if coluna not in cabecalho]
    if faltando:
        raise ArquivoRecusado(f"Faltam colunas no cabeçalho: {', '.join(faltando)}.")

    linhas = []
    for linha in leitor:
        numero = leitor.line_num
        if not any(campo.strip() for campo in linha):
            continue  # linha em branco
        campos = {
            coluna: (linha[i].strip() if i < len(linha) else "")
            for i, coluna in enumerate(cabecalho)
        }
        campos["_colunas_a_mais"] = len(linha) > len(cabecalho)
        linhas.append((numero, campos))
    if not linhas:
        raise ArquivoRecusado("O arquivo não tem linhas de dados, só o cabeçalho.")
    return linhas


def _email_valido(email: str) -> bool:
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True


def validar(linhas: list[tuple[int, dict]]) -> tuple[list[Linha], list[dict]]:
    """Separa as linhas aceitas das rejeitadas, cada rejeitada com a linha e o motivo."""
    aceitas: list[Linha] = []
    rejeitadas: list[dict] = []
    vistas: dict[tuple[str, tuple], int] = {}
    professores: dict[tuple, tuple[str, int]] = {}

    def rejeitar(numero: int, motivo: str) -> None:
        rejeitadas.append({"linha": numero, "motivo": motivo})

    for numero, campos in linhas:
        vazios = [coluna for coluna in COLUNAS if not campos[coluna]]
        if campos["_colunas_a_mais"]:
            rejeitar(numero, "A linha tem mais colunas que o cabeçalho.")
            continue
        if vazios:
            rejeitar(numero, f"Campo obrigatório vazio: {', '.join(vazios)}.")
            continue
        if not _email_valido(campos["email"]):
            rejeitar(numero, "O e-mail do aluno é inválido.")
            continue
        if not _email_valido(campos["email_professor"]):
            rejeitar(numero, "O e-mail do professor é inválido.")
            continue
        if not SEMESTRE.match(campos["semestre"]):
            rejeitar(numero, "O semestre deve ter o formato AAAA/N, por exemplo 2026/2.")
            continue

        linha = Linha(
            numero=numero,
            ra=campos["ra"],
            nome=campos["nome"],
            email=campos["email"].lower(),
            codigo=campos["codigo_disciplina"],
            nome_disciplina=campos["nome_disciplina"],
            turma=campos["turma"],
            semestre=campos["semestre"],
            email_professor=campos["email_professor"].lower(),
        )
        chave_do_aluno = (linha.email, linha.disciplina)
        if chave_do_aluno in vistas:
            rejeitar(
                numero,
                "Linha repetida: o aluno já aparece nesta disciplina na linha "
                f"{vistas[chave_do_aluno]}.",
            )
            continue
        anterior = professores.get(linha.disciplina)
        if anterior and anterior[0] != linha.email_professor:
            rejeitar(
                numero,
                f"Outro professor para a mesma disciplina (a linha {anterior[1]} "
                f"indica {anterior[0]}).",
            )
            continue

        vistas[chave_do_aluno] = numero
        professores.setdefault(linha.disciplina, (linha.email_professor, numero))
        aceitas.append(linha)
    return aceitas, rejeitadas
