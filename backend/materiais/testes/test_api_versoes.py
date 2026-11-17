"""Nova versão de um material, que substitui a anterior quando fica pronta (MAT-T52, MAT-RF-11).

A IA é o adaptador falso. Dados fictícios.
"""

from unittest import mock

import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from disciplinas.models import Disciplina, Matricula
from materiais import servicos
from materiais.models import Material
from materiais.testes import pdfs


@pytest.fixture(autouse=True)
def arquivos_temporarios(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def disciplina(professor, aluna) -> Disciplina:
    disciplina = Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)
    return disciplina


@pytest.fixture
def publicado(disciplina, professor) -> Material:
    material = Material(
        disciplina=disciplina, aula_numero=5, aula_titulo="Pilhas", enviado_por=professor
    )
    material.arquivo.save(
        "aula-5.pdf", ContentFile(pdfs.pdf_com_texto(["Pilha é LIFO."])), save=False
    )
    material.save()
    servicos.processar_material(material.id)
    material.refresh_from_db()
    assert material.status == Material.Status.PRONTO
    return material


def enviar_versao(cliente, material, conteudo: bytes | None = None):
    arquivo = SimpleUploadedFile(
        "aula-5-corrigida.pdf",
        conteudo
        or pdfs.pdf_com_texto(["Pilha segue a ordem LIFO: último a entrar, primeiro a sair."]),
        content_type="application/pdf",
    )
    return cliente.post(
        f"/api/materiais/{material.id}/versoes", {"arquivo": arquivo}, format="multipart"
    )


@pytest.mark.requisito("MAT-RF-11")
def test_a_versao_nova_substitui_a_anterior_quando_fica_pronta(cliente_professor, publicado):
    resposta = enviar_versao(cliente_professor, publicado)

    assert resposta.status_code == 202
    nova = Material.objects.get(id=resposta.json()["material_id"])
    publicado.refresh_from_db()
    assert (nova.aula_numero, nova.aula_titulo, nova.versao, nova.substitui) == (
        5,
        "Pilhas",
        2,
        publicado,
    )
    assert nova.status == Material.Status.PRONTO  # o Celery roda na hora nos testes
    assert publicado.status == Material.Status.SUBSTITUIDO


@pytest.mark.requisito("MAT-RF-11")
def test_a_versao_antiga_continua_em_uso_enquanto_a_nova_processa(cliente_professor, publicado):
    with mock.patch.object(servicos, "enfileirar_processamento"):  # a fila ainda não rodou
        resposta = enviar_versao(cliente_professor, publicado)

    publicado.refresh_from_db()
    assert publicado.status == Material.Status.PRONTO
    assert Material.objects.get(id=resposta.json()["material_id"]).status == "processando"
    trechos = servicos.buscar_trechos(publicado.disciplina_id, [0.1] * 256, limite=6)
    assert {t.material_id for t in trechos} == {publicado.id}


@pytest.mark.requisito("MAT-RF-11")
def test_se_a_versao_nova_falha_a_anterior_continua_valendo(cliente_professor, publicado):
    with mock.patch.object(servicos, "enfileirar_processamento"):
        resposta = enviar_versao(cliente_professor, publicado)
    nova = Material.objects.get(id=resposta.json()["material_id"])
    nova.arquivo.save("quebrado.pdf", ContentFile(b"%PDF-1.7 quebrado"))

    servicos.processar_material(nova.id)

    publicado.refresh_from_db()
    nova.refresh_from_db()
    assert nova.status == Material.Status.ERRO
    assert publicado.status == Material.Status.PRONTO


@pytest.mark.requisito("MAT-RF-11")
def test_o_aluno_so_ve_a_versao_atual_e_a_citacao_antiga_abre_a_nova(
    cliente_professor, cliente_aluna, publicado
):
    nova_id = enviar_versao(cliente_professor, publicado).json()["material_id"]

    lista = cliente_aluna.get(f"/api/disciplinas/{publicado.disciplina_id}/materiais").json()
    assert [m["id"] for m in lista] == [nova_id]
    antiga = cliente_aluna.get(f"/api/materiais/{publicado.id}/arquivo?pagina=1")
    assert antiga.status_code == 200
    assert antiga["Content-Disposition"].endswith('aula-5.pdf"')
    assert antiga["X-Farol-Material"] == str(nova_id)


def test_nao_ha_versao_nova_de_material_retirado(cliente_professor, publicado):
    cliente_professor.delete(f"/api/materiais/{publicado.id}")

    resposta = enviar_versao(cliente_professor, publicado)

    assert resposta.status_code == 400


def test_versao_nova_que_nao_e_pdf_e_recusada(cliente_professor, publicado):
    resposta = enviar_versao(cliente_professor, publicado, conteudo=pdfs.nao_e_pdf())

    assert resposta.status_code == 400
    assert Material.objects.count() == 1


@pytest.mark.requisito("MAT-RNF-02")
def test_so_o_professor_da_disciplina_e_a_administracao_enviam_versao(cliente_aluna, publicado):
    assert enviar_versao(cliente_aluna, publicado).status_code == 403
