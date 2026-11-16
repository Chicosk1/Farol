"""Rotas do núcleo. Só HTTP: nenhuma regra de negócio (ADR 0007)."""

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import SaudeSerializer


@extend_schema(summary="Saúde da API", responses=SaudeSerializer, tags=["nucleo"])
@api_view(["GET"])
@permission_classes([AllowAny])
def saude(request: Request) -> Response:
    """Diz que a API está no ar. Usada pelo Docker Compose e pelo monitoramento; não exige login."""
    return Response(SaudeSerializer({"status": "ok"}).data)
