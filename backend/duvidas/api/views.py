"""Rotas das dúvidas. Só HTTP: as regras ficam em duvidas/servicos.py (ADR 0007)."""

from django.http import Http404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from duvidas import servicos
from nucleo.permissoes import acesso_a_disciplina, exige_perfil_ativo

from .serializers import DuvidaDoProfessorSerializer, DuvidaEnviadaSerializer, PreviaSerializer

JA_ENVIADA = "Esta dúvida já foi enviada ao professor."


def _recusa(erro: Exception) -> Response:
    if isinstance(erro, servicos.MensagemNaoEncontrada):
        raise Http404 from None
    if isinstance(erro, servicos.NaoPodeVirarDuvida):
        return Response({"detail": str(erro)}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(erro, servicos.DuvidaJaEnviada):
        return Response({"detail": JA_ENVIADA}, status=status.HTTP_409_CONFLICT)
    return Response(
        {
            "detail": f"Você já enviou {servicos.LIMITE_POR_DIA} dúvidas hoje nesta disciplina. "
            "Tente de novo amanhã."
        },
        status=status.HTTP_429_TOO_MANY_REQUESTS,
    )


RECUSAS = (
    servicos.MensagemNaoEncontrada,
    servicos.NaoPodeVirarDuvida,
    servicos.DuvidaJaEnviada,
    servicos.LimiteDeDuvidas,
)


@extend_schema(
    summary="Mostra o texto que vai ao professor, já sem dados pessoais",
    request=None,
    responses={
        200: PreviaSerializer,
        400: OpenApiResponse(description='A mensagem não é uma resposta "não encontrei".'),
        409: OpenApiResponse(description="A dúvida já foi enviada."),
    },
    tags=["duvidas"],
)
@api_view(["POST"])
@permission_classes([exige_perfil_ativo("aluno")])
def previa(request: Request, mensagem_id: int) -> Response:
    try:
        texto = servicos.previa(request.user, mensagem_id)
    except RECUSAS as erro:
        return _recusa(erro)
    return Response(PreviaSerializer({"texto_filtrado": texto}).data)


@extend_schema(
    summary="Envia a dúvida ao professor, sem o nome do aluno",
    request=None,
    responses={
        201: DuvidaEnviadaSerializer,
        400: OpenApiResponse(description='A mensagem não é uma resposta "não encontrei".'),
        409: OpenApiResponse(description="A dúvida já foi enviada."),
        429: OpenApiResponse(description="O aluno já enviou 5 dúvidas hoje nesta disciplina."),
    },
    tags=["duvidas"],
)
@api_view(["POST"])
@permission_classes([exige_perfil_ativo("aluno")])
def enviar(request: Request, mensagem_id: int) -> Response:
    try:
        duvida = servicos.enviar(request.user, mensagem_id)
    except RECUSAS as erro:
        return _recusa(erro)
    dados = {"duvida_id": duvida.id, "status": duvida.status}
    return Response(DuvidaEnviadaSerializer(dados).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="As dúvidas da disciplina para o professor, sem dados do aluno",
    parameters=[
        OpenApiParameter("status", str, enum=["aberta", "respondida"], description="Padrão: aberta")
    ],
    responses=DuvidaDoProfessorSerializer(many=True),
    tags=["duvidas"],
)
@api_view(["GET"])
@permission_classes([acesso_a_disciplina("professor")])
def da_disciplina(request: Request, disciplina_id: int) -> Response:
    try:
        lista = servicos.duvidas_para_o_professor(
            disciplina_id, request.query_params.get("status", "aberta")
        )
    except servicos.StatusInvalido:
        return Response(
            {"status": ["Use aberta ou respondida."]}, status=status.HTTP_400_BAD_REQUEST
        )
    return Response(DuvidaDoProfessorSerializer(lista, many=True).data)
