"""Comando popular_demo: pessoas, disciplinas e matrículas fictícias do protótipo (ACE-T25, T27)."""

from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula


def popular() -> str:
    saida = StringIO()
    call_command("popular_demo", stdout=saida)
    return saida.getvalue()


@pytest.mark.django_db
def test_cria_a_aluna_ana_souza_e_o_professor_carlos_mendes():
    popular()

    ana = Pessoa.objects.get(email="ana.souza@exemplo.edu.br")
    carlos = Pessoa.objects.get(email="carlos.mendes@exemplo.edu.br")
    assert (ana.nome, ana.perfis) == ("Ana Souza", [Perfil.ALUNO])
    assert (carlos.nome, carlos.perfis) == ("Carlos Mendes", [Perfil.PROFESSOR])


@pytest.mark.django_db
def test_rodar_de_novo_nao_duplica_nem_desfaz_nada():
    popular()
    ana = Pessoa.objects.get(email="ana.souza@exemplo.edu.br")

    saida = popular()

    assert Pessoa.objects.count() == 7  # a aluna e os 6 professores
    assert Pessoa.objects.get(email="ana.souza@exemplo.edu.br").id == ana.id
    assert "já existiam" in saida


@pytest.mark.django_db
def test_rodar_de_novo_restaura_o_perfil_e_reativa_a_pessoa():
    popular()
    Pessoa.objects.filter(email="ana.souza@exemplo.edu.br").update(perfis=[], is_active=False)

    popular()

    ana = Pessoa.objects.get(email="ana.souza@exemplo.edu.br")
    assert ana.perfis == [Perfil.ALUNO]
    assert ana.is_active


@pytest.mark.django_db
def test_as_pessoas_de_demonstracao_nao_tem_senha():
    popular()

    assert not any(pessoa.has_usable_password() for pessoa in Pessoa.objects.all())


@pytest.mark.django_db
def test_so_usa_dados_ficticios_de_um_dominio_de_exemplo():
    popular()

    assert all(pessoa.email.endswith("@exemplo.edu.br") for pessoa in Pessoa.objects.all())


@pytest.mark.django_db
def test_recusa_rodar_fora_do_desenvolvimento_e_do_teste():
    with (
        override_settings(FAROL_LOGIN_DESENVOLVIMENTO=False),
        pytest.raises(CommandError, match="desenvolvimento"),
    ):
        popular()

    assert Pessoa.objects.count() == 0
    assert Disciplina.objects.count() == 0


NOMES_DAS_DISCIPLINAS = {
    "Estruturas de Dados",
    "Banco de Dados I",
    "Programação Orientada a Objetos",
    "Matemática Discreta",
    "Cálculo Diferencial e Integral",
    "Engenharia de Software I",
}


@pytest.mark.requisito("ACE-RF-04")
@pytest.mark.django_db
def test_cria_as_seis_disciplinas_do_2_periodo_da_turma_sinf2na():
    popular()

    disciplinas = Disciplina.objects.all()
    assert {d.nome for d in disciplinas} == NOMES_DAS_DISCIPLINAS
    assert {(d.turma, d.semestre) for d in disciplinas} == {("SINF2NA", "2026/2")}
    estruturas = Disciplina.objects.get(nome="Estruturas de Dados")
    assert estruturas.professor.email == "carlos.mendes@exemplo.edu.br"


@pytest.mark.requisito("ACE-RF-04")
@pytest.mark.django_db
def test_a_aluna_ana_esta_matriculada_nas_seis_disciplinas():
    popular()

    matriculas = Matricula.objects.filter(aluno__email="ana.souza@exemplo.edu.br")
    assert matriculas.count() == 6
    assert all(m.situacao == Matricula.Situacao.ATIVA for m in matriculas)


@pytest.mark.requisito("ACE-RF-04")
@pytest.mark.django_db
def test_rodar_de_novo_nao_duplica_disciplinas_nem_matriculas_e_reativa_a_matricula():
    popular()
    Matricula.objects.update(situacao=Matricula.Situacao.ENCERRADA)

    popular()

    assert Disciplina.objects.count() == 6
    assert Matricula.objects.count() == 6
    assert not Matricula.objects.exclude(situacao=Matricula.Situacao.ATIVA).exists()


@pytest.mark.requisito("ACE-RF-04")
@pytest.mark.django_db
def test_o_login_de_desenvolvimento_mostra_6_disciplinas_para_a_ana_e_1_para_o_carlos(cliente):
    popular()

    cliente.post("/api/dev/entrar", {"email": "ana.souza@exemplo.edu.br"}, format="json")
    da_ana = cliente.get("/api/disciplinas").json()
    cliente.post("/api/sair")
    cliente.post("/api/dev/entrar", {"email": "carlos.mendes@exemplo.edu.br"}, format="json")
    do_carlos = cliente.get("/api/disciplinas").json()

    assert {d["nome"] for d in da_ana} == NOMES_DAS_DISCIPLINAS
    assert [d["nome"] for d in do_carlos] == ["Estruturas de Dados"]
