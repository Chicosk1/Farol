"""Configurações por ambiente, lidas de variáveis (ACE-T11)."""

import importlib
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

MODULO_PRODUCAO = "farol.configuracoes.producao"

VARIAVEIS_DE_PRODUCAO = {
    "DJANGO_SECRET_KEY": "chave-de-teste-nao-secreta",
    "DJANGO_ALLOWED_HOSTS": "farol.exemplo.edu.br, www.farol.exemplo.edu.br",
    "POSTGRES_DB": "farol",
    "POSTGRES_USER": "farol",
    "POSTGRES_PASSWORD": "senha-de-teste",
    "POSTGRES_HOST": "db",
    "FAROL_ARQUIVOS": "/arquivos",
    "FAROL_SEGREDO_PSEUDONIMO": "segredo-de-teste-do-pseudonimo",
    "FAROL_IA_ADAPTADOR": "ia.adaptadores.falso.ProvedorFalso",
}


def carregar_producao():
    """Importa o módulo de produção do zero, como o Django faria ao iniciar."""
    sys.modules.pop(MODULO_PRODUCAO, None)
    try:
        return importlib.import_module(MODULO_PRODUCAO)
    finally:
        sys.modules.pop(MODULO_PRODUCAO, None)


@pytest.fixture
def ambiente_de_producao(monkeypatch):
    for nome, valor in VARIAVEIS_DE_PRODUCAO.items():
        monkeypatch.setenv(nome, valor)
    return monkeypatch


def test_producao_le_tudo_das_variaveis_de_ambiente(ambiente_de_producao):
    producao = carregar_producao()

    assert producao.DEBUG is False
    assert producao.SECRET_KEY == "chave-de-teste-nao-secreta"
    assert producao.ALLOWED_HOSTS == ["farol.exemplo.edu.br", "www.farol.exemplo.edu.br"]
    assert producao.DATABASES["default"]["HOST"] == "db"
    assert producao.DATABASES["default"]["PASSWORD"] == "senha-de-teste"


@pytest.mark.parametrize(
    "variavel", ["DJANGO_SECRET_KEY", "DJANGO_ALLOWED_HOSTS", "POSTGRES_PASSWORD"]
)
def test_producao_nao_sobe_sem_uma_variavel_obrigatoria(ambiente_de_producao, variavel):
    ambiente_de_producao.delenv(variavel)

    with pytest.raises(ImproperlyConfigured, match=variavel):
        carregar_producao()


@pytest.mark.django_db
def test_nao_ha_migracao_pendente():
    # makemigrations --check termina com SystemExit quando falta gerar uma migração.
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)


@pytest.mark.requisito("ACE-RNF-02")
def test_producao_exige_https_e_so_manda_cookies_por_conexao_segura(ambiente_de_producao):
    producao = carregar_producao()

    assert producao.SECURE_SSL_REDIRECT is True
    assert producao.SESSION_COOKIE_SECURE is True
    assert producao.CSRF_COOKIE_SECURE is True
    assert producao.SECURE_HSTS_SECONDS == 365 * 24 * 3600
    assert producao.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    assert producao.CSRF_TRUSTED_ORIGINS == [
        "https://farol.exemplo.edu.br",
        "https://www.farol.exemplo.edu.br",
    ]


@pytest.mark.requisito("ACE-RNF-02")
def test_a_sessao_expira_apos_12_horas_sem_uso_e_o_prazo_e_configuravel(ambiente_de_producao):
    from django.conf import settings

    assert settings.SESSION_COOKIE_AGE == 12 * 3600
    assert settings.SESSION_SAVE_EVERY_REQUEST is True  # cada uso renova o prazo

    ambiente_de_producao.setenv("FAROL_SESSAO_HORAS", "8")
    sys.modules.pop("farol.configuracoes.base", None)
    try:
        assert carregar_producao().SESSION_COOKIE_AGE == 8 * 3600
    finally:
        sys.modules.pop("farol.configuracoes.base", None)


@pytest.mark.requisito("ACE-RNF-02")
def test_o_cookie_de_sessao_sai_com_o_prazo_de_expiracao(db, client):
    from contas.models import Perfil, Pessoa

    Pessoa.objects.create_user(
        email="ana.souza@exemplo.edu.br", nome="Ana Souza", perfis=[Perfil.ALUNO]
    )
    resposta = client.post(
        "/api/dev/entrar", {"email": "ana.souza@exemplo.edu.br"}, content_type="application/json"
    )

    assert resposta.status_code == 200
    assert resposta.cookies["sessionid"]["max-age"] == 12 * 3600
