"""POST /api/disciplinas/{id}/materiais: o professor publica o PDF de uma aula (MAT-T21, MAT-T20).

Cenários de aceite da História 1 da spec 002 (envio, aula e arquivo que não é PDF) e as bordas do
arquivo: protegido por senha, corrompido, grande demais. Só o professor da disciplina e a
administração enviam (MAT-RNF-02). A IA é o adaptador falso. Dados fictícios.
"""

from unittest import mock

import pytest
from celery.canvas import Signature
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from materiais.models import Material, Trecho
from materiais.testes import pdfs

MENSAGEM_NAO_E_PDF = "Envie um arquivo PDF. Slides podem ser exportados como PDF."
AULA = [
    "Listas encadeadas\nUma lista encadeada é formada por nós.",
    "Cada nó aponta para o próximo.",
]


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


def url(disciplina: Disciplina) -> str:
    return f"/api/disciplinas/{disciplina.id}/materiais"


def pdf_enviado(conteudo: bytes | None = None, nome: str = "aula-4.pdf") -> SimpleUploadedFile:
    return SimpleUploadedFile(
        nome, conteudo if conteudo is not None else pdfs.pdf_com_texto(AULA), "application/pdf"
    )


def enviar(cliente, disciplina, arquivo=None, **campos):
    dados = {"arquivo": arquivo or pdf_enviado(), "aula_numero": 4, "aula_titulo": "Listas"}
    dados.update(campos)
    return cliente.post(url(disciplina), dados, format="multipart")


@pytest.mark.requisito("MAT-RF-02")
def test_professor_envia_o_pdf_com_a_aula_e_recebe_202_com_o_id_do_material(
    cliente_professor, disciplina, professor
):
    resposta = enviar(cliente_professor, disciplina)

    assert resposta.status_code == 202
    corpo = resposta.json()
    assert set(corpo) == {"material_id", "status"}
    material = Material.objects.get(pk=corpo["material_id"])
    assert (material.disciplina, material.aula_numero, material.aula_titulo) == (
        disciplina,
        4,
        "Listas",
    )
    assert material.enviado_por == professor
    assert material.arquivo.name.startswith("materiais/aula-4")


@pytest.mark.requisito("MAT-RF-03")
def test_o_envio_dispara_o_processamento_e_o_material_chega_a_pronto(cliente_professor, disciplina):
    # Nos testes, o Celery roda na hora: depois do envio o material já está processado.
    material_id = enviar(cliente_professor, disciplina).json()["material_id"]

    material = Material.objects.get(pk=material_id)
    assert material.status == Material.Status.PRONTO
    assert Trecho.objects.filter(material=material).count() == 2


@pytest.mark.requisito("MAT-RF-03")
def test_o_processamento_vai_para_a_fila_do_celery_pelo_nome_da_tarefa(
    cliente_professor, disciplina
):
    with mock.patch.object(Signature, "apply_async", autospec=True) as enfileirar:
        material_id = enviar(cliente_professor, disciplina).json()["material_id"]

    enfileirar.assert_called_once()
    assinatura = enfileirar.call_args.args[0]
    assert (assinatura.task, assinatura.args) == ("materiais.processar", (material_id,))
    assert Material.objects.get(pk=material_id).status == Material.Status.PROCESSANDO


@pytest.mark.requisito("MAT-RF-01")
@pytest.mark.parametrize(
    ("nome", "conteudo"),
    [
        ("planilha.xlsx", pdfs.nao_e_pdf()),
        ("slides.pptx", b"PK\x03\x04 qualquer coisa"),
        ("aula.pdf", pdfs.nao_e_pdf()),  # extensão de PDF, mas o conteúdo não é
        ("aula.txt", pdfs.pdf_com_texto(AULA)),  # conteúdo de PDF, mas a extensão não é
    ],
    ids=["planilha", "slides", "falso pdf", "pdf com outra extensão"],
)
def test_arquivo_que_nao_e_pdf_e_recusado_com_a_orientacao_para_exportar_slides(
    cliente_professor, disciplina, nome, conteudo
):
    resposta = enviar(cliente_professor, disciplina, arquivo=pdf_enviado(conteudo, nome))

    assert resposta.status_code == 400
    assert resposta.json() == {"arquivo": [MENSAGEM_NAO_E_PDF]}
    assert Material.objects.count() == 0  # nada é enviado


@pytest.mark.requisito("MAT-RF-02")
@pytest.mark.parametrize(
    "campos",
    [
        {"aula_numero": ""},
        {"aula_numero": "abc"},
        {"aula_numero": 0},
        {"aula_titulo": ""},
        {"aula_titulo": "   "},
    ],
)
def test_toda_aula_precisa_de_numero_e_titulo(cliente_professor, disciplina, campos):
    resposta = enviar(cliente_professor, disciplina, **campos)

    assert resposta.status_code == 400
    assert Material.objects.count() == 0


@pytest.mark.requisito("MAT-RF-02")
def test_sem_o_arquivo_ou_sem_a_aula_o_envio_e_recusado(cliente_professor, disciplina):
    assert cliente_professor.post(url(disciplina), {}, format="multipart").status_code == 400


def test_pdf_protegido_por_senha_e_recusado_no_envio_com_mensagem_clara(
    cliente_professor, disciplina
):
    resposta = enviar(cliente_professor, disciplina, arquivo=pdf_enviado(pdfs.pdf_protegido(AULA)))

    assert resposta.status_code == 400
    assert "senha" in resposta.json()["arquivo"][0]
    assert Material.objects.count() == 0


def test_pdf_corrompido_e_recusado_no_envio(cliente_professor, disciplina):
    corrompido = pdf_enviado(b"%PDF-1.4 isto nao e um pdf de verdade")

    resposta = enviar(cliente_professor, disciplina, arquivo=corrompido)

    assert resposta.status_code == 400
    assert "PDF válido" in resposta.json()["arquivo"][0]


def test_pdf_com_paginas_demais_e_recusado_dizendo_o_limite(cliente_professor, disciplina):
    seis_paginas = pdf_enviado(pdfs.pdf_com_texto([f"Página {i}" for i in range(6)]))

    with override_settings(FAROL_PDF_MAX_PAGINAS=5):
        resposta = enviar(cliente_professor, disciplina, arquivo=seis_paginas)

    assert resposta.status_code == 400
    assert "5 páginas" in resposta.json()["arquivo"][0]


def test_o_limite_padrao_e_de_300_paginas_e_50_mb(settings):
    assert settings.FAROL_PDF_MAX_PAGINAS == 300
    assert settings.FAROL_PDF_MAX_BYTES == 50 * 1024 * 1024


def test_pdf_grande_demais_e_recusado_dizendo_o_limite(cliente_professor, disciplina):
    grande = pdf_enviado(pdfs.pdf_com_texto(AULA) + b"\n" * (1024 * 1024 + 1))

    with override_settings(FAROL_PDF_MAX_BYTES=1024 * 1024):
        resposta = enviar(cliente_professor, disciplina, arquivo=grande)

    assert resposta.status_code == 400
    assert "1 MB" in resposta.json()["arquivo"][0]
    assert Material.objects.count() == 0


def test_dois_materiais_da_mesma_disciplina_sao_processados_cada_um_na_sua_aula(
    cliente_professor, disciplina
):
    enviar(cliente_professor, disciplina, aula_numero=1, aula_titulo="Introdução")
    enviar(cliente_professor, disciplina, aula_numero=2, aula_titulo="Vetores")

    assert list(Material.objects.values_list("aula_numero", "status")) == [
        (1, Material.Status.PRONTO),
        (2, Material.Status.PRONTO),
    ]


@pytest.mark.requisito("MAT-RNF-02")
def test_aluno_matriculado_nao_envia_material(cliente_aluna, aluna, disciplina):
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)

    assert enviar(cliente_aluna, disciplina).status_code == 403
    assert Material.objects.count() == 0


@pytest.mark.requisito("MAT-RNF-02")
def test_professor_de_outra_disciplina_nao_envia_material(disciplina):
    outro = Pessoa.objects.create_user(
        email="marta.ribeiro@exemplo.edu.br", nome="Marta Ribeiro", perfis=[Perfil.PROFESSOR]
    )
    cliente = APIClient()
    cliente.force_login(outro)

    assert enviar(cliente, disciplina).status_code == 403
    assert Material.objects.count() == 0


@pytest.mark.requisito("MAT-RNF-02")
def test_a_administracao_envia_material_em_qualquer_disciplina(cliente_admin, disciplina):
    assert enviar(cliente_admin, disciplina).status_code == 202


@pytest.mark.requisito("MAT-RNF-02")
def test_administrador_com_outro_perfil_ativo_nao_envia(cliente_admin, admin, disciplina):
    admin.perfis = [Perfil.ALUNO, Perfil.ADMIN]
    admin.save()
    cliente_admin.post("/api/eu/perfil-ativo", {"perfil": "aluno"}, format="json")

    assert enviar(cliente_admin, disciplina).status_code == 403


@pytest.mark.requisito("MAT-RNF-02")
def test_disciplina_que_nao_existe_recebe_403(cliente_professor):
    resposta = cliente_professor.post(
        "/api/disciplinas/999999/materiais",
        {"arquivo": pdf_enviado(), "aula_numero": 1, "aula_titulo": "x"},
        format="multipart",
    )

    assert resposta.status_code == 403


def test_exige_login(cliente, disciplina):
    assert enviar(cliente, disciplina).status_code == 401


def test_a_rota_de_envio_so_aceita_post_e_get_da_lista(cliente_professor, disciplina):
    assert cliente_professor.delete(url(disciplina)).status_code == 405
