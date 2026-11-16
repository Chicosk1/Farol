"""Rotas de disciplinas. Só HTTP: as regras ficam em disciplinas/servicos.py (ADR 0007)."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contas import servicos as contas
from disciplinas import servicos
from disciplinas.models import Importacao
from materiais import servicos as materiais
from nucleo.permissoes import AcessoADisciplina, exige_perfil_ativo

from .serializers import (
    ConsultaDeDisciplinasSerializer,
    DisciplinaSerializer,
    EnvioDeImportacaoSerializer,
    ImportacaoCriadaSerializer,
    ImportacaoSerializer,
)


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
        com_material_pronto=(
            materiais.disciplinas_com_material_pronto()
            if consulta.validated_data["filtro"] == "com-tutor"
            else None
        ),
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


@extend_schema(
    summary="Envia um CSV de turmas e matrículas (só administrador)",
    request={"multipart/form-data": EnvioDeImportacaoSerializer},
    responses={202: ImportacaoCriadaSerializer},
    tags=["importacoes"],
)
@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([exige_perfil_ativo("admin")])
def enviar_importacao(request: Request) -> Response:
    """Guarda o arquivo e põe o processamento na fila. O relatório sai em GET /importacoes/{id}."""
    entrada = EnvioDeImportacaoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    arquivo = entrada.validated_data["arquivo"]
    importacao = servicos.criar_importacao(arquivo.read(), arquivo.name, request.user)
    servicos.enfileirar_importacao(importacao.id)
    importacao.refresh_from_db()
    return Response(
        ImportacaoCriadaSerializer({"id": importacao.id, "status": importacao.status}).data,
        status=status.HTTP_202_ACCEPTED,
    )


@extend_schema(
    summary="Relatório de uma importação (só administrador)",
    responses=ImportacaoSerializer,
    tags=["importacoes"],
)
@api_view(["GET"])
@permission_classes([exige_perfil_ativo("admin")])
def ver_importacao(request: Request, importacao_id: int) -> Response:
    importacao = get_object_or_404(Importacao, pk=importacao_id)
    return Response(ImportacaoSerializer(importacao).data)
