"""DELETE /api/materiais/{id}: o professor retira um material (MAT-T51, MAT-T50).

Cenário 1 da História 4 da spec 002: o material some da lista do aluno e deixa de ser usado. O
teste de que o tutor para de usar o material retirado está na spec 003 (MAT-CS-03). Dados fictícios.
"""

from unittest import mock

import pytest
from django.core.files.base import ContentFile
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from materiais import servicos
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


@pytest.fixture
def material(disciplina) -> Material:
    material = Material(disciplina=disciplina, aula_numero=4, aula_titulo="Listas")
    material.arquivo.save("aula-4.pdf", ContentFile(pdfs.pdf_com_texto(["Listas encadeadas"])))
    return servicos.processar_material(material.id)


def retirar(cliente, material):
    return cliente.delete(f"/api/materiais/{material.id}")


@pytest.mark.requisito("MAT-RF-10")
def test_professor_retira_o_material_e_ele_passa_a_retirado(cliente_professor, material):
    assert material.status == Material.Status.PRONTO

    resposta = retirar(cliente_professor, material)

    assert resposta.status_code == 204
    material.refresh_from_db()
    assert material.status == Material.Status.RETIRADO


@pytest.mark.requisito("MAT-RF-10")
def test_o_material_retirado_some_da_lista_e_do_pdf_do_aluno(
    cliente_aluna, cliente_professor, aluna, disciplina, material
):
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)
    assert len(cliente_aluna.get(f"/api/disciplinas/{disciplina.id}/materiais").json()) == 1

    retirar(cliente_professor, material)

    assert cliente_aluna.get(f"/api/disciplinas/{disciplina.id}/materiais").json() == []
    assert cliente_aluna.get(f"/api/materiais/{material.id}/arquivo").status_code == 404


@pytest.mark.requisito("MAT-RF-10")
def test_o_professor_continua_vendo_o_material_retirado_na_lista(
    cliente_professor, disciplina, material
):
    retirar(cliente_professor, material)

    (item,) = cliente_professor.get(f"/api/disciplinas/{disciplina.id}/materiais").json()

    assert item["status"] == "retirado"


@pytest.mark.requisito("MAT-RF-10")
def test_retirar_nao_apaga_o_arquivo_nem_os_trechos(cliente_professor, material):
    retirar(cliente_professor, material)

    material.refresh_from_db()
    material.arquivo.open("rb").close()
    assert Trecho.objects.filter(material=material).count() == 1


@pytest.mark.requisito("MAT-RF-10")
def test_retirar_de_novo_tambem_responde_204(cliente_professor, material):
    retirar(cliente_professor, material)

    assert retirar(cliente_professor, material).status_code == 204


@pytest.mark.requisito("MAT-RF-10")
def test_material_retirado_durante_o_processamento_nao_volta_a_ficar_pronto(disciplina):
    material = Material(disciplina=disciplina, aula_numero=1, aula_titulo="Intro")
    material.arquivo.save(
        "aula-1.pdf", ContentFile(pdfs.pdf_com_texto(["Introdução à disciplina"]))
    )
    vetorizar_real = servicos.ia.gerar_embeddings

    def retirar_no_meio(textos):
        Material.objects.filter(pk=material.pk).update(status=Material.Status.RETIRADO)
        return vetorizar_real(textos)

    with mock.patch.object(servicos.ia, "gerar_embeddings", retirar_no_meio):
        resultado = servicos.processar_material(material.id)

    assert resultado.status == Material.Status.RETIRADO
    assert Trecho.objects.count() == 0


@pytest.mark.requisito("MAT-RF-10")
def test_material_retirado_nao_e_reprocessado(disciplina, material):
    Material.objects.filter(pk=material.pk).update(status=Material.Status.RETIRADO)

    assert servicos.processar_material(material.id).status == Material.Status.RETIRADO


@pytest.mark.requisito("MAT-RNF-02")
def test_aluno_nao_retira_material(cliente_aluna, aluna, disciplina, material):
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)

    assert retirar(cliente_aluna, material).status_code == 403
    material.refresh_from_db()
    assert material.status == Material.Status.PRONTO


@pytest.mark.requisito("MAT-RNF-02")
def test_professor_de_outra_disciplina_nao_retira_material(material):
    outro = Pessoa.objects.create_user(
        email="marta.ribeiro@exemplo.edu.br", nome="Marta Ribeiro", perfis=[Perfil.PROFESSOR]
    )
    cliente = APIClient()
    cliente.force_login(outro)

    assert retirar(cliente, material).status_code == 403


@pytest.mark.requisito("MAT-RNF-02")
def test_a_administracao_retira_material_de_qualquer_disciplina(cliente_admin, material):
    assert retirar(cliente_admin, material).status_code == 204


def test_material_que_nao_existe_recebe_404_e_sem_login_recebe_401(
    cliente_professor, cliente, material
):
    assert cliente_professor.delete("/api/materiais/999999").status_code == 404
    assert retirar(cliente, material).status_code == 401
