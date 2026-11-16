"""Modelo Pessoa: o usuário do Farol, identificado pelo e-mail institucional e sem senha própria.

Requisito verificado: ACE-RF-02 (o sistema não cria nem guarda senhas próprias).
Todos os dados são fictícios.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from contas.models import Pessoa


def test_pessoa_e_o_modelo_de_usuario_e_entra_pelo_email():
    assert get_user_model() is Pessoa
    assert Pessoa.USERNAME_FIELD == "email"


@pytest.mark.django_db
def test_pessoa_criada_nao_tem_senha_utilizavel():
    pessoa = Pessoa.objects.create_user(email="ana.souza@exemplo.edu.br", nome="Ana Souza")

    pessoa.refresh_from_db()
    assert not pessoa.has_usable_password()


@pytest.mark.django_db
def test_superusuario_tambem_nao_tem_senha_utilizavel():
    pessoa = Pessoa.objects.create_superuser(
        email="equipe.ti@exemplo.edu.br", nome="Equipe de TI", password="ignorada"
    )

    pessoa.refresh_from_db()
    assert pessoa.is_staff
    assert pessoa.is_superuser
    assert not pessoa.has_usable_password()


@pytest.mark.django_db
def test_definir_senha_nao_grava_senha_nenhuma():
    pessoa = Pessoa.objects.create_user(email="carlos.mendes@exemplo.edu.br", nome="Carlos Mendes")

    pessoa.set_password("uma-senha-qualquer")
    pessoa.save()
    pessoa.refresh_from_db()

    assert not pessoa.has_usable_password()
    assert not pessoa.check_password("uma-senha-qualquer")


@pytest.mark.django_db
def test_email_e_guardado_sem_espacos_e_em_minusculas():
    pessoa = Pessoa.objects.create_user(email="  Ana.Souza@Exemplo.EDU.br ", nome="Ana Souza")

    pessoa.refresh_from_db()
    assert pessoa.email == "ana.souza@exemplo.edu.br"


@pytest.mark.django_db
def test_o_banco_recusa_email_repetido_mesmo_com_outra_caixa():
    Pessoa.objects.create_user(email="carlos.mendes@exemplo.edu.br", nome="Carlos Mendes")

    with pytest.raises(IntegrityError):
        Pessoa.objects.create_user(email="CARLOS.MENDES@exemplo.edu.br", nome="Outra pessoa")


@pytest.mark.django_db
def test_pessoa_precisa_de_email():
    with pytest.raises(ValueError, match="e-mail"):
        Pessoa.objects.create_user(email="", nome="Sem e-mail")
