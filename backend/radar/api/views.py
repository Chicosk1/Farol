"""Rotas do radar. Só HTTP: as regras ficam em radar/servicos.py (ADR 0007)."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from nucleo.permissoes import acesso_a_disciplina
from radar import servicos

from .serializers import (
    ExemploSerializer,
    FiltroDaSemanaSerializer,
    RadarSerializer,
    SemanaSerializer,
)


@extend_schema(
    summary="O radar da turma numa semana",
    description="Só o professor da disciplina. Sem semana, vale a atual (RAD-RF-02 a 09).",
    parameters=[FiltroDaSemanaSerializer],
    responses=RadarSerializer,
    tags=["radar"],
)
@api_view(["GET"])
@permission_classes([acesso_a_disciplina("professor")])
def radar(request: Request, disciplina_id: int) -> Response:
    filtro = FiltroDaSemanaSerializer(data=request.query_params)
    filtro.is_valid(raise_exception=True)
    semana = filtro.validated_data.get("semana") or servicos.semana_atual()
    return Response(RadarSerializer(servicos.radar(disciplina_id, semana)).data)


@extend_schema(
    summary="As semanas que o seletor do radar oferece",
    responses=SemanaSerializer(many=True),
    tags=["radar"],
)
@api_view(["GET"])
@permission_classes([acesso_a_disciplina("professor")])
def semanas(request: Request, disciplina_id: int) -> Response:
    return Response(SemanaSerializer(servicos.semanas_disponiveis(), many=True).data)


@extend_schema(
    summary="Esconde uma pergunta de exemplo do radar",
    request=ExemploSerializer,
    responses={204: None},
    tags=["radar"],
)
@api_view(["POST"])
@permission_classes([acesso_a_disciplina("professor")])
def ocultar_exemplo(request: Request, disciplina_id: int) -> Response:
    entrada = ExemploSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    servicos.ocultar_exemplo(disciplina_id, request.user, entrada.validated_data["texto"])
    return Response(status=status.HTTP_204_NO_CONTENT)
