"""Mede o tempo até a primeira palavra da resposta do tutor, com perguntas simultâneas
(TUT-T92, TUT-RNF-01: até 3 segundos no percentil 95).

Uso: python manage.py medir_tutor --disciplina ID [--perguntas 40] [--simultaneas 5]
Usa o material já publicado na disciplina e o provedor configurado. Não guarda conversas nem
registros de uso: mede só a busca e o começo da resposta.
"""

import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from django.core.management.base import BaseCommand, CommandError
from django.db import close_old_connections

from tutor import servicos

META_EM_SEGUNDOS = 3.0
PERGUNTAS = [
    "O que é uma lista encadeada?",
    "Qual o custo de inserir no início de uma lista?",
    "Como funciona uma pilha?",
    "Qual a diferença entre pilha e fila?",
    "Por que a busca binária é O(log n)?",
]


def tempo_ate_a_primeira_palavra(disciplina_id: int, pergunta: str) -> float:
    close_old_connections()
    inicio = time.perf_counter()
    try:
        for evento in servicos.responder_pergunta(disciplina_id, pergunta, modo_pistas=True):
            if isinstance(evento, servicos.Texto):
                break
        return time.perf_counter() - inicio
    finally:
        close_old_connections()


def percentil_95(tempos: list[float]) -> float:
    if len(tempos) == 1:
        return tempos[0]
    return statistics.quantiles(tempos, n=20, method="inclusive")[18]


class Command(BaseCommand):
    help = "Mede o tempo até a primeira palavra do tutor (meta: 3 s no percentil 95)."

    def add_arguments(self, parser):
        parser.add_argument("--disciplina", type=int, required=True)
        parser.add_argument("--perguntas", type=int, default=40)
        parser.add_argument("--simultaneas", type=int, default=5)

    def handle(self, *args, disciplina: int, perguntas: int, simultaneas: int, **opcoes):
        if perguntas < 1 or simultaneas < 1:
            raise CommandError("Use pelo menos 1 pergunta e 1 pergunta simultânea.")
        lista = [PERGUNTAS[i % len(PERGUNTAS)] for i in range(perguntas)]
        with ThreadPoolExecutor(max_workers=simultaneas) as executor:
            tempos = list(
                executor.map(lambda p: tempo_ate_a_primeira_palavra(disciplina, p), lista)
            )
        p95 = percentil_95(tempos)
        self.stdout.write(
            f"{perguntas} perguntas, {simultaneas} ao mesmo tempo: "
            f"mediana {statistics.median(tempos):.2f} s, p95 {p95:.2f} s "
            f"(meta: {META_EM_SEGUNDOS:.0f} s) -> "
            + ("dentro da meta" if p95 <= META_EM_SEGUNDOS else "ACIMA DA META")
        )
