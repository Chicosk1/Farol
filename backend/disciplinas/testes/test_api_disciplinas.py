"""GET /api/disciplinas: as disciplinas da pessoa, com busca (ACE-T30).

Cenários de aceite da História 2 da spec 001 (1, 2 e 5) e o filtro "Com tutor", que devolve
uma lista vazia até existir o serviço de materiais (ACE-T34). Todos os dados são fictícios.
"""

import pytest
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula

DISCIPLINAS_DO_2_PERIODO = [
    ("SINF201", "Estruturas de Dados"),
    ("SINF202", "Programação Orientada a Objetos"),
    ("SINF203", "Banco de Dados"),
    ("SINF204", "Engenharia de Software"),
    ("SINF205", "Álgebra Linear"),
    ("SINF206", "Redes de Computadores"),
]


@pytest.fixture
def professor_de_estruturas(professor) -> Pessoa:
    return professor


def criar_disciplina(codigo: str, nome: str, professor: Pessoa, semestre: str = "2026/2"):
    return Disciplina.objects.create(
        codigo=codigo, nome=nome, turma="SINF2NA", semestre=semestre, professor=professor
    )


@pytest.fixture
def seis_disciplinas(professor) -> list[Disciplina]:
    return [criar_disciplina(codigo, nome, professor) for codigo, nome in DISCIPLINAS_DO_2_PERIODO]


@pytest.fixture
def aluna_matriculada_nas_seis(aluna, seis_disciplinas) -> Pessoa:
    for disciplina in seis_disciplinas:
        Matricula.objects.create(aluno=aluna, disciplina=disciplina)
    return aluna


def nomes(resposta) -> list[str]:
    return [item["nome"] for item in resposta.json()]


@pytest.mark.requisito("ACE-RF-04")
def test_aluno_matriculado_em_6_disciplinas_ve_as_6_e_nenhuma_outra(
    cliente_aluna, aluna_matriculada_nas_seis, professor
):
    criar_disciplina("SINF301", "Compiladores", professor)  # de outra turma, sem matrícula

    resposta = cliente_aluna.get("/api/disciplinas")

    assert resposta.status_code == 200
    assert sorted(nomes(resposta)) == sorted(nome for _, nome in DISCIPLINAS_DO_2_PERIODO)


@pytest.mark.requisito("ACE-RF-04")
def test_cada_disciplina_traz_codigo_turma_semestre_e_o_nome_do_professor(
    cliente_aluna, aluna_matriculada_nas_seis
):
    resposta = cliente_aluna.get("/api/disciplinas", {"busca": "Estruturas"})

    (disciplina,) = resposta.json()
    assert disciplina == {
        "id": Disciplina.objects.get(codigo="SINF201").id,
        "codigo": "SINF201",
        "nome": "Estruturas de Dados",
        "turma": "SINF2NA",
        "semestre": "2026/2",
        "professor_nome": "Carlos Mendes",
        "favorita": False,
    }


@pytest.mark.requisito("ACE-RF-04")
def test_matricula_encerrada_tira_a_disciplina_do_aluno(cliente_aluna, aluna_matriculada_nas_seis):
    Matricula.objects.filter(disciplina__codigo="SINF203").update(
        situacao=Matricula.Situacao.ENCERRADA
    )

    resposta = cliente_aluna.get("/api/disciplinas")

    assert len(resposta.json()) == 5
    assert "Banco de Dados" not in nomes(resposta)


@pytest.mark.requisito("ACE-RF-04")
def test_a_lista_vem_em_ordem_alfabetica_sem_considerar_acentos(
    cliente_aluna, aluna_matriculada_nas_seis
):
    resposta = cliente_aluna.get("/api/disciplinas")

    assert nomes(resposta) == [
        "Álgebra Linear",
        "Banco de Dados",
        "Engenharia de Software",
        "Estruturas de Dados",
        "Programação Orientada a Objetos",
        "Redes de Computadores",
    ]


@pytest.mark.requisito("ACE-RF-10")
@pytest.mark.parametrize(
    "busca",
    ["programacao", "PROGRAMAÇÃO", "  Programação  ", "orientada a obj", "programa"],
)
def test_busca_por_parte_do_nome_ignora_acentos_e_maiusculas(
    cliente_aluna, aluna_matriculada_nas_seis, busca
):
    resposta = cliente_aluna.get("/api/disciplinas", {"busca": busca})

    assert nomes(resposta) == ["Programação Orientada a Objetos"]


@pytest.mark.requisito("ACE-RF-10")
def test_busca_sem_acento_acha_nome_com_acento_e_vice_versa(
    cliente_aluna, aluna_matriculada_nas_seis
):
    assert nomes(cliente_aluna.get("/api/disciplinas", {"busca": "algebra"})) == ["Álgebra Linear"]
    assert nomes(cliente_aluna.get("/api/disciplinas", {"busca": "álgebra"})) == ["Álgebra Linear"]


@pytest.mark.requisito("ACE-RF-10")
def test_busca_mostra_so_as_que_contem_o_texto_e_so_entre_as_da_pessoa(
    cliente_aluna, aluna_matriculada_nas_seis, professor
):
    criar_disciplina("SINF302", "Estruturas Avançadas", professor)  # sem matrícula

    resposta = cliente_aluna.get("/api/disciplinas", {"busca": "estruturas"})

    assert nomes(resposta) == ["Estruturas de Dados"]


@pytest.mark.requisito("ACE-RF-10")
def test_busca_vazia_ou_so_com_espacos_nao_filtra(cliente_aluna, aluna_matriculada_nas_seis):
    assert len(cliente_aluna.get("/api/disciplinas", {"busca": "   "}).json()) == 6
    assert len(cliente_aluna.get("/api/disciplinas", {"busca": ""}).json()) == 6


@pytest.mark.requisito("ACE-RF-10")
def test_busca_sem_resultado_devolve_lista_vazia(cliente_aluna, aluna_matriculada_nas_seis):
    resposta = cliente_aluna.get("/api/disciplinas", {"busca": "culinária"})

    assert resposta.status_code == 200
    assert resposta.json() == []


@pytest.mark.requisito("ACE-RF-10")
def test_a_busca_nao_trata_o_texto_como_padrao_de_banco(cliente_aluna, aluna_matriculada_nas_seis):
    # % e _ valeriam como curingas se o texto fosse repassado sem cuidado ao LIKE.
    assert cliente_aluna.get("/api/disciplinas", {"busca": "%"}).json() == []
    assert cliente_aluna.get("/api/disciplinas", {"busca": "_"}).json() == []


@pytest.mark.requisito("ACE-RF-04")
def test_professor_ve_so_as_disciplinas_que_leciona(cliente_professor, seis_disciplinas, aluna):
    outro = Pessoa.objects.create_user(
        email="marina.lopes@exemplo.edu.br", nome="Marina Lopes", perfis=[Perfil.PROFESSOR]
    )
    criar_disciplina("SINF310", "Sistemas Operacionais", outro)

    resposta = cliente_professor.get("/api/disciplinas")

    assert len(resposta.json()) == 6
    assert "Sistemas Operacionais" not in nomes(resposta)


@pytest.mark.requisito("ACE-RF-04")
def test_professor_nao_ve_disciplina_so_por_ser_aluno_dela(
    cliente_professor, seis_disciplinas, professor
):
    # O mesmo professor também está matriculado numa disciplina de outra pessoa.
    outro = Pessoa.objects.create_user(
        email="o@exemplo.edu.br", nome="O", perfis=[Perfil.PROFESSOR]
    )
    de_outro = criar_disciplina("SINF320", "Ética em Computação", outro)
    Matricula.objects.create(aluno=professor, disciplina=de_outro)

    resposta = cliente_professor.get("/api/disciplinas")  # perfil ativo: professor

    assert "Ética em Computação" not in nomes(resposta)


@pytest.mark.requisito("ACE-RF-03")
@pytest.mark.requisito("ACE-RF-04")
def test_com_dois_perfis_a_lista_segue_o_perfil_ativo(seis_disciplinas, professor):
    de_outro = criar_disciplina("SINF320", "Ética em Computação", professor)
    professor.perfis = [Perfil.PROFESSOR, Perfil.ALUNO]
    professor.save()
    colega = Pessoa.objects.create_user(
        email="c@exemplo.edu.br", nome="C", perfis=[Perfil.PROFESSOR]
    )
    de_colega = criar_disciplina("SINF321", "Gestão de Projetos", colega)
    Matricula.objects.create(aluno=professor, disciplina=de_colega)
    cliente = APIClient()
    cliente.force_login(professor)

    como_professor = cliente.get("/api/disciplinas")
    cliente.post("/api/eu/perfil-ativo", {"perfil": "aluno"}, format="json")
    como_aluno = cliente.get("/api/disciplinas")

    assert "Ética em Computação" in nomes(como_professor)
    assert nomes(como_aluno) == ["Gestão de Projetos"]
    assert de_outro.professor == professor


@pytest.mark.requisito("ACE-RF-04")
@pytest.mark.parametrize("perfil", [Perfil.COORDENACAO, Perfil.ADMIN])
def test_coordenacao_e_admin_ainda_nao_tem_lista_propria(seis_disciplinas, perfil):
    pessoa = Pessoa.objects.create_user(email="z@exemplo.edu.br", nome="Z", perfis=[perfil])
    cliente = APIClient()
    cliente.force_login(pessoa)

    assert cliente.get("/api/disciplinas").json() == []


def material(disciplina: Disciplina, status: str):
    from materiais.models import Material

    return Material.objects.create(
        disciplina=disciplina,
        aula_numero=1,
        aula_titulo="Introdução",
        arquivo="materiais/x.pdf",
        status=status,
    )


@pytest.mark.requisito("ACE-RF-10")
def test_aba_com_tutor_mostra_so_as_disciplinas_com_material_pronto(
    cliente_aluna, aluna_matriculada_nas_seis
):
    estruturas = Disciplina.objects.get(codigo="SINF201")
    banco = Disciplina.objects.get(codigo="SINF203")
    redes = Disciplina.objects.get(codigo="SINF206")
    material(estruturas, "pronto")
    material(banco, "pronto")
    material(banco, "processando")  # um pronto basta, e o outro não atrapalha
    material(redes, "processando")  # sem nenhum pronto, não entra

    resposta = cliente_aluna.get("/api/disciplinas", {"filtro": "com-tutor"})

    assert resposta.status_code == 200
    assert nomes(resposta) == ["Banco de Dados", "Estruturas de Dados"]


@pytest.mark.requisito("ACE-RF-10")
def test_aba_com_tutor_nao_conta_material_retirado_nem_com_erro(
    cliente_aluna, aluna_matriculada_nas_seis
):
    estruturas = Disciplina.objects.get(codigo="SINF201")
    for status in ("retirado", "erro", "atencao"):
        material(estruturas, status)

    assert cliente_aluna.get("/api/disciplinas", {"filtro": "com-tutor"}).json() == []


@pytest.mark.requisito("ACE-RF-10")
def test_aba_com_tutor_so_mostra_disciplinas_da_pessoa_e_aceita_busca(
    cliente_aluna, aluna_matriculada_nas_seis, professor
):
    estruturas = Disciplina.objects.get(codigo="SINF201")
    banco = Disciplina.objects.get(codigo="SINF203")
    de_outra_turma = criar_disciplina("SINF399", "Estruturas Avançadas", professor)
    for d in (estruturas, banco, de_outra_turma):
        material(d, "pronto")

    resposta = cliente_aluna.get("/api/disciplinas", {"filtro": "com-tutor", "busca": "estruturas"})

    assert nomes(resposta) == ["Estruturas de Dados"]


@pytest.mark.requisito("ACE-RF-10")
def test_filtro_todas_e_o_padrao(cliente_aluna, aluna_matriculada_nas_seis):
    assert len(cliente_aluna.get("/api/disciplinas", {"filtro": "todas"}).json()) == 6


def test_filtro_desconhecido_e_recusado(cliente_aluna):
    assert cliente_aluna.get("/api/disciplinas", {"filtro": "arquivadas"}).status_code == 400


def test_exige_login(cliente):
    assert cliente.get("/api/disciplinas").status_code == 401


def test_so_aceita_leitura(cliente_aluna):
    assert cliente_aluna.post("/api/disciplinas").status_code == 405


@pytest.mark.django_db
def test_o_banco_recusa_a_mesma_disciplina_duas_vezes_e_a_mesma_matricula_duas_vezes(
    professor, aluna
):
    from django.db import IntegrityError, transaction

    disciplina = criar_disciplina("SINF201", "Estruturas de Dados", professor)
    with pytest.raises(IntegrityError), transaction.atomic():
        criar_disciplina("SINF201", "Estruturas de Dados II", professor)

    Matricula.objects.create(aluno=aluna, disciplina=disciplina)
    with pytest.raises(IntegrityError), transaction.atomic():
        Matricula.objects.create(aluno=aluna, disciplina=disciplina)

    # O mesmo código em outro semestre é outra oferta, e vale.
    criar_disciplina("SINF201", "Estruturas de Dados", professor, semestre="2027/1")
