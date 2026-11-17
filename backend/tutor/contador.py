"""Contador diário de perguntas ao tutor, no Redis (TUT-RF-08).

Chave `limite:{disciplina}:{aluno}:{AAAA-MM-DD}`, com o dia de Brasília e expiração de 48 horas
(plan.md). A pergunta reserva a sua vaga antes de ir ao provedor: o incremento é atômico, então
duas perguntas ao mesmo tempo não passam do limite. Se o provedor falhar, a vaga é devolvida.
"""

from datetime import date
from functools import cache

import redis
from django.conf import settings
from django.utils import timezone

EXPIRACAO = 48 * 3600


@cache
def cliente() -> redis.Redis:
    return redis.Redis.from_url(settings.FAROL_REDIS_URL)


def hoje() -> date:
    """O dia no horário de Brasília (TIME_ZONE): o limite zera à meia-noite daqui."""
    return timezone.localdate()


def chave(disciplina_id: int, aluno_id: int, dia: date) -> str:
    return f"limite:{disciplina_id}:{aluno_id}:{dia:%Y-%m-%d}"


def usadas(disciplina_id: int, aluno_id: int) -> int:
    """Quantas perguntas o aluno já fez hoje na disciplina."""
    valor = cliente().get(chave(disciplina_id, aluno_id, hoje()))
    return int(valor or 0)


def reservar(disciplina_id: int, aluno_id: int, limite: int) -> bool:
    """Conta uma pergunta, se ainda houver vaga hoje. Falso, sem contar, se o limite acabou."""
    nome = chave(disciplina_id, aluno_id, hoje())
    with cliente().pipeline() as operacoes:
        operacoes.incr(nome)
        operacoes.expire(nome, EXPIRACAO)
        total, _ = operacoes.execute()
    if total > limite:
        cliente().decr(nome)
        return False
    return True


def devolver(disciplina_id: int, aluno_id: int) -> None:
    """Desfaz a reserva de uma pergunta que não chegou a ser respondida."""
    cliente().decr(chave(disciplina_id, aluno_id, hoje()))
