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

# A IA é sempre o adaptador falso nos testes, mesmo com FAROL_IA_ADAPTADOR no ambiente, e com o
# limite de similaridade calibrado para ele.
FAROL_IA = {"ADAPTADOR": "ia.adaptadores.falso.ProvedorFalso"}
FAROL_TUTOR_SIMILARIDADE_MINIMA = 0.3

# Credencial fictícia do Google: os testes simulam a resposta dele (contas/testes/test_login.py).
FAROL_DOMINIO_INSTITUCIONAL = "exemplo.edu.br"
FAROL_GOOGLE_CLIENT_ID = "cliente-de-teste.apps.googleusercontent.com"
FAROL_GOOGLE_SECRET = "segredo-de-teste"
SOCIALACCOUNT_PROVIDERS = login_do_google(  # noqa: F405
    FAROL_DOMINIO_INSTITUCIONAL, FAROL_GOOGLE_CLIENT_ID, FAROL_GOOGLE_SECRET
)

# Os testes zeram o Redis a cada teste: usam um banco só deles, para não apagar o do ambiente.
FAROL_REDIS_URL = FAROL_REDIS_URL.rsplit("/", 1)[0] + "/15"  # noqa: F405
