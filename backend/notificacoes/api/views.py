"""Rotas das notificações. Só HTTP: as regras ficam em notificacoes/servicos.py (ADR 0007)."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from notificacoes import servicos

from .serializers import NotificacoesSerializer


@extend_schema(
    summary="As notificações da pessoa, das mais novas, e quantas não foram lidas",
    responses=NotificacoesSerializer,
    tags=["notificacoes"],
)
@api_view(["GET"])
def listar(request: Request) -> Response:
    notificacoes, nao_lidas = servicos.notificacoes_de(request.user)
    dados = {"notificacoes": notificacoes, "nao_lidas": nao_lidas}
    return Response(NotificacoesSerializer(dados).data)


@extend_schema(
    summary="Marca a notificação como lida",
    request=None,
    responses={204: None},
    tags=["notificacoes"],
)
@api_view(["POST"])
def marcar_como_lida(request: Request, notificacao_id: int) -> Response:
    try:
        servicos.marcar_como_lida(request.user, notificacao_id)
    except servicos.NotificacaoNaoEncontrada:
        raise Http404 from None
    return Response(status=status.HTTP_204_NO_CONTENT)
