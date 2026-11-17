"""A página citada com o trecho destacado (MAT-T32, MAT-RF-09). Dados fictícios."""

import pytest
from django.core.files.base import ContentFile
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from materiais import servicos
from materiais.models import Material, Trecho
from materiais.testes import pdfs

PAGINA_2 = (
    "Uma pilha segue a ordem LIFO. O último elemento inserido é o primeiro a sair. "
    "As operações são push e pop."
)


@pytest.fixture(autouse=True)
def arquivos_temporarios(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def material(professor, aluna) -> Material:
    disciplina = Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)
    material = Material(
        disciplina=disciplina, aula_numero=5, aula_titulo="Pilhas", enviado_por=professor
    )
    conteudo = pdfs.pdf_com_texto(["Capa da aula de pilhas.", PAGINA_2])
    material.arquivo.save("aula-5.pdf", ContentFile(conteudo), save=False)
    material.save()
    servicos.processar_material(material.id)
    return material


def url(trecho) -> str:
    return f"/api/trechos/{trecho.id}"


@pytest.mark.requisito("MAT-RF-09")
def test_a_citacao_abre_a_pagina_com_o_trecho_destacado(cliente_aluna, material):
    trecho = Trecho.objects.filter(material=material, pagina=2).first()

    dados = cliente_aluna.get(url(trecho)).json()

    assert dados["material_id"] == material.id
    assert (dados["aula_numero"], dados["aula_titulo"], dados["pagina"]) == (5, "Pilhas", 2)
    pagina = dados["texto_da_pagina"]
    assert "LIFO" in pagina
    assert pagina[dados["inicio"] : dados["fim"]] == trecho.texto
    assert dados["atualizado"] is False


def test_trecho_de_material_nao_pronto_ou_de_outra_disciplina_nao_abre(material):
    trecho = Trecho.objects.filter(material=material).first()
    outra = Pessoa.objects.create_user(
        email="bruno.dias@exemplo.edu.br", nome="Bruno Dias", perfis=[Perfil.ALUNO]
    )
    cliente = APIClient()
    cliente.force_login(outra)

    assert cliente.get(url(trecho)).status_code == 403
    Material.objects.filter(pk=material.pk).update(status=Material.Status.RETIRADO)
    aluna = Pessoa.objects.get(email="ana.souza@exemplo.edu.br")
    cliente.force_login(aluna)
    assert cliente.get(url(trecho)).status_code == 404


@pytest.mark.requisito("MAT-RF-09")
def test_citacao_de_versao_substituida_avisa_e_abre_o_pdf_da_versao_nova(
    cliente_aluna, material, professor
):
    trecho = Trecho.objects.filter(material=material, pagina=2).first()
    nova = Material(
        disciplina=material.disciplina,
        aula_numero=5,
        aula_titulo="Pilhas",
        versao=2,
        substitui=material,
        enviado_por=professor,
    )
    nova.arquivo.save(
        "aula-5-v2.pdf", ContentFile(pdfs.pdf_com_texto(["Pilha: LIFO."])), save=False
    )
    nova.save()
    servicos.processar_material(nova.id)

    dados = cliente_aluna.get(url(trecho)).json()

    assert dados["atualizado"] is True
    assert dados["material_id"] == nova.id  # o PDF abre na versão nova
    assert trecho.texto in dados["texto_da_pagina"]  # o trecho é o da versão citada


def test_trecho_que_nao_existe_recebe_404_e_sem_login_401(cliente_aluna, cliente):
    assert cliente_aluna.get("/api/trechos/999999").status_code == 404
    assert cliente.get("/api/trechos/1").status_code == 401
