"""Rotas de questões. Só HTTP: as regras ficam em questoes/servicos.py (ADR 0007)."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contas import servicos as contas
from questoes import servicos

from .serializers import GeracaoSerializer, PedidoDeGeracaoSerializer

MENSAGEM_AULA_NAO_PRONTA = (
    "Esta aula ainda não está pronta. Espere o processamento do PDF terminar para gerar questões."
)


@extend_schema(
    summary="Pede rascunhos de questões de uma aula",
    description=(
        "Só o professor da disciplina. A geração roda em segundo plano: acompanhe pelo id do "
        "pedido. Se já há um pedido em andamento para a aula, devolve esse (QUE-RF-01)."
    ),
    request=PedidoDeGeracaoSerializer,
    responses={202: GeracaoSerializer},
    tags=["questoes"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pedir(request: Request, material_id: int) -> Response:
    entrada = PedidoDeGeracaoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        pedido = servicos.pedir_geracao(
            request.user, perfil, material_id, entrada.validated_data["quantidade"]
        )
    except servicos.NaoEncontrado:
        raise Http404 from None
    except servicos.SemAcesso:
        raise PermissionDenied from None
    except servicos.AulaNaoPronta:
        return Response({"detail": MENSAGEM_AULA_NAO_PRONTA}, status=status.HTTP_409_CONFLICT)
    if pedido.status == pedido.Status.PROCESSANDO:
        servicos.enfileirar_geracao(pedido.id)
        pedido.refresh_from_db()
    return Response(GeracaoSerializer(pedido).data, status=status.HTTP_202_ACCEPTED)


@extend_schema(
    summary="Andamento de um pedido de rascunhos",
    responses=GeracaoSerializer,
    tags=["questoes"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def geracao(request: Request, pedido_id: int) -> Response:
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        pedido = servicos.pedido_para_ver(request.user, perfil, pedido_id)
    except servicos.NaoEncontrado:
        raise Http404 from None
    except servicos.SemAcesso:
        raise PermissionDenied from None
    return Response(GeracaoSerializer(pedido).data)
