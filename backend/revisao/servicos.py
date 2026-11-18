"""Regras da revisão do dia (spec 006). Chamado pela API, pelas tarefas e por outros módulos."""

import logging
import math
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Case, IntegerField, Value, When
from django.utils import timezone

from contas.servicos import Perfil
from disciplinas import servicos as disciplinas
from questoes import servicos as questoes
from tutor import servicos as tutor

from .agenda import agendar, quando_volta
from .models import Cartao, PreferenciaLembrete, SessaoRevisao

logger = logging.getLogger(__name__)

MAXIMO_DE_CARTOES = 10  # REV-RF-02
HORA_DA_NOVA_SESSAO = 6  # REV-RF-08: a sessão nova fica pronta às 6h, horário de Brasília
SEGUNDOS_POR_CARTAO = 30


class NaoEncontrado(LookupError):
    pass


class JaRespondido(Exception):
    pass


class AindaNaoRespondido(Exception):
    pass


def dia_da_revisao(agora=None) -> date:
    """O dia da sessão: antes das 6h, ainda vale a sessão do dia anterior."""
    local = timezone.localtime(agora or timezone.now())
    return (local - timedelta(hours=HORA_DA_NOVA_SESSAO)).date()


def _disciplinas_do_aluno(aluno) -> dict[int, str]:
    """As disciplinas ativas do aluno, sem as que estão em modo prova (decisão da spec 006)."""
    return {
        d.id: d.nome
        for d in disciplinas.listar_disciplinas(aluno, Perfil.ALUNO)
        if not tutor.tutor_pausado(d.id)
    }


def _garantir_cartoes(aluno, publicadas: set[int]) -> None:
    """Um cartão para cada questão publicada nas disciplinas do aluno (REV-RF-01)."""
    existentes = set(
        Cartao.objects.filter(aluno=aluno, questao_id__in=publicadas).values_list(
            "questao_id", flat=True
        )
    )
    novos = [Cartao(aluno=aluno, questao_id=q) for q in publicadas - existentes]
    Cartao.objects.bulk_create(novos, ignore_conflicts=True)


def _vencidos(aluno, publicadas: set[int], hoje: date):
    """Os cartões vencidos, primeiro os que o aluno errou ou achou difíceis, depois os mais
    atrasados (REV-RF-02, cenário 3 da história 2)."""
    return (
        Cartao.objects.filter(aluno=aluno, questao_id__in=publicadas, proxima_data__lte=hoje)
        .annotate(
            prioridade=Case(
                When(ultima_avaliacao__in=["erro", "dificil"], then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("prioridade", "proxima_data", "id")
    )


def montar_sessao(aluno, hoje: date | None = None) -> SessaoRevisao | None:
    """A sessão do dia, montada uma vez e guardada: o número de cartões não muda ao longo do dia.

    Sem cartões vencidos, nada é guardado, para que questões publicadas mais tarde no mesmo dia
    ainda entrem.
    """
    hoje = hoje or dia_da_revisao()
    existente = SessaoRevisao.objects.filter(aluno=aluno, data=hoje).first()
    if existente:
        return existente
    publicadas = questoes.ids_publicadas(set(_disciplinas_do_aluno(aluno)))
    _garantir_cartoes(aluno, publicadas)
    ids = list(_vencidos(aluno, publicadas, hoje).values_list("id", flat=True)[:MAXIMO_DE_CARTOES])
    if not ids:
        return None
    sessao, _ = SessaoRevisao.objects.get_or_create(
        aluno=aluno, data=hoje, defaults={"cartoes": ids}
    )
    return sessao


def montar_sessoes_do_dia() -> int:
    """Tarefa das 6h: a sessão de cada aluno com matrícula ativa (REV-RF-08)."""
    hoje = dia_da_revisao()
    alunos = (
        get_user_model().objects.filter(matriculas__situacao="ativa", is_active=True).distinct()
    )
    return sum(1 for aluno in alunos if montar_sessao(aluno, hoje))


def _sequencia(aluno, hoje: date) -> tuple[list[dict], int]:
    """Os últimos 7 dias, terminando hoje, e quantos dias seguidos de revisão (REV-RF-07)."""
    feitas = set(
        SessaoRevisao.objects.filter(
            aluno=aluno, concluida=True, data__gte=hoje - timedelta(days=60)
        ).values_list("data", flat=True)
    )
    dias = [
        {"data": hoje - timedelta(days=d), "feita": (hoje - timedelta(days=d)) in feitas}
        for d in range(6, -1, -1)
    ]
    seguidos = 0
    dia = hoje if hoje in feitas else hoje - timedelta(days=1)
    while dia in feitas:
        seguidos += 1
        dia -= timedelta(days=1)
    return dias, seguidos


def _cartoes_validos(sessao: SessaoRevisao, nomes: dict[int, str]) -> list[Cartao]:
    """Os cartões da sessão que continuam valendo: questão ainda publicada e disciplina fora do
    modo prova. Uma questão despublicada sai da agenda (caso de borda da spec 006)."""
    por_id = {
        c.id: c
        for c in Cartao.objects.filter(id__in=sessao.cartoes).select_related(
            "questao__material", "questao__trecho"
        )
    }
    validos = []
    for cartao_id in sessao.cartoes:
        cartao = por_id.get(cartao_id)
        if (
            cartao
            and cartao.questao.status == questoes.StatusDaQuestao.PUBLICADA
            and cartao.questao.material.disciplina_id in nomes
        ):
            validos.append(cartao)
    return validos


def revisao_de_hoje(aluno) -> dict:
    """Tudo o que a tela inicial e a tela da revisão mostram (REV-RF-06)."""
    hoje = dia_da_revisao()
    nomes = _disciplinas_do_aluno(aluno)
    sessao = montar_sessao(aluno, hoje)
    cartoes = _cartoes_validos(sessao, nomes) if sessao else []
    ids = {c.id for c in cartoes}
    por_id = {c.id: c for c in cartoes}
    respostas = []
    for r in sessao.respostas if sessao else []:
        if r["cartao"] in ids:
            retorno = questoes.retorno_da_questao(por_id[r["cartao"]].questao, r["alternativa"])
            respostas.append(
                retorno
                | {
                    "cartao": r["cartao"],
                    "avaliacao": r.get("avaliacao") or "",
                    "volta": r.get("volta") or "",
                }
            )
    concluida = (
        bool(cartoes)
        and all(r["avaliacao"] for r in respostas)
        and (len(respostas) == len(cartoes))
    )
    if sessao and concluida and not sessao.concluida:
        sessao.concluida = True
        sessao.save(update_fields=["concluida"])
    dias, seguidos = _sequencia(aluno, hoje)
    disciplinas_da_sessao = sorted({nomes[c.questao.material.disciplina_id] for c in cartoes})
    return {
        "data": hoje,
        "cartoes": [
            {
                "id": c.id,
                "disciplina": c.questao.material.disciplina_id,
                "disciplina_nome": nomes[c.questao.material.disciplina_id],
                "enunciado": c.questao.enunciado,
                "alternativas": c.questao.alternativas,
                "topico": c.questao.topico,
            }
            for c in cartoes
        ],
        "respostas": respostas,
        "concluida": concluida,
        "disciplinas": disciplinas_da_sessao,
        "minutos": max(1, math.ceil(len(cartoes) * SEGUNDOS_POR_CARTAO / 60)),
        "tem_questoes": bool(questoes.ids_publicadas(set(nomes))),
        "sequencia": dias,
        "dias_seguidos": seguidos,
    }


def _cartao_da_sessao(aluno, cartao_id: int) -> tuple[SessaoRevisao, Cartao]:
    hoje = dia_da_revisao()
    sessao = SessaoRevisao.objects.select_for_update().filter(aluno=aluno, data=hoje).first()
    if not sessao or cartao_id not in sessao.cartoes:
        raise NaoEncontrado(cartao_id)
    validos = _cartoes_validos(sessao, _disciplinas_do_aluno(aluno))
    cartao = next((c for c in validos if c.id == cartao_id), None)
    if not cartao:
        raise NaoEncontrado(cartao_id)
    return sessao, cartao


def responder_cartao(aluno, cartao_id: int, alternativa: int) -> dict:
    """Corrige e mostra o retorno, como no quiz (REV-RF-03). A resposta vai para o radar com o
    pseudônimo e o contexto "revisão"."""
    with transaction.atomic():
        sessao, cartao = _cartao_da_sessao(aluno, cartao_id)
        if any(r["cartao"] == cartao_id for r in sessao.respostas):
            raise JaRespondido(cartao_id)
        questao = cartao.questao
        questoes.registrar_resposta(questao, aluno, alternativa, "revisao")
        sessao.respostas = [
            *sessao.respostas,
            {
                "cartao": cartao_id,
                "alternativa": alternativa,
                "acerto": alternativa == questao.correta,
                "avaliacao": "",
            },
        ]
        sessao.save(update_fields=["respostas"])
    return questoes.retorno_da_questao(questao, alternativa) | {"cartao": cartao_id}


def avaliar_cartao(aluno, cartao_id: int, avaliacao: str) -> dict:
    """Agenda o cartão pelo SM-2 e diz quando ele volta (REV-RF-04, REV-RF-05)."""
    hoje = dia_da_revisao()
    with transaction.atomic():
        sessao, cartao = _cartao_da_sessao(aluno, cartao_id)
        resposta = next((r for r in sessao.respostas if r["cartao"] == cartao_id), None)
        if not resposta:
            raise AindaNaoRespondido(cartao_id)
        if resposta.get("avaliacao"):
            raise JaRespondido(cartao_id)
        agenda = agendar(
            cartao.facilidade,
            cartao.intervalo_dias,
            cartao.repeticoes,
            resposta["acerto"],
            avaliacao,
            hoje,
        )
        cartao.facilidade = agenda.facilidade
        cartao.intervalo_dias = agenda.intervalo_dias
        cartao.repeticoes = agenda.repeticoes
        cartao.proxima_data = agenda.proxima_data
        cartao.ultima_avaliacao = avaliacao if resposta["acerto"] else "erro"
        cartao.save()
        texto = quando_volta(agenda.proxima_data, hoje)
        sessao.respostas = [
            r | {"avaliacao": avaliacao, "volta": texto} if r["cartao"] == cartao_id else r
            for r in sessao.respostas
        ]
        sessao.save(update_fields=["respostas"])
    return {"proxima_data": agenda.proxima_data, "texto": texto}


# --- Lembrete (história 4) ---


def preferencia_de_lembrete(aluno) -> PreferenciaLembrete:
    preferencia, _ = PreferenciaLembrete.objects.get_or_create(aluno=aluno)
    return preferencia


def salvar_lembrete(aluno, ligado: bool, horario) -> PreferenciaLembrete:
    preferencia = preferencia_de_lembrete(aluno)
    preferencia.ligado = ligado
    preferencia.horario = horario
    preferencia.save()
    return preferencia


def enviar_lembretes(agora=None) -> int:
    """Manda o e-mail a quem ligou o lembrete, já passou do horário e tem cartões a revisar.

    Um e-mail por dia, no máximo. Sem cartões vencidos, nada é enviado (REV-RF-09).
    """
    agora = timezone.localtime(agora or timezone.now())
    hoje = dia_da_revisao(agora)
    enviados = 0
    pendentes = PreferenciaLembrete.objects.filter(
        ligado=True, horario__lte=agora.time(), aluno__is_active=True
    ).exclude(ultimo_envio=hoje)
    for preferencia in pendentes.select_related("aluno"):
        aluno = preferencia.aluno
        sessao = montar_sessao(aluno, hoje)
        if not sessao or sessao.concluida:
            continue
        faltam = len(sessao.cartoes) - len(sessao.respostas)
        if faltam <= 0:
            continue
        send_mail(
            "Sua revisão do dia está pronta",
            f"Olá, {aluno.nome.split()[0]}! Você tem {faltam} cartões para revisar hoje, cerca "
            f"de {max(1, math.ceil(faltam * SEGUNDOS_POR_CARTAO / 60))} minutos. "
            f"Abra o Farol: {settings.FAROL_ENDERECO_PUBLICO}/revisao",
            None,
            [aluno.email],
        )
        preferencia.ultimo_envio = hoje
        preferencia.save(update_fields=["ultimo_envio"])
        enviados += 1
    return enviados
