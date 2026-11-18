"""Rotas da revisão do dia. Só HTTP: as regras ficam em revisao/servicos.py (ADR 0007)."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from nucleo.permissoes import exige_perfil_ativo
from revisao import servicos

from .serializers import (
    AgendaDoCartaoSerializer,
    AvaliacaoDoCartaoSerializer,
    LembreteSerializer,
    RespostaAoCartaoSerializer,
    RetornoDoCartaoSerializer,
    RevisaoDeHojeSerializer,
)


@extend_schema(
    summary="A revisão do dia do aluno, com a sequência dos últimos 7 dias",
    responses=RevisaoDeHojeSerializer,
    tags=["revisao"],
)
@api_view(["GET"])
@permission_classes([exige_perfil_ativo("aluno")])
def hoje(request: Request) -> Response:
    return Response(RevisaoDeHojeSerializer(servicos.revisao_de_hoje(request.user)).data)


@extend_schema(
    summary="Responde a um cartão da revisão",
    request=RespostaAoCartaoSerializer,
    responses=RetornoDoCartaoSerializer,
    tags=["revisao"],
)
@api_view(["POST"])
@permission_classes([exige_perfil_ativo("aluno")])
def responder(request: Request, cartao_id: int) -> Response:
    entrada = RespostaAoCartaoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    try:
        retorno = servicos.responder_cartao(
            request.user, cartao_id, entrada.validated_data["alternativa"]
        )
    except servicos.NaoEncontrado:
        raise Http404 from None
    except servicos.JaRespondido:
        return Response(
            {"detail": "Este cartão já foi respondido hoje."}, status=status.HTTP_409_CONFLICT
        )
    return Response(RetornoDoCartaoSerializer(retorno).data)


@extend_schema(
    summary="Avalia um cartão como Difícil, Bom ou Fácil e diz quando ele volta",
    request=AvaliacaoDoCartaoSerializer,
    responses=AgendaDoCartaoSerializer,
    tags=["revisao"],
)
@api_view(["POST"])
@permission_classes([exige_perfil_ativo("aluno")])
def avaliar(request: Request, cartao_id: int) -> Response:
    entrada = AvaliacaoDoCartaoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    try:
        agenda = servicos.avaliar_cartao(
            request.user, cartao_id, entrada.validated_data["avaliacao"]
        )
    except servicos.NaoEncontrado:
        raise Http404 from None
    except (servicos.JaRespondido, servicos.AindaNaoRespondido):
        return Response(
            {"detail": "Responda ao cartão antes de avaliar, uma vez só."},
            status=status.HTTP_409_CONFLICT,
        )
    return Response(AgendaDoCartaoSerializer(agenda).data)


@extend_schema(
    methods=["GET"],
    summary="O lembrete diário da revisão",
    responses=LembreteSerializer,
    tags=["revisao"],
)
@extend_schema(
    methods=["PUT"],
    summary="Liga ou desliga o lembrete diário, por e-mail",
    request=LembreteSerializer,
    responses=LembreteSerializer,
    tags=["revisao"],
)
@api_view(["GET", "PUT"])
@permission_classes([exige_perfil_ativo("aluno")])
def lembrete(request: Request) -> Response:
    if request.method == "PUT":
        entrada = LembreteSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        preferencia = servicos.salvar_lembrete(request.user, **entrada.validated_data)
    else:
        preferencia = servicos.preferencia_de_lembrete(request.user)
    return Response(LembreteSerializer(preferencia).data)
