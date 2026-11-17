"""Login de desenvolvimento: POST /api/dev/entrar (ACE-T24).

Requisito verificado: ACE-RNF-03 (em produção, a única forma de entrar é o login institucional).
"""

import importlib
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.urls import clear_url_caches
from rest_framework.test import APIClient

import farol.urls
from farol.testes.test_configuracoes import VARIAVEIS_DE_PRODUCAO, carregar_producao


@pytest.fixture
def sem_login_de_desenvolvimento():
    """Recarrega as rotas com o login de desenvolvimento desligado, como em produção."""
    with override_settings(FAROL_LOGIN_DESENVOLVIMENTO=False):
        importlib.reload(farol.urls)
        clear_url_caches()
        yield
    importlib.reload(farol.urls)
    clear_url_caches()


def test_entra_pelo_email_e_abre_a_sessao(cliente, aluna):
    resposta = cliente.post("/api/dev/entrar", {"email": "ana.souza@exemplo.edu.br"}, format="json")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "id": aluna.id,
        "email": "ana.souza@exemplo.edu.br",
        "nome": "Ana Souza",
        "perfis": ["aluno"],
        "perfil_ativo": "aluno",
        "precisa_ver_aviso": True,
    }
    # A sessão ficou aberta: as outras rotas já reconhecem a pessoa.
    assert cliente.get("/api/eu").json()["email"] == "ana.souza@exemplo.edu.br"


def test_o_email_vale_sem_diferenciar_maiusculas_nem_espacos(cliente, professor):
    resposta = cliente.post(
        "/api/dev/entrar", {"email": "  Carlos.Mendes@EXEMPLO.edu.br "}, format="json"
    )

    assert resposta.status_code == 200
    assert resposta.json()["id"] == professor.id


@pytest.mark.parametrize("email", ["ninguem@exemplo.edu.br", "", "isto-nao-e-email"])
def test_email_desconhecido_ou_invalido_e_recusado_sem_abrir_sessao(cliente, aluna, email):
    resposta = cliente.post("/api/dev/entrar", {"email": email}, format="json")

    assert resposta.status_code == 400
    assert cliente.get("/api/eu").status_code == 401


def test_pessoa_desativada_nao_entra(cliente, aluna):
    aluna.is_active = False
    aluna.save()

    resposta = cliente.post("/api/dev/entrar", {"email": aluna.email}, format="json")

    assert resposta.status_code == 400


@pytest.mark.requisito("ACE-RNF-03")
def test_com_o_login_de_desenvolvimento_desligado_a_rota_nao_existe(
    aluna, sem_login_de_desenvolvimento
):
    resposta = APIClient().post("/api/dev/entrar", {"email": aluna.email}, format="json")

    assert resposta.status_code == 404
    assert APIClient().get("/api/eu").status_code == 401


@pytest.mark.requisito("ACE-RNF-03")
def test_a_configuracao_de_producao_desliga_o_login_de_desenvolvimento(monkeypatch):
    for nome, valor in VARIAVEIS_DE_PRODUCAO.items():
        monkeypatch.setenv(nome, valor)
    # Nem uma variável de ambiente consegue ligar o atalho em produção.
    monkeypatch.setenv("FAROL_LOGIN_DESENVOLVIMENTO", "true")

    assert carregar_producao().FAROL_LOGIN_DESENVOLVIMENTO is False


@pytest.mark.requisito("ACE-RNF-03")
def test_so_o_desenvolvimento_e_o_teste_ligam_o_login_de_desenvolvimento():
    from farol.configuracoes import desenvolvimento, teste

    assert desenvolvimento.FAROL_LOGIN_DESENVOLVIMENTO is True
    assert teste.FAROL_LOGIN_DESENVOLVIMENTO is True
    assert "farol.configuracoes.producao" not in sys.modules


def test_importar_a_configuracao_de_producao_continua_exigindo_as_variaveis(monkeypatch):
    for nome in VARIAVEIS_DE_PRODUCAO:
        monkeypatch.delenv(nome, raising=False)

    with pytest.raises(ImproperlyConfigured):
        carregar_producao()
