"""Rotas da própria pessoa. Só HTTP: as regras ficam em contas/servicos.py (ADR 0007)."""

from django.contrib.auth import logout
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contas import servicos

from .serializers import EuSerializer, TrocaDePerfilSerializer


def _dados_da_pessoa(request: Request) -> dict:
    pessoa = request.user
    return {
        "id": pessoa.id,
        "email": pessoa.email,
        "nome": pessoa.nome,
        "perfis": pessoa.perfis,
        "perfil_ativo": servicos.perfil_ativo(pessoa, request.session),
    }


@extend_schema(summary="A pessoa que está logada", responses=EuSerializer, tags=["contas"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie  # entrega o cookie do token CSRF, enviado nas chamadas que mudam dados
def eu(request: Request) -> Response:
    return Response(EuSerializer(_dados_da_pessoa(request)).data)


@extend_schema(
    summary="Troca o perfil em uso, sem sair",
    request=TrocaDePerfilSerializer,
    responses=EuSerializer,
    tags=["contas"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def perfil_ativo(request: Request) -> Response:
    entrada = TrocaDePerfilSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    try:
        servicos.trocar_perfil_ativo(
            request.user, request.session, entrada.validated_data["perfil"]
        )
    except servicos.PerfilInvalido:
        return Response(
            {"perfil": ["Você não tem este perfil."]}, status=status.HTTP_400_BAD_REQUEST
        )
    return Response(EuSerializer(_dados_da_pessoa(request)).data)


@extend_schema(summary="Encerra a sessão", request=None, responses={204: None}, tags=["contas"])
@api_view(["POST"])
@permission_classes([AllowAny])
def sair(request: Request) -> Response:
    logout(request._request)
    return Response(status=status.HTTP_204_NO_CONTENT)
