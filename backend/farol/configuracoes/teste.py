"""Configurações dos testes (pytest), localmente e no GitHub Actions.

Os testes usam o PostgreSQL do Docker, nunca SQLite (docs/qualidade-e-testes.md).
"""

from .base import *  # noqa: F403

DEBUG = False

SECRET_KEY = "teste-nao-secreto"

ALLOWED_HOSTS = ["testserver", "localhost"]
