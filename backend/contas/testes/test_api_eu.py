"""Rotas da própria pessoa: /api/eu, /api/eu/perfil-ativo e /api/sair (ACE-T22).

Requisito verificado: ACE-RF-03 (um ou mais perfis e troca de perfil sem sair).
"""

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa


@pytest.fixture
def professora_e_aluna(db) -> Pessoa:
    """Professora que também é aluna de pós-graduação: dois perfis."""
    return Pessoa.objects.create_user(
        email="marina.lopes@exemplo.edu.br",
        nome="Marina Lopes",
        perfis=[Perfil.PROFESSOR, Perfil.ALUNO],
    )


@pytest.fixture
def cliente_dois_perfis(professora_e_aluna) -> APIClient:
    cliente = APIClient()
    cliente.force_login(professora_e_aluna)
    return cliente


@pytest.mark.requisito("ACE-RF-03")
@pytest.mark.django_db
def test_pessoa_pode_ter_um_ou_mais_perfis_mas_so_os_conhecidos():
    pessoa = Pessoa.objects.create_user(
        email="x@exemplo.edu.br", nome="X", perfis=[Perfil.ALUNO, Perfil.ADMIN]
    )
    pessoa.refresh_from_db()
    assert pessoa.perfis == ["aluno", "admin"]

    pessoa.perfis = ["aluno", "diretor"]
    with pytest.raises(ValidationError):
        pessoa.full_clean()


def test_eu_exige_login_e_responde_401(cliente):
    resposta = cliente.get("/api/eu")

    assert resposta.status_code == 401


@pytest.mark.requisito("ACE-RF-03")
def test_eu_mostra_a_pessoa_e_o_perfil_ativo(cliente_aluna, aluna):
    resposta = cliente_aluna.get("/api/eu")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "id": aluna.id,
        "email": "ana.souza@exemplo.edu.br",
        "nome": "Ana Souza",
        "perfis": ["aluno"],
        "perfil_ativo": "aluno",
    }


@pytest.mark.requisito("ACE-RF-03")
def test_perfil_ativo_comeca_no_primeiro_perfil_da_pessoa(cliente_dois_perfis):
    assert cliente_dois_perfis.get("/api/eu").json()["perfil_ativo"] == "professor"


@pytest.mark.requisito("ACE-RF-03")
def test_pessoa_troca_de_perfil_sem_sair(cliente_dois_perfis):
    resposta = cliente_dois_perfis.post("/api/eu/perfil-ativo", {"perfil": "aluno"}, format="json")

    assert resposta.status_code == 200
    assert resposta.json()["perfil_ativo"] == "aluno"
    # A escolha vale para as próximas chamadas da mesma sessão.
    assert cliente_dois_perfis.get("/api/eu").json()["perfil_ativo"] == "aluno"


@pytest.mark.requisito("ACE-RF-03")
def test_a_escolha_de_perfil_vale_so_para_a_sessao_em_que_foi_feita(
    cliente_dois_perfis, professora_e_aluna
):
    cliente_dois_perfis.post("/api/eu/perfil-ativo", {"perfil": "aluno"}, format="json")

    outro_aparelho = APIClient()
    outro_aparelho.force_login(professora_e_aluna)

    assert outro_aparelho.get("/api/eu").json()["perfil_ativo"] == "professor"


@pytest.mark.requisito("ACE-RF-03")
@pytest.mark.parametrize("perfil", ["professor", "diretor", "", None])
def test_nao_troca_para_perfil_que_a_pessoa_nao_tem(cliente_aluna, perfil):
    resposta = cliente_aluna.post("/api/eu/perfil-ativo", {"perfil": perfil}, format="json")

    assert resposta.status_code == 400
    assert cliente_aluna.get("/api/eu").json()["perfil_ativo"] == "aluno"


def test_trocar_de_perfil_exige_login(cliente):
    resposta = cliente.post("/api/eu/perfil-ativo", {"perfil": "aluno"}, format="json")

    assert resposta.status_code == 401


def test_sair_encerra_a_sessao(cliente_aluna):
    assert cliente_aluna.get("/api/eu").status_code == 200

    resposta = cliente_aluna.post("/api/sair")

    assert resposta.status_code == 204
    assert cliente_aluna.get("/api/eu").status_code == 401


def test_sair_sem_estar_logado_tambem_responde_204(cliente):
    assert cliente.post("/api/sair").status_code == 204


def test_requisicao_que_muda_dados_logada_sem_token_csrf_e_recusada(aluna):
    cliente = APIClient(enforce_csrf_checks=True)
    cliente.force_login(aluna)

    resposta = cliente.post("/api/eu/perfil-ativo", {"perfil": "aluno"}, format="json")

    assert resposta.status_code == 403


def test_eu_entrega_o_cookie_do_token_csrf(cliente_aluna):
    resposta = cliente_aluna.get("/api/eu")

    assert "csrftoken" in resposta.cookies
