"""Rotas de materiais. Só HTTP: as regras ficam em materiais/servicos.py (ADR 0007)."""

from django.http import FileResponse, Http404
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from contas import servicos as contas
from materiais import servicos
from nucleo.permissoes import AcessoADisciplina, acesso_a_disciplina

from .serializers import (
    EnvioDeMaterialSerializer,
    MaterialDoAlunoSerializer,
    MaterialDoProfessorSerializer,
    MaterialEnviadoSerializer,
    NovaVersaoSerializer,
    PaginaDoPdfSerializer,
    TrechoParaAbrirSerializer,
)


class MateriaisDaDisciplina(APIView):
    """Os materiais de uma disciplina: lista para quem tem acesso, envio para o professor."""

    parser_classes = [MultiPartParser]
    permission_classes = [AcessoADisciplina]

    def get_permissions(self):
        if self.request.method == "POST":
            return [acesso_a_disciplina("professor", "admin")()]
        return super().get_permissions()

    @extend_schema(
        summary="Materiais da disciplina",
        description=(
            "O professor e a administração veem todos, com status, etapa e avisos; o aluno vê só "
            "os prontos, apenas com id, aula, título e páginas."
        ),
        responses=MaterialDoProfessorSerializer(many=True),
        tags=["materiais"],
    )
    def get(self, request: Request, disciplina_id: int) -> Response:
        perfil = contas.perfil_ativo(request.user, request.session)
        materiais = servicos.listar_materiais(perfil, disciplina_id)
        serializador = (
            MaterialDoProfessorSerializer
            if servicos.ve_todos_os_materiais(perfil)
            else MaterialDoAlunoSerializer
        )
        return Response(serializador(materiais, many=True).data)

    @extend_schema(
        summary="Envia o PDF de uma aula da disciplina",
        request={"multipart/form-data": EnvioDeMaterialSerializer},
        responses={202: MaterialEnviadoSerializer},
        tags=["materiais"],
    )
    def post(self, request: Request, disciplina_id: int) -> Response:
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
            return Response(
                {invalido.campo: [invalido.mensagem]}, status=status.HTTP_400_BAD_REQUEST
            )
        servicos.enfileirar_processamento(material.id)
        material.refresh_from_db()
        return Response(
            MaterialEnviadoSerializer({"material_id": material.id, "status": material.status}).data,
            status=status.HTTP_202_ACCEPTED,
        )


@extend_schema(
    summary="Abre o PDF de um material",
    description=(
        "Serve o arquivo só para quem tem acesso à disciplina. O aluno só abre material pronto. "
        "O parâmetro pagina é validado; o visualizador abre nessa página (MAT-RF-09)."
    ),
    parameters=[PaginaDoPdfSerializer],
    responses={(200, "application/pdf"): OpenApiTypes.BINARY},
    tags=["materiais"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def arquivo(request: Request, material_id: int) -> FileResponse:
    consulta = PaginaDoPdfSerializer(data=request.query_params)
    consulta.is_valid(raise_exception=True)
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        material = servicos.material_para_abrir(request.user, perfil, material_id)
    except servicos.MaterialNaoEncontrado:
        raise Http404 from None
    except servicos.SemAcessoAoMaterial:
        raise PermissionDenied from None
    resposta = FileResponse(
        material.arquivo.open("rb"),
        content_type="application/pdf",
        as_attachment=False,
        filename=f"aula-{material.aula_numero}.pdf",
    )
    # Quando a citação é de uma versão substituída, diz qual versão foi aberta.
    resposta["X-Farol-Material"] = str(material.id)
    # O PDF é de uma disciplina: nunca fica em cache compartilhado.
    resposta["Cache-Control"] = "private, max-age=0, must-revalidate"
    return resposta


@extend_schema(summary="Retira um material", responses={204: None}, tags=["materiais"])
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def retirar(request: Request, material_id: int) -> Response:
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        servicos.retirar_material(request.user, perfil, material_id)
    except servicos.MaterialNaoEncontrado:
        raise Http404 from None
    except servicos.SemAcessoAoMaterial:
        raise PermissionDenied from None
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Envia a versão nova de um material",
    description="A versão anterior continua em uso até a nova ficar pronta (MAT-RF-11).",
    request={"multipart/form-data": NovaVersaoSerializer},
    responses={202: MaterialEnviadoSerializer},
    tags=["materiais"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def nova_versao(request: Request, material_id: int) -> Response:
    entrada = NovaVersaoSerializer(data=request.data)
    entrada.is_valid(raise_exception=True)
    arquivo = entrada.validated_data["arquivo"]
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        nova = servicos.criar_nova_versao(
            request.user, perfil, material_id, arquivo.read(), arquivo.name
        )
    except servicos.MaterialNaoEncontrado:
        raise Http404 from None
    except servicos.SemAcessoAoMaterial:
        raise PermissionDenied from None
    except servicos.MaterialInvalido as invalido:
        return Response({invalido.campo: [invalido.mensagem]}, status=status.HTTP_400_BAD_REQUEST)
    servicos.enfileirar_processamento(nova.id)
    nova.refresh_from_db()
    dados = {"material_id": nova.id, "status": nova.status}
    return Response(MaterialEnviadoSerializer(dados).data, status=status.HTTP_202_ACCEPTED)


@extend_schema(
    summary="A página citada com a posição do trecho, para destacar",
    responses=TrechoParaAbrirSerializer,
    tags=["materiais"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trecho(request: Request, trecho_id: int) -> Response:
    perfil = contas.perfil_ativo(request.user, request.session)
    try:
        dados = servicos.trecho_para_abrir(request.user, perfil, trecho_id)
    except servicos.MaterialNaoEncontrado:
        raise Http404 from None
    except servicos.SemAcessoAoMaterial:
        raise PermissionDenied from None
    return Response(TrechoParaAbrirSerializer(dados).data)
