"""O SM-2 da revisão do dia, numa função pura (REV-RF-04).

A nota do SM-2 vem do acerto e da avaliação: erro = 1 (o cartão recomeça e volta amanhã),
Difícil = 3, Bom = 4 e Fácil = 5. Os primeiros intervalos seguem o protótipo (Difícil volta
amanhã, Bom em 3 dias, Fácil em 4); depois, o intervalo cresce pela facilidade.
"""

from dataclasses import dataclass
from datetime import date, timedelta

NOTAS = {"dificil": 3, "bom": 4, "facil": 5}
PRIMEIRO_INTERVALO = {3: 1, 4: 3, 5: 4}
SEGUNDO_INTERVALO = {3: 3, 4: 6, 5: 8}
FACILIDADE_MINIMA = 1.3


@dataclass(frozen=True)
class Agenda:
    facilidade: float
    intervalo_dias: int
    repeticoes: int
    proxima_data: date


def agendar(
    facilidade: float,
    intervalo_dias: int,
    repeticoes: int,
    acerto: bool,
    avaliacao: str,
    hoje: date,
) -> Agenda:
    if avaliacao not in NOTAS:
        raise ValueError(f"Avaliação desconhecida: {avaliacao!r}")
    nota = NOTAS[avaliacao] if acerto else 1
    if nota < 3:
        repeticoes, intervalo = 0, 1
    else:
        repeticoes += 1
        if repeticoes == 1:
            intervalo = PRIMEIRO_INTERVALO[nota]
        elif repeticoes == 2:
            intervalo = SEGUNDO_INTERVALO[nota]
        else:
            # Difícil cresce pouco; Fácil ganha um bônus, como nas variações comuns do SM-2.
            fator = {3: 1.2, 4: facilidade, 5: facilidade * 1.3}[nota]
            intervalo = max(intervalo_dias + 1, round(intervalo_dias * fator))
    facilidade = max(
        FACILIDADE_MINIMA, facilidade + (0.1 - (5 - nota) * (0.08 + (5 - nota) * 0.02))
    )
    return Agenda(round(facilidade, 2), intervalo, repeticoes, hoje + timedelta(days=intervalo))


def quando_volta(proxima: date, hoje: date) -> str:
    """O texto que o aluno vê depois de avaliar (REV-RF-05)."""
    dias = (proxima - hoje).days
    if dias <= 1:
        return "Este cartão volta amanhã."
    return f"Este cartão volta em {dias} dias."
