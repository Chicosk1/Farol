"""Rotas da própria pessoa. Só HTTP: as regras ficam em contas/servicos.py (ADR 0007)."""

from django.contrib.auth import login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contas import servicos

from .serializers import (
    AvisoDePrivacidadeSerializer,
    CienciaDoAvisoSerializer,
    EntradaDeDesenvolvimentoSerializer,
    EuSerializer,
    TrocaDePerfilSerializer,
)


def _dados_da_pessoa(request: Request) -> dict:
    pessoa = request.user
    perfil = servicos.perfil_ativo(pessoa, request.session)
    return {
        "id": pessoa.id,
        "email": pessoa.email,
        "nome": pessoa.nome,
        "perfis": pessoa.perfis,
        "perfil_ativo": perfil,
        "precisa_ver_aviso": servicos.precisa_ver_aviso(pessoa, perfil),
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


@extend_schema(
    summary="Entra pelo e-mail, sem login institucional (só desenvolvimento e teste)",
    request=EntradaDeDesenvolvimentoSerializer,
    responses=EuSerializer,
    tags=["desenvolvimento"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def entrar_em_desenvolvimento(request: Request) -> Response:
    """Abre a sessão de uma pessoa fictícia pelo e-mail. A rota só existe com
    FAROL_LOGIN_DESENVOLVIMENTO ligado (ACE-RNF-03)."""
    entrada = EntradaDeDesenvolvimentoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    try:
        pessoa = servicos.pessoa_ativa_por_email(entrada.validated_data["email"])
    except servicos.PessoaNaoEncontrada:
        return Response(
            {"email": ["Não há pessoa ativa com este e-mail."]}, status=status.HTTP_400_BAD_REQUEST
        )
    login(request._request, pessoa, backend="django.contrib.auth.backends.ModelBackend")
    request.user = pessoa
    return Response(EuSerializer(_dados_da_pessoa(request)).data)


@extend_schema(summary="Encerra a sessão", request=None, responses={204: None}, tags=["contas"])
@api_view(["POST"])
@permission_classes([AllowAny])
def sair(request: Request) -> Response:
    logout(request._request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Texto da versão atual do aviso de privacidade",
    responses=AvisoDePrivacidadeSerializer,
    tags=["contas"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def aviso_de_privacidade(request: Request) -> Response:
    return Response(AvisoDePrivacidadeSerializer(servicos.texto_do_aviso()).data)


@extend_schema(
    summary="Registra que a pessoa leu a versão atual do aviso de privacidade",
    request=CienciaDoAvisoSerializer,
    responses={204: None},
    tags=["contas"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ciencia_de_privacidade(request: Request) -> Response:
    entrada = CienciaDoAvisoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    try:
        servicos.registrar_ciencia(request.user, entrada.validated_data["versao"])
    except servicos.VersaoDoAvisoDesatualizada:
        return Response(
            {"versao": ["Esta não é mais a versão atual do aviso. Recarregue a página."]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(status=status.HTTP_204_NO_CONTENT)
