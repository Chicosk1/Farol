"""Rotas de questões. Só HTTP: as regras ficam em questoes/servicos.py (ADR 0007)."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contas import servicos as contas
from nucleo.permissoes import acesso_a_disciplina, exige_perfil_ativo
from questoes import servicos

from .serializers import (
    FiltroDeQuestoesSerializer,
    GeracaoSerializer,
    MudancaDeQuestaoSerializer,
    PedidoDeGeracaoSerializer,
    QuestaoDoProfessorSerializer,
    QuestoesDaDisciplinaSerializer,
    QuizDaAulaSerializer,
    QuizSerializer,
    RespostaDoAlunoSerializer,
    RetornoDaQuestaoSerializer,
)

MENSAGEM_AULA_NAO_PRONTA = (
    "Esta aula ainda não está pronta. Espere o processamento do PDF terminar para gerar questões."
)


@extend_schema(
    summary="Pede rascunhos de questões de uma aula",
    description=(
        "Só o professor da disciplina. A geração roda em segundo plano: acompanhe pelo id do "
        "pedido. Se já há um pedido em andamento para a aula, devolve esse (QUE-RF-01)."
    ),
    request=PedidoDeGeracaoSerializer,
    responses={202: GeracaoSerializer},
    tags=["questoes"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pedir(request: Request, material_id: int) -> Response:
    entrada = PedidoDeGeracaoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        pedido = servicos.pedir_geracao(
            request.user, perfil, material_id, entrada.validated_data["quantidade"]
        )
    except servicos.NaoEncontrado:
        raise Http404 from None
    except servicos.SemAcesso:
        raise PermissionDenied from None
    except servicos.AulaNaoPronta:
        return Response({"detail": MENSAGEM_AULA_NAO_PRONTA}, status=status.HTTP_409_CONFLICT)
    if pedido.status == pedido.Status.PROCESSANDO:
        servicos.enfileirar_geracao(pedido.id)
        pedido.refresh_from_db()
    return Response(GeracaoSerializer(pedido).data, status=status.HTTP_202_ACCEPTED)


@extend_schema(
    summary="Andamento de um pedido de rascunhos",
    responses=GeracaoSerializer,
    tags=["questoes"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def geracao(request: Request, pedido_id: int) -> Response:
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        pedido = servicos.pedido_para_ver(request.user, perfil, pedido_id)
    except servicos.NaoEncontrado:
        raise Http404 from None
    except servicos.SemAcesso:
        raise PermissionDenied from None
    return Response(GeracaoSerializer(pedido).data)


@extend_schema(
    summary="Questões da disciplina por status, com as contagens",
    description="Só o professor da disciplina: inclui rascunhos e o gabarito (QUE-RF-04 e 06).",
    parameters=[FiltroDeQuestoesSerializer],
    responses=QuestoesDaDisciplinaSerializer,
    tags=["questoes"],
)
@api_view(["GET"])
@permission_classes([acesso_a_disciplina("professor")])
def da_disciplina(request: Request, disciplina_id: int) -> Response:
    filtro = FiltroDeQuestoesSerializer(data=request.query_params)
    filtro.is_valid(raise_exception=True)
    contagens, questoes = servicos.questoes_da_disciplina(
        disciplina_id, filtro.validated_data["status"], filtro.validated_data.get("material")
    )
    dados = {"contagens": contagens, "questoes": questoes}
    return Response(QuestoesDaDisciplinaSerializer(dados).data)


@extend_schema(
    summary="Edita, aprova, descarta ou devolve uma questão para pendentes",
    description=(
        "A edição só vale em pendentes (409 fora delas). Publicar só a partir de pendentes, e "
        "nunca uma questão cujo material foi retirado (QUE-RF-05)."
    ),
    request=MudancaDeQuestaoSerializer,
    responses=QuestaoDoProfessorSerializer,
    tags=["questoes"],
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def mudar(request: Request, questao_id: int) -> Response:
    entrada = MudancaDeQuestaoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        questao = servicos.mudar_questao(request.user, perfil, questao_id, entrada.validated_data)
    except servicos.NaoEncontrado:
        raise Http404 from None
    except servicos.SemAcesso:
        raise PermissionDenied from None
    except servicos.QuestaoInvalida as invalida:
        erros = {campo: [mensagem] for campo, mensagem in invalida.erros.items()}
        return Response(erros, status=status.HTTP_400_BAD_REQUEST)
    except servicos.MudancaNaoPermitida as recusa:
        return Response({"detail": recusa.mensagem}, status=status.HTTP_409_CONFLICT)
    return Response(QuestaoDoProfessorSerializer(questao).data)


MENSAGEM_PAUSADO = "O professor pausou o tutor e os quizzes desta disciplina durante a prova."


@extend_schema(
    summary="Quiz de uma aula para o aluno",
    description="Só as questões publicadas, sem o gabarito das que faltam responder (QUE-RF-04).",
    responses=QuizSerializer,
    tags=["questoes"],
)
@api_view(["GET"])
@permission_classes([exige_perfil_ativo("aluno")])
def quiz(request: Request, material_id: int) -> Response:
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        dados = servicos.quiz_da_aula(request.user, perfil, material_id)
    except servicos.NaoEncontrado:
        raise Http404 from None
    except servicos.SemAcesso:
        raise PermissionDenied from None
    return Response(QuizSerializer(dados).data)


@extend_schema(
    summary="Começa o quiz da aula de novo",
    request=None,
    responses={204: None},
    tags=["questoes"],
)
@api_view(["POST"])
@permission_classes([exige_perfil_ativo("aluno")])
def reiniciar(request: Request, material_id: int) -> Response:
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        servicos.reiniciar_quiz(request.user, perfil, material_id)
    except servicos.NaoEncontrado:
        raise Http404 from None
    except servicos.SemAcesso:
        raise PermissionDenied from None
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Responde a uma questão do quiz",
    description="Devolve o acerto, a correta, a justificativa e o trecho (QUE-RF-08 e 11).",
    request=RespostaDoAlunoSerializer,
    responses=RetornoDaQuestaoSerializer,
    tags=["questoes"],
)
@api_view(["POST"])
@permission_classes([exige_perfil_ativo("aluno")])
def responder(request: Request, questao_id: int) -> Response:
    entrada = RespostaDoAlunoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        retorno = servicos.responder_questao(
            request.user, perfil, questao_id, entrada.validated_data["alternativa"]
        )
    except servicos.NaoEncontrado:
        raise Http404 from None
    except servicos.SemAcesso:
        raise PermissionDenied from None
    except servicos.QuizPausado:
        return Response({"detail": MENSAGEM_PAUSADO}, status=status.HTTP_409_CONFLICT)
    return Response(RetornoDaQuestaoSerializer(retorno).data)


@extend_schema(
    summary="Quizzes da disciplina, com o andamento do aluno",
    responses=QuizDaAulaSerializer(many=True),
    tags=["questoes"],
)
@api_view(["GET"])
@permission_classes([acesso_a_disciplina("aluno")])
def quizzes(request: Request, disciplina_id: int) -> Response:
    dados = servicos.quizzes_da_disciplina(request.user, disciplina_id)
    return Response(QuizDaAulaSerializer(dados, many=True).data)
