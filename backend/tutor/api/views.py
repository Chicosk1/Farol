"""Rotas do tutor. Só HTTP: as regras ficam em tutor/servicos.py (ADR 0007)."""

import json

from django.http import StreamingHttpResponse
from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from nucleo.permissoes import acesso_a_disciplina
from tutor import servicos

from .serializers import PerguntaSerializer


def _evento_sse(tipo: str, dados: dict) -> str:
    return f"event: {tipo}\ndata: {json.dumps(dados, ensure_ascii=False)}\n\n"


@extend_schema(
    summary="Pergunta ao tutor da disciplina, com a resposta em streaming",
    description=(
        "Resposta em eventos SSE: inicio {conversa_id}, texto {texto} (aos poucos), citacao "
        "{ordem, rotulo, trecho_id, material_id, pagina}, fim {tipo, mensagem_id} ou erro "
        "{mensagem}. O tipo do fim é resposta, pistas ou nao_encontrado."
    ),
    request=PerguntaSerializer,
    responses={
        (200, "text/event-stream"): OpenApiTypes.STR,
        503: OpenApiResponse(description="O provedor de IA está indisponível."),
    },
    tags=["tutor"],
)
@api_view(["POST"])
@permission_classes([acesso_a_disciplina("aluno")])
def perguntar(request: Request, disciplina_id: int):
    entrada = PerguntaSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    try:
        eventos = servicos.perguntar(request.user, disciplina_id, entrada.validated_data["texto"])
    except servicos.ProvedorIndisponivel:
        return Response(
            {"detail": "O tutor está indisponível agora. Tente de novo em instantes."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    resposta = StreamingHttpResponse(
        (_evento_sse(tipo, dados) for tipo, dados in eventos),
        content_type="text/event-stream; charset=utf-8",
    )
    resposta["Cache-Control"] = "no-cache"
    resposta["X-Accel-Buffering"] = "no"  # o Nginx não segura os eventos
    return resposta
