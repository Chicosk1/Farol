"""Processamento do PDF: leitura por página, divisão em trechos e vetores (MAT-T22, MAT-T20).

Cenários de aceite das Histórias 1 e 3 da spec 002 que dependem do processamento: etapas na ordem,
trechos com aula, arquivo e página de origem, aviso de PDF sem texto e falhas que deixam o
material em "Erro" sem perder o arquivo. A IA é sempre o adaptador falso. Dados fictícios.
"""

from unittest import mock

import pytest
from django.core.files.base import ContentFile

from disciplinas.models import Disciplina
from materiais import servicos, tarefas
from materiais.models import Material, Trecho
from materiais.testes import pdfs


@pytest.fixture(autouse=True)
def arquivos_temporarios(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def disciplina(professor) -> Disciplina:
    return Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )


def material_de(disciplina, conteudo: bytes, aula: int = 4) -> Material:
    material = Material(disciplina=disciplina, aula_numero=aula, aula_titulo="Listas encadeadas")
    material.arquivo.save(f"aula-{aula}.pdf", ContentFile(conteudo), save=False)
    material.save()
    return material


def processar(material: Material) -> Material:
    return servicos.processar_material(material.id)


AULA = [
    "Listas encadeadas\nUma lista encadeada é formada por nós.",
    "Cada nó guarda um valor e um ponteiro para o próximo nó.",
    "Inserir no início da lista custa tempo constante.",
]


@pytest.mark.requisito("MAT-RF-04")
def test_pdf_com_texto_fica_pronto_com_um_trecho_por_pagina_e_a_origem_de_cada_um(disciplina):
    material = processar(material_de(disciplina, pdfs.pdf_com_texto(AULA)))

    assert material.status == Material.Status.PRONTO
    assert material.etapa == Material.Etapa.PRONTO
    assert material.paginas == 3
    assert material.paginas_sem_texto == []
    trechos = list(material.trechos.order_by("pagina", "ordem"))
    assert [(t.pagina, t.ordem) for t in trechos] == [(1, 0), (2, 0), (3, 0)]
    assert "Uma lista encadeada é formada por nós." in trechos[0].texto
    # A aula e o arquivo de origem vêm do material; a página, do próprio trecho.
    assert trechos[1].material.aula_numero == 4
    assert trechos[1].material.arquivo.name.startswith("materiais/aula-4")
    assert all(len(t.vetor) == 256 for t in trechos)


@pytest.mark.requisito("MAT-RF-04")
def test_a_posicao_do_trecho_aponta_para_o_texto_da_pagina(disciplina):
    material = processar(material_de(disciplina, pdfs.pdf_com_texto(AULA)))

    for trecho in material.trechos.all():
        assert trecho.inicio == 0
        assert trecho.fim == len(trecho.texto)


@pytest.mark.requisito("MAT-RF-03")
def test_as_etapas_passam_na_ordem_lendo_dividindo_vetorizando_pronto(disciplina):
    material = material_de(disciplina, pdfs.pdf_com_texto(AULA))
    vistas: list[str] = []

    def etapa_atual() -> str:
        return Material.objects.get(pk=material.pk).etapa

    leitor_real = servicos.PdfReader
    divisor_real = servicos.dividir_em_trechos
    vetorizador_real = servicos.ia.gerar_embeddings

    def ler(*args, **kwargs):
        vistas.append(etapa_atual())
        return leitor_real(*args, **kwargs)

    def dividir(*args, **kwargs):
        vistas.append(etapa_atual())
        return divisor_real(*args, **kwargs)

    def vetorizar(textos):
        vistas.append(etapa_atual())
        return vetorizador_real(textos)

    with (
        mock.patch.object(servicos, "PdfReader", ler),
        mock.patch.object(servicos, "dividir_em_trechos", dividir),
        mock.patch.object(servicos.ia, "gerar_embeddings", vetorizar),
    ):
        processar(material)

    assert vistas[0] == Material.Etapa.LENDO
    assert Material.Etapa.DIVIDINDO in vistas
    assert vistas[-1] == Material.Etapa.VETORIZANDO
    assert vistas.index(Material.Etapa.DIVIDINDO) < vistas.index(Material.Etapa.VETORIZANDO)
    assert Material.objects.get(pk=material.pk).etapa == Material.Etapa.PRONTO


@pytest.mark.requisito("MAT-RF-05")
def test_pdf_escaneado_fica_com_status_precisa_de_atencao_e_sem_trechos(disciplina):
    material = processar(material_de(disciplina, pdfs.pdf_escaneado(5)))

    assert material.status == Material.Status.ATENCAO
    assert material.paginas == 5
    assert material.paginas_sem_texto == [1, 2, 3, 4, 5]
    assert "escaneadas" in material.erro  # a mensagem explica o problema ao professor
    assert Trecho.objects.count() == 0


@pytest.mark.requisito("MAT-RF-05")
def test_pdf_com_algumas_paginas_sem_texto_fica_pronto_e_diz_quais_foram_ignoradas(disciplina):
    conteudo = pdfs.pdf_misto(["Texto da página um", None, "Texto da página três", "Texto quatro"])

    material = processar(material_de(disciplina, conteudo))

    assert material.status == Material.Status.PRONTO
    assert material.paginas_sem_texto == [2]
    assert sorted(material.trechos.values_list("pagina", flat=True)) == [1, 3, 4]


@pytest.mark.requisito("MAT-RF-05")
def test_a_maioria_das_paginas_sem_texto_muda_o_status_para_atencao(disciplina):
    conteudo = pdfs.pdf_misto(["Só esta tem texto", None, None, None])

    material = processar(material_de(disciplina, conteudo))

    assert material.status == Material.Status.ATENCAO
    assert material.paginas_sem_texto == [2, 3, 4]


def test_pdf_protegido_por_senha_fica_com_erro_e_mensagem_clara(disciplina):
    material = processar(material_de(disciplina, pdfs.pdf_protegido(AULA)))

    assert material.status == Material.Status.ERRO
    assert "senha" in material.erro


def test_arquivo_que_nao_e_pdf_fica_com_erro_sem_derrubar_a_tarefa(disciplina):
    material = processar(material_de(disciplina, pdfs.nao_e_pdf()))

    assert material.status == Material.Status.ERRO
    assert material.erro


def test_falha_do_provedor_deixa_erro_sem_trechos_e_sem_perder_o_arquivo(disciplina):
    material = material_de(disciplina, pdfs.pdf_com_texto(AULA))

    with mock.patch.object(servicos.ia, "gerar_embeddings", side_effect=RuntimeError("fora do ar")):
        processado = processar(material)

    assert processado.status == Material.Status.ERRO
    assert "tente de novo" in processado.erro.lower()
    assert Trecho.objects.count() == 0
    processado.arquivo.open("rb")  # o arquivo continua guardado
    processado.arquivo.close()


def test_depois_de_um_erro_reprocessar_conclui_sem_duplicar_trechos(disciplina):
    material = material_de(disciplina, pdfs.pdf_com_texto(AULA))
    with mock.patch.object(servicos.ia, "gerar_embeddings", side_effect=RuntimeError("fora do ar")):
        processar(material)

    refeito = processar(material)
    processar(material)  # e de novo: o resultado é o mesmo

    assert refeito.status == Material.Status.PRONTO
    assert refeito.erro == ""
    assert Trecho.objects.filter(material=material).count() == 3


def test_pagina_com_mais_texto_que_o_limite_gera_varios_trechos_numerados(disciplina):
    texto_longo = " ".join(f"palavra{i}" for i in range(1500))  # bem mais que um trecho

    material = processar(material_de(disciplina, pdfs.pdf_com_texto([texto_longo])))

    ordens = list(material.trechos.order_by("ordem").values_list("ordem", flat=True))
    assert ordens == list(range(len(ordens)))
    assert len(ordens) > 1


def test_trecho_sem_palavras_uteis_e_ignorado_e_o_material_conclui(disciplina):
    conteudo = pdfs.pdf_com_texto(["12", "Uma página com texto de verdade sobre pilhas"])

    material = processar(material_de(disciplina, conteudo))

    assert material.status == Material.Status.PRONTO
    assert list(material.trechos.values_list("pagina", flat=True)) == [2]


def test_a_tarefa_do_celery_so_chama_o_servico_e_devolve_o_status(disciplina):
    material = material_de(disciplina, pdfs.pdf_com_texto(AULA))

    assert tarefas.processar(material.id) == "pronto"
