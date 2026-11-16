"""Regras do módulo materiais (spec 002). Chamado pela API, pelas tarefas e por outros módulos."""

import logging

from django.db import transaction
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from ia import servicos as ia

from .models import Material, Trecho
from .trechos import dividir_em_trechos

logger = logging.getLogger(__name__)

TAMANHO_DO_LOTE_DE_VETORES = 64
MENSAGEM_DE_ERRO_GERAL = "Não foi possível processar o material. Tente de novo."
MENSAGEM_SEM_TEXTO = (
    "A maioria das páginas deste PDF não tem texto selecionável, como acontece com páginas "
    "escaneadas. O tutor não consegue ler páginas escaneadas: envie uma versão com texto."
)


class _ProblemaDoArquivo(Exception):
    """O PDF tem um problema que o professor pode corrigir; a mensagem diz qual."""


def _definir_etapa(material: Material, etapa: str) -> None:
    material.etapa = etapa
    material.save(update_fields=["etapa"])


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
    return material
