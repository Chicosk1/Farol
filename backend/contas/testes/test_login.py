"""Login institucional com o Google (ACE-T20, ACE-T21).

O teste percorre o fluxo de verdade do django-allauth: a ida ao Google e a volta pela rota de
retorno. Só a troca do código pelo token, que iria à internet, é simulada: o "Google" devolve um
id_token com os dados da conta escolhida.
"""

import time
from unittest import mock
from urllib.parse import parse_qs, urlparse

import jwt
import pytest
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa

DOMINIO = "exemplo.edu.br"


def _conta_do_google(email: str, *, hd: str | None = DOMINIO, verificado=True, nome="") -> dict:
    dados = {
        "iss": "https://accounts.google.com",
        "aud": settings.FAROL_GOOGLE_CLIENT_ID,
        "sub": f"google-{email}",
        "iat": int(time.time()),
        "exp": int(time.time()) + 300,
        "email": email,
        "email_verified": verificado,
        "name": nome,
    }
    if hd:
        dados["hd"] = hd
    return dados


def _entrar_pelo_google(cliente: APIClient, conta: dict | None, erro: str | None = None):
    """Clica em "Entrar com o Google", escolhe a conta no Google e volta ao Farol."""
    ida = cliente.post("/contas/google/login/")
    assert ida.status_code == 302
    estado = parse_qs(urlparse(ida["Location"]).query)["state"][0]
    if erro:
        return cliente.get("/contas/google/login/callback/", {"error": erro, "state": estado})

    id_token = jwt.encode(conta, "assinatura-ignorada", algorithm="HS256")
    resposta_do_google = mock.Mock(status_code=200, headers={"content-type": "application/json"})
    resposta_do_google.json.return_value = {
        "access_token": "token-de-acesso",
        "expires_in": 3600,
        "token_type": "Bearer",
        "id_token": id_token,
    }
    with mock.patch(
        "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.get_requests_session"
    ) as sessao:
        sessao.return_value.__enter__.return_value.request.return_value = resposta_do_google
        return cliente.get("/contas/google/login/callback/", {"code": "codigo", "state": estado})


def test_a_ida_ao_google_sugere_o_dominio_institucional(db):
    ida = APIClient().post("/contas/google/login/")

    destino = urlparse(ida["Location"])
    parametros = parse_qs(destino.query)
    assert destino.netloc == "accounts.google.com"
    assert parametros["hd"] == [DOMINIO]
    assert set(parametros["scope"][0].split()) == {"openid", "email", "profile"}
    assert parametros["redirect_uri"] == ["http://testserver/contas/google/login/callback/"]


@pytest.mark.requisito("ACE-RF-01")
def test_cenario_1_aluno_com_matricula_entra_e_chega_a_tela_inicial(aluna):
    cliente = APIClient()

    volta = _entrar_pelo_google(cliente, _conta_do_google("Ana.Souza@exemplo.edu.br"))

    assert volta.status_code == 302
    assert volta["Location"] == "/"
    eu = cliente.get("/api/eu").json()
    assert eu["id"] == aluna.id
    assert eu["perfil_ativo"] == "aluno"
    # A conta do Google ficou ligada à pessoa importada, sem criar outra.
    assert Pessoa.objects.count() == 1
    assert SocialAccount.objects.get(provider="google").user_id == aluna.id


@pytest.mark.requisito("ACE-RF-01")
@pytest.mark.parametrize(
    "conta",
    [
        {"email": "fulano@gmail.com", "hd": None},
        {"email": "fulano@outra-faculdade.edu.br", "hd": "outra-faculdade.edu.br"},
        # Conta pessoal do Google criada com o e-mail da instituição: não é do Workspace.
        {"email": "ana.souza@exemplo.edu.br", "hd": None},
        {"email": "ana.souza@exemplo.edu.br", "verificado": False},
    ],
    ids=["gmail", "outro-dominio", "conta-pessoal-com-email-institucional", "nao-verificado"],
)
def test_cenario_2_conta_de_fora_da_instituicao_nao_acessa_nada(aluna, conta):
    cliente = APIClient()
    dados = dict(conta)
    email = dados.pop("email")

    volta = _entrar_pelo_google(cliente, _conta_do_google(email, **dados))

    assert volta.status_code == 302
    assert volta["Location"] == "/entrar?erro=conta_externa"
    assert cliente.get("/api/eu").status_code == 401
    assert Pessoa.objects.count() == 1
    assert not SocialAccount.objects.exists()


@pytest.mark.requisito("ACE-RF-01", "ACE-RF-02")
def test_cenario_3_conta_institucional_nova_entra_como_aluno_sem_disciplinas(db):
    cliente = APIClient()

    volta = _entrar_pelo_google(
        cliente, _conta_do_google("bruno.lima@exemplo.edu.br", nome="Bruno Lima")
    )

    assert volta["Location"] == "/"
    pessoa = Pessoa.objects.get(email="bruno.lima@exemplo.edu.br")
    assert pessoa.nome == "Bruno Lima"
    assert pessoa.perfis == [Perfil.ALUNO]
    # Nenhuma senha própria (ACE-RF-02).
    assert not pessoa.has_usable_password()
    assert cliente.get("/api/eu").json()["email"] == "bruno.lima@exemplo.edu.br"
    assert cliente.get("/api/disciplinas").json() == []


def test_conta_nova_sem_nome_no_google_usa_o_nome_do_email(db):
    cliente = APIClient()

    _entrar_pelo_google(cliente, _conta_do_google("maria.clara@exemplo.edu.br"))

    assert Pessoa.objects.get(email="maria.clara@exemplo.edu.br").nome == "Maria Clara"


def test_pessoa_desativada_nao_entra(aluna):
    aluna.is_active = False
    aluna.save()
    cliente = APIClient()

    volta = _entrar_pelo_google(cliente, _conta_do_google(aluna.email))

    assert volta["Location"] == "/entrar?erro=conta_desativada"
    assert cliente.get("/api/eu").status_code == 401


def test_cancelar_no_google_volta_para_a_entrada(db):
    cliente = APIClient()

    volta = _entrar_pelo_google(cliente, None, erro="access_denied")

    assert volta.status_code == 302
    assert volta["Location"] == "/entrar?erro=falha"
    assert cliente.get("/api/eu").status_code == 401


@pytest.mark.requisito("ACE-RF-02")
def test_o_farol_nao_tem_cadastro_nem_senha_proprios(db):
    cliente = APIClient()

    for rota in ["/contas/signup/", "/contas/password/reset/", "/contas/login/"]:
        resposta = cliente.post(rota, {"email": "x@exemplo.edu.br", "password1": "s3nh4-f0rte!"})
        assert resposta.status_code in (302, 403, 404), rota
    assert not Pessoa.objects.exists()


def test_formas_de_entrar(db, settings):
    assert APIClient().get("/api/entrada").json() == {"google": True, "desenvolvimento": True}

    settings.FAROL_GOOGLE_CLIENT_ID = ""
    assert APIClient().get("/api/entrada").json()["google"] is False


def test_formas_de_entrar_entrega_o_cookie_csrf_para_o_formulario_do_google(db):
    resposta = APIClient().get("/api/entrada")

    assert "csrftoken" in resposta.cookies
