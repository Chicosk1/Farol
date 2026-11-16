"""Rotas de disciplinas. Só HTTP: as regras ficam em disciplinas/servicos.py (ADR 0007)."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contas import servicos as contas
from disciplinas import servicos
from nucleo.permissoes import AcessoADisciplina

from .serializers import ConsultaDeDisciplinasSerializer, DisciplinaSerializer


@extend_schema(
    summary="Disciplinas da pessoa no perfil em uso",
    parameters=[ConsultaDeDisciplinasSerializer],
    responses=DisciplinaSerializer(many=True),
    tags=["disciplinas"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar(request: Request) -> Response:
    consulta = ConsultaDeDisciplinasSerializer(data=request.query_params)
    consulta.is_valid(raise_exception=True)
    disciplinas = servicos.listar_disciplinas(
        request.user,
        contas.perfil_ativo(request.user, request.session),
        busca=consulta.validated_data["busca"],
        filtro=consulta.validated_data["filtro"],
    )
    return Response(DisciplinaSerializer(disciplinas, many=True).data)


@extend_schema(
    summary="Marca a disciplina como favorita",
    request=None,
    responses={204: None},
    tags=["disciplinas"],
)
@extend_schema(methods=["DELETE"], summary="Tira a disciplina dos favoritos", responses={204: None})
@api_view(["PUT", "DELETE"])
@permission_classes([AcessoADisciplina])
def favorito(request: Request, disciplina_id: int) -> Response:
    if request.method == "PUT":
        servicos.favoritar(request.user, disciplina_id)
    else:
        servicos.desfavoritar(request.user, disciplina_id)
    return Response(status=status.HTTP_204_NO_CONTENT)
