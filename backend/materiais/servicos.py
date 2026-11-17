"""Regras do módulo materiais (spec 002). Chamado pela API, pelas tarefas e por outros módulos."""

import io
import logging
from dataclasses import dataclass

from celery import current_app
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from pgvector.django import CosineDistance
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from contas.servicos import Perfil
from disciplinas import servicos as disciplinas
from ia import servicos as ia
from notificacoes import servicos as notificacoes

from .models import Material, Trecho
from .trechos import dividir_em_trechos

logger = logging.getLogger(__name__)

TAMANHO_DO_LOTE_DE_VETORES = 64
MENSAGEM_DE_ERRO_GERAL = "Não foi possível processar o material. Tente de novo."
MENSAGEM_SEM_TEXTO = (
    "A maioria das páginas deste PDF não tem texto selecionável, como acontece com páginas "
    "escaneadas. O tutor não consegue ler páginas escaneadas: envie uma versão com texto."
)


MENSAGEM_NAO_E_PDF = "Envie um arquivo PDF. Slides podem ser exportados como PDF."


class MaterialInvalido(ValueError):
    """O envio tem um problema que o professor corrige. `campo` é o campo da API com o erro."""

    def __init__(self, campo: str, mensagem: str):
        super().__init__(mensagem)
        self.campo = campo
        self.mensagem = mensagem


class _ProblemaDoArquivo(Exception):
    """O PDF tem um problema que o professor pode corrigir; a mensagem diz qual."""


def _definir_etapa(material: Material, etapa: str) -> None:
    material.etapa = etapa
    material.save(update_fields=["etapa"])


def _foi_retirado(material: Material) -> bool:
    return Material.objects.filter(pk=material.pk, status=Material.Status.RETIRADO).exists()


def _marcar_erro(material: Material, mensagem: str) -> None:
    material.status = Material.Status.ERRO
    material.erro = mensagem
    material.save(update_fields=["status", "erro"])


def _ler_paginas(material: Material) -> list[str]:
    """O texto de cada página. Levanta _ProblemaDoArquivo para PDF protegido ou ilegível."""
    try:
        with material.arquivo.open("rb") as arquivo:
            leitor = PdfReader(arquivo)
            if leitor.is_encrypted:
                raise _ProblemaDoArquivo("O PDF é protegido por senha. Envie uma versão sem senha.")
            return [(pagina.extract_text() or "").strip() for pagina in leitor.pages]
    except PyPdfError as erro:
        raise _ProblemaDoArquivo("O arquivo não é um PDF válido. Exporte o PDF de novo.") from erro


def _vetorizar(textos: list[str]) -> list[list[float] | None]:
    """Um vetor por texto; None para o texto que o módulo de IA recusa por não ter palavras."""
    vetores: list[list[float] | None] = []
    for inicio in range(0, len(textos), TAMANHO_DO_LOTE_DE_VETORES):
        lote = textos[inicio : inicio + TAMANHO_DO_LOTE_DE_VETORES]
        try:
            vetores.extend(ia.gerar_embeddings(lote))
        except ValueError:
            for texto in lote:
                try:
                    vetores.append(ia.gerar_embeddings([texto])[0])
                except ValueError:
                    vetores.append(None)
    return vetores


def _processar(material: Material) -> None:
    _definir_etapa(material, Material.Etapa.LENDO)
    paginas = _ler_paginas(material)
    sem_texto = [numero for numero, texto in enumerate(paginas, start=1) if not texto]
    material.paginas = len(paginas)
    material.paginas_sem_texto = sem_texto

    if not paginas or len(sem_texto) * 2 > len(paginas):
        material.status = Material.Status.ATENCAO
        material.erro = MENSAGEM_SEM_TEXTO
        material.save(update_fields=["paginas", "paginas_sem_texto", "status", "erro"])
        return

    _definir_etapa(material, Material.Etapa.DIVIDINDO)
    pedacos = [
        (numero, ordem, inicio, fim, texto)
        for numero, texto_da_pagina in enumerate(paginas, start=1)
        for ordem, (inicio, fim, texto) in enumerate(dividir_em_trechos(texto_da_pagina))
    ]

    _definir_etapa(material, Material.Etapa.VETORIZANDO)
    vetores = _vetorizar([texto for *_, texto in pedacos])
    trechos = [
        Trecho(
            material=material,
            pagina=numero,
            ordem=ordem,
            texto=texto,
            inicio=inicio,
            fim=fim,
            vetor=vetor,
        )
        for (numero, ordem, inicio, fim, texto), vetor in zip(pedacos, vetores, strict=True)
        if vetor is not None
    ]
    if not trechos:
        material.status = Material.Status.ATENCAO
        material.erro = MENSAGEM_SEM_TEXTO
        material.save(update_fields=["paginas", "paginas_sem_texto", "status", "erro"])
        return

    # Os trechos entram todos juntos: o material nunca fica pronto com a busca pela metade.
    with transaction.atomic():
        if _foi_retirado(material):
            material.status = Material.Status.RETIRADO  # retirado no meio do processamento
            return
        material.trechos.all().delete()
        Trecho.objects.bulk_create(trechos)
        material.status = Material.Status.PRONTO
        material.etapa = Material.Etapa.PRONTO
        material.erro = ""
        material.save(update_fields=["paginas", "paginas_sem_texto", "status", "etapa", "erro"])


def processar_material(material_id: int) -> Material:
    """Lê o PDF, divide em trechos, gera os vetores e deixa o material pronto (MAT-RF-03 e 04).

    Problema do arquivo ou falha do provedor não derrubam a tarefa: o material fica com o status
    certo e a mensagem para o professor, sem perder o arquivo, e pode ser processado de novo.
    """
    material = Material.objects.get(pk=material_id)
    if material.status == Material.Status.RETIRADO:
        return material  # o professor retirou: não há o que processar
    material.status = Material.Status.PROCESSANDO
    material.erro = ""
    material.save(update_fields=["status", "erro"])
    try:
        _processar(material)
    except _ProblemaDoArquivo as problema:
        _marcar_erro(material, str(problema))
    except Exception:
        logger.exception("Falha ao processar o material %s", material_id)
        _marcar_erro(material, MENSAGEM_DE_ERRO_GERAL)
    _avisar_professor(material)
    return material


def _avisar_professor(material: Material) -> None:
    """O aviso no sino de quem enviou: pronto, precisa de atenção ou erro (MAT-RF-06)."""
    aula = f"Aula {material.aula_numero}, {material.aula_titulo},"
    avisos = {
        Material.Status.PRONTO: (
            notificacoes.Tipo.MATERIAL_PRONTO,
            f"{aula} está pronta para o tutor.",
        ),
        Material.Status.ATENCAO: (
            notificacoes.Tipo.MATERIAL_ATENCAO,
            f"{aula} precisa de atenção: {material.erro}",
        ),
        Material.Status.ERRO: (
            notificacoes.Tipo.MATERIAL_ERRO,
            f"{aula} não pôde ser processada. {material.erro}",
        ),
    }
    if material.status not in avisos or material.enviado_por_id is None:
        return
    tipo, texto = avisos[material.status]
    notificacoes.notificar(
        material.enviado_por, tipo, texto, link=f"/disciplinas/{material.disciplina_id}/materiais"
    )


def _validar_pdf(conteudo: bytes, nome: str) -> None:
    """Confere se o arquivo é um PDF aberto, legível e dentro dos limites (MAT-RF-01)."""
    if not nome.lower().endswith(".pdf") or b"%PDF-" not in conteudo[:1024]:
        raise MaterialInvalido("arquivo", MENSAGEM_NAO_E_PDF)
    limite_em_bytes = settings.FAROL_PDF_MAX_BYTES
    if len(conteudo) > limite_em_bytes:
        raise MaterialInvalido(
            "arquivo", f"O arquivo passa do limite de {limite_em_bytes // (1024 * 1024)} MB."
        )
    try:
        leitor = PdfReader(io.BytesIO(conteudo))
        if leitor.is_encrypted:
            raise MaterialInvalido(
                "arquivo", "O PDF é protegido por senha. Envie uma versão sem senha."
            )
        paginas = len(leitor.pages)
    except PyPdfError:
        raise MaterialInvalido(
            "arquivo", "O arquivo não é um PDF válido. Exporte o PDF de novo."
        ) from None
    if paginas > settings.FAROL_PDF_MAX_PAGINAS:
        raise MaterialInvalido(
            "arquivo", f"O PDF passa do limite de {settings.FAROL_PDF_MAX_PAGINAS} páginas."
        )


def criar_material(
    disciplina_id: int,
    conteudo: bytes,
    nome_do_arquivo: str,
    aula_numero: int,
    aula_titulo: str,
    enviado_por,
) -> Material:
    """Valida o PDF e cria o material da aula, ainda sem processar (MAT-RF-01 e 02).

    Levanta MaterialInvalido, sem guardar nada, se o arquivo não pode ser aceito.
    """
    _validar_pdf(conteudo, nome_do_arquivo)
    material = Material(
        disciplina_id=disciplina_id,
        aula_numero=aula_numero,
        aula_titulo=aula_titulo,
        enviado_por=enviado_por,
    )
    material.arquivo.save(nome_do_arquivo, ContentFile(conteudo), save=False)
    material.save()
    return material


def enfileirar_processamento(material_id: int) -> None:
    """Põe o processamento do material na fila do Celery.

    A tarefa é chamada pelo nome, porque a camada de serviços não importa a de tarefas.
    """
    current_app.signature("materiais.processar", args=(material_id,)).apply_async()


class MaterialNaoEncontrado(LookupError):
    """O material não existe, ou o aluno não deve saber que ele existe (ainda não está pronto)."""


class SemAcessoAoMaterial(PermissionError):
    """A pessoa não tem acesso à disciplina do material."""


def ve_todos_os_materiais(perfil: str | None) -> bool:
    """O professor e a administração veem todos os materiais, em qualquer status."""
    return perfil in (Perfil.PROFESSOR, Perfil.ADMIN)


def listar_materiais(perfil: str | None, disciplina_id: int):
    """Os materiais da disciplina, por aula. O aluno só vê os prontos (MAT-RF-07 e 08)."""
    materiais = Material.objects.filter(disciplina_id=disciplina_id)
    if not ve_todos_os_materiais(perfil):
        materiais = materiais.filter(status=Material.Status.PRONTO)
    return materiais.order_by("aula_numero", "id")


def material_para_abrir(pessoa, perfil: str | None, material_id: int) -> Material:
    """O material, se a pessoa pode abrir o PDF dele. Levanta MaterialNaoEncontrado ou
    SemAcessoAoMaterial."""
    try:
        material = Material.objects.get(pk=material_id)
    except Material.DoesNotExist:
        raise MaterialNaoEncontrado(material_id) from None
    if not disciplinas.tem_acesso(pessoa, perfil, material.disciplina_id):
        raise SemAcessoAoMaterial(material_id)
    if not ve_todos_os_materiais(perfil) and material.status != Material.Status.PRONTO:
        raise MaterialNaoEncontrado(material_id)
    return material


def disciplinas_com_material_pronto() -> set[int]:
    """Os ids das disciplinas que têm pelo menos um material pronto para o tutor."""
    return set(
        Material.objects.filter(status=Material.Status.PRONTO)
        .values_list("disciplina_id", flat=True)
        .distinct()
    )


def retirar_material(pessoa, perfil: str | None, material_id: int) -> Material:
    """Retira o material: some da lista do aluno e deixa de ser usado pelo tutor (MAT-RF-10).

    Só o professor da disciplina e a administração retiram (MAT-RNF-02). O arquivo e os trechos
    ficam guardados; retirar de novo não muda nada.
    """
    try:
        material = Material.objects.get(pk=material_id)
    except Material.DoesNotExist:
        raise MaterialNaoEncontrado(material_id) from None
    pode = ve_todos_os_materiais(perfil) and disciplinas.tem_acesso(
        pessoa, perfil, material.disciplina_id
    )
    if not pode:
        raise SemAcessoAoMaterial(material_id)
    if material.status != Material.Status.RETIRADO:
        material.status = Material.Status.RETIRADO
        material.save(update_fields=["status"])
    return material


@dataclass(frozen=True)
class TrechoEncontrado:
    """Um trecho achado pela busca, com a origem que vira a citação (aula e página)."""

    id: int
    material_id: int
    aula_numero: int
    pagina: int
    texto: str
    similaridade: float  # de 0 a 1; quanto maior, mais parecido com a pergunta


def buscar_trechos(
    disciplina_id: int, vetor: list[float], limite: int = 6
) -> list[TrechoEncontrado]:
    """Os `limite` trechos mais próximos do vetor, só da disciplina e só de material pronto.

    Material em processamento, com erro, que precisa de atenção ou retirado nunca entra: o
    professor é o dono do conteúdo (princípio I) e a retirada vale já na pergunta seguinte
    (MAT-RF-10, MAT-CS-03). Quem decide se a similaridade basta é quem chama.
    """
    achados = (
        Trecho.objects.filter(
            material__disciplina_id=disciplina_id, material__status=Material.Status.PRONTO
        )
        .annotate(distancia=CosineDistance("vetor", vetor))
        .select_related("material")
        .order_by("distancia", "id")[:limite]
    )
    return [
        TrechoEncontrado(
            id=t.id,
            material_id=t.material_id,
            aula_numero=t.material.aula_numero,
            pagina=t.pagina,
            texto=t.texto,
            similaridade=1.0 - float(t.distancia),
        )
        for t in achados
    ]
