"""Registros sintéticos para os testes do radar (RAD-T11): perguntas e respostas de N alunos
pseudônimos, sem pessoas de verdade."""

from datetime import date, datetime, time

from django.utils import timezone

from questoes.models import Questao, RespostaQuiz
from tutor.models import RegistroUso


def no_dia(dia: date):
    return timezone.make_aware(datetime.combine(dia, time(10, 0)))


def perguntas(disciplina, trecho, alunos: int, dia: date, prefixo="aluno", texto="Como funciona?"):
    for i in range(alunos):
        RegistroUso.objects.create(
            aluno_pseudonimo=f"{prefixo}-{i}",
            disciplina=disciplina,
            pergunta_filtrada=f"{texto} ({i})",
            trechos=[trecho.id],
            tipo="respondida",
            criado_em=no_dia(dia),
        )


def respostas(questao: Questao, alunos: int, acertos: int, dia: date, prefixo="aluno"):
    for i in range(alunos):
        RespostaQuiz.objects.create(
            questao=questao,
            aluno_pseudonimo=f"{prefixo}-{i}",
            alternativa=questao.correta if i < acertos else (questao.correta + 1) % 4,
            acerto=i < acertos,
            respondida_em=dia,
        )
