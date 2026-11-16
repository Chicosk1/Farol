"""Rotas de materiais. Só HTTP: as regras ficam em materiais/servicos.py (ADR 0007)."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from materiais import servicos
from nucleo.permissoes import acesso_a_disciplina

from .serializers import EnvioDeMaterialSerializer, MaterialEnviadoSerializer


@extend_schema(
    summary="Envia o PDF de uma aula da disciplina",
    request={"multipart/form-data": EnvioDeMaterialSerializer},
    responses={202: MaterialEnviadoSerializer},
    tags=["materiais"],
)
@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([acesso_a_disciplina("professor", "admin")])
def enviar(request: Request, disciplina_id: int) -> Response:
    """Guarda o PDF, cria o material e põe o processamento na fila (MAT-RF-01 a 03)."""
    entrada = EnvioDeMaterialSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    dados = entrada.validated_data
    arquivo = dados["arquivo"]
    try:
        material = servicos.criar_material(
            disciplina_id,
            arquivo.read(),
            arquivo.name,
            dados["aula_numero"],
            dados["aula_titulo"].strip(),
            request.user,
        )
    except servicos.MaterialInvalido as invalido:
        return Response({invalido.campo: [invalido.mensagem]}, status=status.HTTP_400_BAD_REQUEST)
    servicos.enfileirar_processamento(material.id)
    material.refresh_from_db()
    return Response(
        MaterialEnviadoSerializer({"material_id": material.id, "status": material.status}).data,
        status=status.HTTP_202_ACCEPTED,
    )
