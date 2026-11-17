"""Rotas do tutor. Só HTTP: as regras ficam em tutor/servicos.py (ADR 0007)."""

import json

from django.http import Http404, StreamingHttpResponse
from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nucleo.permissoes import acesso_a_disciplina
from tutor import servicos

from .serializers import (
    ConfiguracaoSerializer,
    EstadoDoTutorSerializer,
    JanelaSerializer,
    NovaJanelaSerializer,
    PerguntaSerializer,
)

PAUSADO = "O tutor está pausado durante a prova."


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
        423: OpenApiResponse(description="O tutor está pausado durante a prova."),
        429: OpenApiResponse(description="O aluno chegou ao limite de perguntas de hoje."),
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
    except servicos.TutorPausado:
        return Response({"detail": PAUSADO}, status=status.HTTP_423_LOCKED)
    except servicos.LimiteAtingido as atingido:
        return Response(
            {
                "detail": f"Você chegou ao limite de {atingido.limite} perguntas de hoje. "
                "O limite volta amanhã."
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
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


class JanelasDeProva(APIView):
    """As janelas de prova da disciplina, só para o professor dela (TUT-RF-07)."""

    permission_classes = [acesso_a_disciplina("professor")]

    @extend_schema(
        summary="Janelas de prova em andamento e agendadas",
        responses=JanelaSerializer(many=True),
        tags=["tutor"],
    )
    def get(self, request: Request, disciplina_id: int) -> Response:
        janelas = servicos.janelas_atuais_e_futuras(disciplina_id)
        return Response(JanelaSerializer(janelas, many=True).data)

    @extend_schema(
        summary="Liga o modo prova agora ou agenda uma janela de prova",
        description="Sem início, a janela começa agora; sem fim, fica aberta até ser apagada.",
        request=NovaJanelaSerializer,
        responses={201: JanelaSerializer},
        tags=["tutor"],
    )
    def post(self, request: Request, disciplina_id: int) -> Response:
        entrada = NovaJanelaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        janela = servicos.criar_janela(disciplina_id, request.user, **entrada.validated_data)
        return Response(JanelaSerializer(janela).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Apaga uma janela de prova (desliga o modo prova)",
    responses={204: None},
    tags=["tutor"],
)
@api_view(["DELETE"])
@permission_classes([acesso_a_disciplina("professor")])
def apagar_janela(request: Request, disciplina_id: int, janela_id: int) -> Response:
    if not servicos.apagar_janela(disciplina_id, janela_id):
        raise Http404
    return Response(status=status.HTTP_204_NO_CONTENT)


class ConfiguracaoDoTutor(APIView):
    """O que o professor controla no tutor da disciplina (TUT-RF-06, TUT-RF-08 e TUT-RF-10)."""

    permission_classes = [acesso_a_disciplina("professor")]

    @extend_schema(
        summary="Configuração do tutor da disciplina",
        responses=ConfiguracaoSerializer,
        tags=["tutor"],
    )
    def get(self, request: Request, disciplina_id: int) -> Response:
        configuracao = servicos.configuracao_do_tutor(disciplina_id)
        return Response(ConfiguracaoSerializer(configuracao).data)

    @extend_schema(
        summary="Muda o modo pistas, o limite diário ou a política de uso de IA",
        description="Só os campos enviados mudam. O limite aceita 20, 40 ou 60 perguntas por dia.",
        request=ConfiguracaoSerializer(partial=True),
        responses=ConfiguracaoSerializer,
        tags=["tutor"],
    )
    def patch(self, request: Request, disciplina_id: int) -> Response:
        entrada = ConfiguracaoSerializer(data=request.data, partial=True)
        entrada.is_valid(raise_exception=True)
        configuracao = servicos.atualizar_configuracao(disciplina_id, **entrada.validated_data)
        return Response(ConfiguracaoSerializer(configuracao).data)


@extend_schema(
    summary="O tutor da disciplina para o aluno: regras, pausa, uso do dia e conversa",
    responses=EstadoDoTutorSerializer,
    tags=["tutor"],
)
@api_view(["GET"])
@permission_classes([acesso_a_disciplina("aluno")])
def estado(request: Request, disciplina_id: int) -> Response:
    dados = servicos.estado_do_tutor(request.user, disciplina_id)
    return Response(EstadoDoTutorSerializer(dados).data)
