"""Lista de materiais e abertura do PDF (MAT-T31, MAT-T30).

Cenários de aceite da História 2 da spec 002: o aluno vê só os materiais prontos, ordenados por
aula, e abre o PDF. O professor vê todos, com a etapa e os avisos. Dados fictícios.
"""

import pytest
from django.core.files.base import ContentFile
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from materiais.models import Material
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
def aluna_matriculada(aluna, disciplina) -> Pessoa:
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)
    return aluna


def criar(disciplina, aula: int, status=Material.Status.PRONTO, paginas: int = 10, **extras):
    material = Material(
        disciplina=disciplina,
        aula_numero=aula,
        aula_titulo=f"Aula {aula}",
        paginas=paginas,
        status=status,
        **extras,
    )
    material.arquivo.save(
        f"aula-{aula}.pdf", ContentFile(pdfs.pdf_com_texto(["Texto"])), save=False
    )
    material.save()
    return material


def lista(cliente, disciplina):
    return cliente.get(f"/api/disciplinas/{disciplina.id}/materiais")


@pytest.mark.requisito("MAT-RF-08")
def test_aluno_ve_os_7_materiais_prontos_ordenados_por_aula_com_titulo_e_paginas(
    cliente_aluna, aluna_matriculada, disciplina
):
    for aula in (5, 1, 7, 3, 2, 6, 4):  # fora de ordem, de propósito
        criar(disciplina, aula, paginas=aula * 10)

    resposta = lista(cliente_aluna, disciplina)

    assert resposta.status_code == 200
    itens = resposta.json()
    assert [i["aula_numero"] for i in itens] == [1, 2, 3, 4, 5, 6, 7]
    assert itens[0]["aula_titulo"] == "Aula 1"
    assert itens[6]["paginas"] == 70


@pytest.mark.requisito("MAT-RF-07")
@pytest.mark.parametrize(
    "status",
    [
        Material.Status.PROCESSANDO,
        Material.Status.ERRO,
        Material.Status.ATENCAO,
        Material.Status.RETIRADO,
    ],
)
def test_aluno_nao_ve_material_que_nao_esta_pronto(
    cliente_aluna, aluna_matriculada, disciplina, status
):
    criar(disciplina, 1, status=Material.Status.PRONTO)
    criar(disciplina, 2, status=status)

    resposta = lista(cliente_aluna, disciplina)

    assert [i["aula_numero"] for i in resposta.json()] == [1]


@pytest.mark.requisito("MAT-RF-07")
def test_a_lista_do_aluno_nao_mostra_status_etapa_erro_nem_caminho_do_arquivo(
    cliente_aluna, aluna_matriculada, disciplina
):
    criar(disciplina, 1)

    (item,) = lista(cliente_aluna, disciplina).json()

    assert set(item) == {"id", "aula_numero", "aula_titulo", "paginas"}


@pytest.mark.requisito("MAT-RF-03")
def test_professor_ve_todos_os_materiais_com_status_etapa_e_avisos(cliente_professor, disciplina):
    criar(disciplina, 1)
    criar(
        disciplina,
        2,
        status=Material.Status.PROCESSANDO,
        etapa=Material.Etapa.VETORIZANDO,
        paginas=0,
    )
    criar(
        disciplina,
        3,
        status=Material.Status.ATENCAO,
        paginas=4,
        paginas_sem_texto=[1, 2, 3],
        erro="Sem texto.",
    )

    itens = lista(cliente_professor, disciplina).json()

    assert [i["aula_numero"] for i in itens] == [1, 2, 3]
    assert itens[1]["status"] == "processando"
    assert itens[1]["etapa"] == "vetorizando"
    assert itens[1]["etapa_rotulo"] == "Gerando a busca semântica"
    assert itens[2]["status_rotulo"] == "Precisa de atenção"
    assert itens[2]["paginas_sem_texto"] == [1, 2, 3]
    assert itens[2]["erro"] == "Sem texto."


@pytest.mark.requisito("MAT-RNF-02")
def test_administracao_ve_todos_os_materiais_da_disciplina(cliente_admin, disciplina):
    criar(disciplina, 1, status=Material.Status.ERRO)

    assert len(lista(cliente_admin, disciplina).json()) == 1


@pytest.mark.requisito("MAT-RF-07")
def test_quem_nao_esta_na_disciplina_recebe_403(cliente_aluna, aluna, disciplina):
    criar(disciplina, 1)

    assert lista(cliente_aluna, disciplina).status_code == 403


@pytest.mark.requisito("MAT-RF-07")
def test_professor_de_outra_disciplina_recebe_403(disciplina):
    outro = Pessoa.objects.create_user(
        email="marta.ribeiro@exemplo.edu.br", nome="Marta Ribeiro", perfis=[Perfil.PROFESSOR]
    )
    cliente = APIClient()
    cliente.force_login(outro)

    assert lista(cliente, disciplina).status_code == 403


def test_a_lista_exige_login(cliente, disciplina):
    assert lista(cliente, disciplina).status_code == 401


@pytest.mark.requisito("MAT-RF-08")
def test_aluno_matriculado_abre_o_pdf_de_um_material_pronto(
    cliente_aluna, aluna_matriculada, disciplina
):
    material = criar(disciplina, 1)

    resposta = cliente_aluna.get(f"/api/materiais/{material.id}/arquivo")

    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/pdf"
    assert resposta["Content-Disposition"].startswith("inline")
    assert b"".join(resposta.streaming_content).startswith(b"%PDF-")
    assert "private" in resposta["Cache-Control"]


@pytest.mark.requisito("MAT-RF-09")
def test_o_pdf_aceita_a_pagina_a_abrir_e_recusa_pagina_invalida(
    cliente_aluna, aluna_matriculada, disciplina
):
    material = criar(disciplina, 1)
    url = f"/api/materiais/{material.id}/arquivo"

    assert cliente_aluna.get(url, {"pagina": 5}).status_code == 200
    assert cliente_aluna.get(url, {"pagina": 0}).status_code == 400
    assert cliente_aluna.get(url, {"pagina": "abc"}).status_code == 400


@pytest.mark.requisito("MAT-RF-07")
@pytest.mark.parametrize(
    "status", [Material.Status.PROCESSANDO, Material.Status.ERRO, Material.Status.RETIRADO]
)
def test_aluno_nao_abre_o_pdf_de_material_que_nao_esta_pronto(
    cliente_aluna, aluna_matriculada, disciplina, status
):
    material = criar(disciplina, 1, status=status)

    assert cliente_aluna.get(f"/api/materiais/{material.id}/arquivo").status_code == 404


@pytest.mark.requisito("MAT-RNF-02")
def test_professor_abre_o_pdf_em_qualquer_status(cliente_professor, disciplina):
    material = criar(disciplina, 1, status=Material.Status.ERRO)

    assert cliente_professor.get(f"/api/materiais/{material.id}/arquivo").status_code == 200


@pytest.mark.requisito("MAT-RF-07")
def test_quem_nao_tem_acesso_a_disciplina_nao_abre_o_pdf(cliente_aluna, aluna, disciplina):
    material = criar(disciplina, 1)

    assert cliente_aluna.get(f"/api/materiais/{material.id}/arquivo").status_code == 403


def test_pdf_que_nao_existe_recebe_404_e_sem_login_recebe_401(cliente_aluna, cliente, disciplina):
    material = criar(disciplina, 1)

    assert cliente_aluna.get("/api/materiais/999999/arquivo").status_code == 404
    assert cliente.get(f"/api/materiais/{material.id}/arquivo").status_code == 401
