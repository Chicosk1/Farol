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
