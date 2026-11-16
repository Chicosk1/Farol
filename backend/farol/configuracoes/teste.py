"""Configurações dos testes (pytest), localmente e no GitHub Actions.

Os testes usam o PostgreSQL do Docker, nunca SQLite (docs/qualidade-e-testes.md).
"""

from .base import *  # noqa: F403

DEBUG = False

FAROL_LOGIN_DESENVOLVIMENTO = True

SECRET_KEY = "teste-nao-secreto"

ALLOWED_HOSTS = ["testserver", "localhost"]

# As tarefas do Celery rodam na hora, sem fila, e os erros aparecem no teste.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
