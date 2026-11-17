"""Armazenamento de arquivos pela API do Django, em pasta indicada por variável (MAT-T11).

O mesmo código serve ao volume do Docker (desenvolvimento e testes) e, em produção, ao disco do
servidor com backup ou a um serviço compatível com S3, sem mudar o código (ADR 0008).
"""

import importlib
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage

from farol.testes.test_configuracoes import VARIAVEIS_DE_PRODUCAO, carregar_producao

MODULO_BASE = "farol.configuracoes.base"


def carregar_base():
    sys.modules.pop(MODULO_BASE, None)
    try:
        return importlib.import_module(MODULO_BASE)
    finally:
        sys.modules.pop(MODULO_BASE, None)
        importlib.import_module(MODULO_BASE)


def test_o_armazenamento_padrao_grava_e_le_arquivos_na_pasta_configurada(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    nome = default_storage.save("materiais/aula-1.pdf", ContentFile(b"%PDF-1.4 conteudo"))

    assert isinstance(default_storage, FileSystemStorage)
    assert (tmp_path / nome).read_bytes() == b"%PDF-1.4 conteudo"
    with default_storage.open(nome) as arquivo:
        assert arquivo.read() == b"%PDF-1.4 conteudo"


def test_a_pasta_dos_arquivos_vem_da_variavel_farol_arquivos(monkeypatch):
    monkeypatch.setenv("FAROL_ARQUIVOS", "/arquivos")

    assert str(carregar_base().MEDIA_ROOT) == "/arquivos"


def test_sem_a_variavel_a_pasta_padrao_fica_dentro_do_backend(monkeypatch):
    monkeypatch.delenv("FAROL_ARQUIVOS", raising=False)

    base = carregar_base()

    assert base.MEDIA_ROOT == base.BASE_DIR / "media"


def test_producao_exige_a_pasta_dos_arquivos(monkeypatch):
    for nome, valor in VARIAVEIS_DE_PRODUCAO.items():
        monkeypatch.setenv(nome, valor)
    monkeypatch.setenv("FAROL_ARQUIVOS", "/dados/arquivos")
    assert str(carregar_producao().MEDIA_ROOT) == "/dados/arquivos"

    monkeypatch.delenv("FAROL_ARQUIVOS")
    with pytest.raises(ImproperlyConfigured, match="FAROL_ARQUIVOS"):
        carregar_producao()
