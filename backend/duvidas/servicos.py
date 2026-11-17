"""Dúvidas que o tutor não respondeu, enviadas ao professor sem o nome do aluno (spec 004)."""

from django.db import IntegrityError, transaction
from django.utils import timezone

from disciplinas import servicos as disciplinas
from notificacoes import servicos as notificacoes
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
    _avisar_professor(duvida)
    return duvida


def _avisar_professor(duvida: Duvida) -> None:
    """O aviso no sino do professor, com o começo do texto e sem nada do aluno (DUV-RF-06)."""
    nome, professor = disciplinas.disciplina_e_professor(duvida.disciplina_id)
    if professor is None:
        return
    trecho = duvida.texto if len(duvida.texto) <= 80 else duvida.texto[:79] + "…"
    notificacoes.notificar(
        professor,
        notificacoes.Tipo.DUVIDA_NOVA,
        f"Nova dúvida em {nome}: {trecho}",
        link=f"/disciplinas/{duvida.disciplina_id}/duvidas",
    )


class StatusInvalido(ValueError):
    """O professor só lista as abertas ou as respondidas."""


def duvidas_para_o_professor(disciplina_id: int, status: str = Duvida.Status.ABERTA) -> list[dict]:
    """As dúvidas da disciplina, da mais recente, com a marca "nova" (DUV-RF-05).

    Depois de listadas, as abertas passam a vistas: na próxima vez, já não são novas.
    """
    if status not in (Duvida.Status.ABERTA, Duvida.Status.RESPONDIDA):
        raise StatusInvalido(status)
    duvidas = list(Duvida.objects.filter(disciplina_id=disciplina_id, status=status))
    lista = [
        {"id": d.id, "texto": d.texto, "data": d.data, "status": d.status, "nova": not d.vista}
        for d in duvidas
    ]
    Duvida.objects.filter(id__in=[d.id for d in duvidas if not d.vista]).update(vista=True)
    return lista


class DuvidaNaoEncontrada(LookupError):
    """A dúvida não existe ou não é desta disciplina."""


def mudar_status(professor, disciplina_id: int, duvida_id: int, status: str) -> Duvida:
    """Respondida em aula ou oculta; a ocultação guarda quem ocultou e quando (DUV-RF-07)."""
    if status not in (Duvida.Status.RESPONDIDA, Duvida.Status.OCULTA):
        raise StatusInvalido(status)
    try:
        duvida = Duvida.objects.get(id=duvida_id, disciplina_id=disciplina_id)
    except Duvida.DoesNotExist:
        raise DuvidaNaoEncontrada(duvida_id) from None
    duvida.status = status
    duvida.vista = True
    if status == Duvida.Status.OCULTA:
        duvida.ocultada_por = professor
        duvida.ocultada_em = timezone.now()
    duvida.save()
    return duvida
