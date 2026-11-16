"""Comando popular_demo: pessoas fictícias do protótipo para desenvolver e demonstrar (ACE-T25)."""

from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings

from contas.models import Perfil, Pessoa


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

    assert Pessoa.objects.count() == 2
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
