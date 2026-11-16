"""App do Celery: fila no Redis e tarefas descobertas em `<modulo>/tarefas.py` (ACE-T13)."""

import importlib
import sys

from django.conf import settings

from farol.celery import app

MODULO_BASE = "farol.configuracoes.base"


def carregar_base():
    """Importa as configurações comuns do zero, para ler as variáveis de ambiente de agora."""
    sys.modules.pop(MODULO_BASE, None)
    try:
        return importlib.import_module(MODULO_BASE)
    finally:
        sys.modules.pop(MODULO_BASE, None)
        importlib.import_module(MODULO_BASE)


def test_celery_usa_as_configuracoes_do_django():
    assert app.main == "farol"
    assert app.conf.broker_url == settings.CELERY_BROKER_URL
    assert app.conf.timezone == "America/Sao_Paulo"


def test_a_fila_vem_da_variavel_redis_url(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://fila.exemplo:6379/3")

    assert carregar_base().CELERY_BROKER_URL == "redis://fila.exemplo:6379/3"


def test_nos_testes_a_tarefa_roda_na_hora_sem_fila():
    @app.task(name="testes.somar")
    def somar(a: int, b: int) -> int:
        return a + b

    assert somar.delay(2, 3).get(timeout=1) == 5
