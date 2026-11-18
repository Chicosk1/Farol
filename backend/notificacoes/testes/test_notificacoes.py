"""Notificações: o aviso ao professor quando o material fica pronto ou falha (MAT-T23, MAT-RF-06).

Dados fictícios. A IA é o adaptador falso.
"""

import pytest
from django.core.files.base import ContentFile
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina
from materiais import servicos as materiais
from materiais.models import Material
from materiais.testes import pdfs
from notificacoes import servicos
from notificacoes.models import Notificacao


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


def material_com(disciplina, professor, conteudo: bytes) -> Material:
    material = Material(
        disciplina=disciplina, aula_numero=5, aula_titulo="Pilhas", enviado_por=professor
    )
    material.arquivo.save("aula-5.pdf", ContentFile(conteudo), save=False)
    material.save()
    return material


@pytest.mark.requisito("MAT-RF-06")
def test_material_pronto_avisa_o_professor(disciplina, professor):
    material = material_com(disciplina, professor, pdfs.pdf_com_texto(["Uma pilha é LIFO."]))

    materiais.processar_material(material.id)

    aviso = Notificacao.objects.get()
    assert aviso.pessoa == professor
    assert aviso.tipo == "material_pronto"
    assert aviso.texto == "Aula 5, Pilhas, está pronta para o tutor."
    assert aviso.link == f"/disciplinas/{disciplina.id}/materiais"
    assert aviso.lida is False


@pytest.mark.requisito("MAT-RF-06")
def test_material_que_falha_ou_precisa_de_atencao_tambem_avisa(disciplina, professor):
    escaneado = material_com(disciplina, professor, pdfs.pdf_escaneado(3))
    quebrado = material_com(disciplina, professor, b"%PDF-1.7 quebrado")

    materiais.processar_material(escaneado.id)
    materiais.processar_material(quebrado.id)

    textos = sorted(Notificacao.objects.values_list("tipo", "texto"))
    assert textos[0][0] == "material_atencao"
    assert textos[0][1].startswith("Aula 5, Pilhas, precisa de atenção:")
    assert textos[1][0] == "material_erro"
    assert textos[1][1].startswith("Aula 5, Pilhas, não pôde ser processada.")


def url(id_=None) -> str:
    return "/api/notificacoes" if id_ is None else f"/api/notificacoes/{id_}/lida"


@pytest.mark.requisito("MAT-RF-06")
def test_a_pessoa_ve_as_suas_notificacoes_mais_novas_primeiro_e_quantas_nao_leu(
    cliente_professor, professor, aluna
):
    servicos.notificar(professor, "material_pronto", "Aula 4, Listas, está pronta para o tutor.")
    servicos.notificar(professor, "material_pronto", "Aula 5, Pilhas, está pronta para o tutor.")
    servicos.notificar(aluna, "material_pronto", "Aviso de outra pessoa.")

    dados = cliente_professor.get(url()).json()

    assert dados["nao_lidas"] == 2
    assert [n["texto"] for n in dados["notificacoes"]] == [
        "Aula 5, Pilhas, está pronta para o tutor.",
        "Aula 4, Listas, está pronta para o tutor.",
    ]
    assert set(dados["notificacoes"][0]) == {"id", "tipo", "texto", "link", "lida", "criada_em"}


@pytest.mark.requisito("MAT-RF-06")
def test_marcar_como_lida_tira_da_contagem(cliente_professor, professor):
    aviso = servicos.notificar(professor, "material_pronto", "Aula 5 pronta.")

    assert cliente_professor.post(url(aviso.id)).status_code == 204

    aviso.refresh_from_db()
    assert aviso.lida is True
    assert cliente_professor.get(url()).json()["nao_lidas"] == 0


def test_nao_da_para_marcar_a_notificacao_de_outra_pessoa(cliente_professor, aluna):
    aviso = servicos.notificar(aluna, "material_pronto", "Aviso da Ana.")

    assert cliente_professor.post(url(aviso.id)).status_code == 404
    aviso.refresh_from_db()
    assert aviso.lida is False


def test_sem_login_recebe_401():
    assert APIClient().get(url()).status_code == 401


def test_lista_so_as_50_mais_recentes(professor):
    for numero in range(55):
        servicos.notificar(professor, "material_pronto", f"Aviso {numero}")
    outra = Pessoa.objects.create_user(
        email="rita.lima@exemplo.edu.br", nome="Rita Lima", perfis=[Perfil.PROFESSOR]
    )

    notificacoes, nao_lidas = servicos.notificacoes_de(professor)

    assert len(notificacoes) == 50 and nao_lidas == 55
    assert notificacoes[0].texto == "Aviso 54"
    assert servicos.notificacoes_de(outra) == ([], 0)
