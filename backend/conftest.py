"""Fixtures comuns a todos os testes do back-end. Todos os dados são fictícios."""

import pytest
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa


@pytest.fixture
def cliente() -> APIClient:
    """Cliente de API sem login."""
    return APIClient()


@pytest.fixture
def aluna(db) -> Pessoa:
    return Pessoa.objects.create_user(
        email="ana.souza@exemplo.edu.br", nome="Ana Souza", perfis=[Perfil.ALUNO]
    )


@pytest.fixture
def professor(db) -> Pessoa:
    return Pessoa.objects.create_user(
        email="carlos.mendes@exemplo.edu.br", nome="Carlos Mendes", perfis=[Perfil.PROFESSOR]
    )


@pytest.fixture
def cliente_aluna(aluna) -> APIClient:
    cliente = APIClient()
    cliente.force_login(aluna)
    return cliente


@pytest.fixture
def cliente_professor(professor) -> APIClient:
    cliente = APIClient()
    cliente.force_login(professor)
    return cliente


@pytest.fixture
def admin(db) -> Pessoa:
    return Pessoa.objects.create_user(
        email="equipe.ti@exemplo.edu.br", nome="Equipe de TI", perfis=[Perfil.ADMIN]
    )


@pytest.fixture
def cliente_admin(admin) -> APIClient:
    cliente = APIClient()
    cliente.force_login(admin)
    return cliente
