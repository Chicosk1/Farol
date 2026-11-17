"""Dúvidas que o tutor não respondeu, enviadas ao professor sem o nome do aluno (spec 004)."""

from django.db import IntegrityError, transaction
from django.utils import timezone

from tutor import servicos as tutor

from .models import Duvida, EnvioDuvida

LIMITE_POR_DIA = 5

MensagemNaoEncontrada = tutor.MensagemNaoEncontrada


class NaoPodeVirarDuvida(ValueError):
    """Só a resposta "não encontrei" do tutor vira dúvida."""


class DuvidaJaEnviada(RuntimeError):
    """A dúvida desta resposta já foi enviada (DUV-RF-04)."""


class LimiteDeDuvidas(RuntimeError):
    """O aluno já enviou as 5 dúvidas do dia nesta disciplina."""


def _pergunta(aluno, mensagem_id: int) -> tutor.PerguntaSemResposta:
    pergunta = tutor.pergunta_sem_resposta(aluno, mensagem_id)
    if pergunta is None:
        raise NaoPodeVirarDuvida('Só a resposta "não encontrei" pode virar dúvida.')
    if EnvioDuvida.objects.filter(mensagem_id=mensagem_id).exists():
        raise DuvidaJaEnviada(mensagem_id)
    return pergunta


def previa(aluno, mensagem_id: int) -> str:
    """O texto exato que o professor vai ler, já sem dados pessoais (DUV-RF-02)."""
    return _pergunta(aluno, mensagem_id).texto


def enviar(aluno, mensagem_id: int) -> Duvida:
    """Cria a dúvida da disciplina; o envio, do lado do aluno, impede repetir (DUV-RF-01, 04)."""
    pergunta = _pergunta(aluno, mensagem_id)
    hoje = timezone.localdate()
    enviadas_hoje = EnvioDuvida.objects.filter(
        mensagem__conversa__aluno=aluno,
        duvida__disciplina_id=pergunta.disciplina_id,
        enviada_em__date=hoje,
    ).count()
    if enviadas_hoje >= LIMITE_POR_DIA:
        raise LimiteDeDuvidas(LIMITE_POR_DIA)
    try:
        with transaction.atomic():
            duvida = Duvida.objects.create(
                disciplina_id=pergunta.disciplina_id, texto=pergunta.texto, data=hoje
            )
            EnvioDuvida.objects.create(mensagem_id=mensagem_id, duvida=duvida)
    except IntegrityError:
        raise DuvidaJaEnviada(mensagem_id) from None  # dois toques ao mesmo tempo
    return duvida
