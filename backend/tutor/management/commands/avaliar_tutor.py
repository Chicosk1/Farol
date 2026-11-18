"""Avalia o tutor com o conjunto de perguntas e diz se as metas foram atingidas (TUT-T13).

Uso: python manage.py avaliar_tutor [--conjunto estruturas_de_dados] [--limite N] [--detalhes]
                                    [--so-relatorio]

Roda com o provedor de IA configurado: com o falso, confere o caminho; com o Ollama ou outro
provedor real, mede a qualidade (TUT-CS-01, 03 e 04). Cria uma disciplina com o material do
conjunto, faz as perguntas como um aluno e desfaz tudo no fim, inclusive os arquivos.
Termina com erro quando alguma meta não é atingida, a menos que se peça só o relatório.
"""

import shutil
import tempfile
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.test.utils import override_settings

from contas import servicos as contas
from disciplinas import servicos as disciplinas
from materiais import servicos as materiais
from nucleo.pdf_de_texto import pdf_com_texto
from tutor.avaliacao import CONJUNTO_PADRAO, Conjunto, carregar
from tutor.avaliacao.avaliar import (
    META_DE_CITACAO,
    META_DE_NAO_ENCONTREI,
    Relatorio,
    Resultado,
    avaliar,
)


class _Desfazer(Exception):
    """Desfaz tudo o que a avaliação criou no banco."""


def _por_cento(valor: float) -> str:
    return f"{valor * 100:.1f}%".replace(".", ",")


def _situacao(atingida: bool) -> str:
    return "atingida" if atingida else "NÃO ATINGIDA"


def _preparar_disciplina(conjunto: Conjunto) -> int:
    """A disciplina de avaliação, com o material de cada aula processado e pronto."""
    professor, _ = contas.garantir_pessoa_com_perfil(
        "avaliacao@exemplo.edu.br", contas.Perfil.PROFESSOR, nome="Avaliação do tutor"
    )
    disciplina, _ = disciplinas.garantir_disciplina(
        "AVALIACAO", conjunto.disciplina, "AVALIACAO", "0000/0", professor
    )
    for aula in conjunto.aulas:
        material = materiais.criar_material(
            disciplina.id,
            pdf_com_texto(aula.paginas),
            f"aula-{aula.numero}.pdf",
            aula.numero,
            aula.titulo,
            professor,
        )
        material = materiais.processar_material(material.id)
        if material.status != "pronto":
            raise CommandError(f"O material da aula {aula.numero} ficou {material.status}.")
    return disciplina.id


class Command(BaseCommand):
    help = "Avalia o tutor com o conjunto de perguntas (TUT-CS-01, 03 e 04)."

    def add_arguments(self, parser):
        parser.add_argument("--conjunto", default=CONJUNTO_PADRAO)
        parser.add_argument("--limite", type=int, help="Faz só as primeiras N perguntas.")
        parser.add_argument("--detalhes", action="store_true", help="Mostra cada pergunta.")
        parser.add_argument(
            "--so-relatorio",
            action="store_true",
            help="Não termina com erro quando uma meta não é atingida.",
        )

    def handle(self, *args, conjunto: str, limite, detalhes: bool, so_relatorio: bool, **opcoes):
        dados = carregar(conjunto)
        perguntas = dados.perguntas[:limite] if limite else dados.perguntas
        self.stdout.write(
            f"{dados.disciplina}: {len(perguntas)} perguntas, adaptador "
            f"{settings.FAROL_IA['ADAPTADOR'].rsplit('.', 1)[-1]}"
        )

        def ao_responder(numero: int, resultado: Resultado) -> None:
            if detalhes or not _acertou(resultado):
                self.stdout.write(_linha(numero, resultado))

        pasta = tempfile.mkdtemp(prefix="avaliacao-")
        inicio = time.perf_counter()
        try:
            # Os PDFs vão para uma pasta temporária, apagada no fim, e o banco é desfeito.
            with override_settings(MEDIA_ROOT=pasta), transaction.atomic():
                disciplina_id = _preparar_disciplina(dados)
                relatorio = avaliar(disciplina_id, perguntas, ao_responder)
                raise _Desfazer
        except _Desfazer:
            pass
        finally:
            shutil.rmtree(pasta, ignore_errors=True)
        self._resumo(relatorio, time.perf_counter() - inicio)
        if not relatorio.metas_atingidas and not so_relatorio:
            raise CommandError("Alguma meta do tutor não foi atingida.")

    def _resumo(self, relatorio: Relatorio, segundos: float) -> None:
        com, sem = relatorio.com_base, relatorio.sem_base
        escrever = self.stdout.write
        escrever("")
        escrever(
            f"Citação da página certa (TUT-CS-01): {relatorio.citacoes_corretas}/{len(com)} = "
            f"{_por_cento(relatorio.taxa_de_citacao)} (meta: {_por_cento(META_DE_CITACAO)}) -> "
            + _situacao(relatorio.taxa_de_citacao >= META_DE_CITACAO)
        )
        escrever(
            f"Afirmações sem citação (TUT-CS-03): {relatorio.afirmacoes_sem_citacao} "
            "(meta: 0) -> " + _situacao(relatorio.afirmacoes_sem_citacao == 0)
        )
        escrever(
            f'"Não encontrei" nas perguntas sem base (TUT-CS-04): '
            f"{relatorio.nao_encontrei_sem_base}/{len(sem)} = "
            f"{_por_cento(relatorio.taxa_de_nao_encontrei)} "
            f"(meta: {_por_cento(META_DE_NAO_ENCONTREI)}) -> "
            + _situacao(relatorio.taxa_de_nao_encontrei >= META_DE_NAO_ENCONTREI)
        )
        if com and sem:
            escrever(
                "Similaridade da busca: com base, de "
                f"{min(r.similaridade for r in com):.3f} a {max(r.similaridade for r in com):.3f}; "
                f"sem base, de {min(r.similaridade for r in sem):.3f} a "
                f"{max(r.similaridade for r in sem):.3f}. Limite atual: "
                f"{settings.FAROL_TUTOR_SIMILARIDADE_MINIMA}; sugerido: "
                f"{relatorio.limite_sugerido()}"
            )
        escrever(f"Tempo: {segundos:.0f} s")


def _acertou(resultado: Resultado) -> bool:
    if resultado.pergunta.sem_base:
        return resultado.tipo == "nao_encontrado"
    return resultado.cita_a_pagina_certa and not resultado.afirmacao_sem_citacao


def _linha(numero: int, resultado: Resultado) -> str:
    pergunta = resultado.pergunta
    esperado = "sem base" if pergunta.sem_base else f"aula {pergunta.aula}, p. {pergunta.pagina}"
    citadas = ", ".join(f"aula {a}, p. {p}" for a, p in resultado.citadas) or "nenhuma"
    marca = "ok   " if _acertou(resultado) else "FALHA"
    return (
        f"{marca} {numero:3d}. {pergunta.texto} | esperado: {esperado} | tipo: {resultado.tipo} "
        f"| citou: {citadas} | similaridade: {resultado.similaridade:.3f}\n"
        f"           {resultado.texto[:300]}"
    )
