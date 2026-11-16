"""Configurações comuns a todos os ambientes."""

from pathlib import Path

from . import ambiente

# Pasta backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    # Módulos do Farol (ADR 0007)
    "nucleo",
    "contas",
    "disciplinas",
    "demonstracao",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Funções dos módulos que o núcleo usa na permissão por disciplina (nucleo/permissoes.py).
# Indicá-las aqui mantém o núcleo sem depender de contas nem de disciplinas (ADR 0007).
FAROL_ACESSO = {
    "PERFIL_ATIVO": "contas.servicos.perfil_ativo",
    "ACESSO_A_DISCIPLINA": "disciplinas.servicos.tem_acesso",
}

# Atalho para entrar sem o login institucional (POST /api/dev/entrar). Desligado por padrão:
# só as configurações de desenvolvimento e de teste ligam (ACE-RNF-03).
FAROL_LOGIN_DESENVOLVIMENTO = False

ROOT_URLCONF = "farol.urls"
WSGI_APPLICATION = "farol.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    },
]

# PostgreSQL com pgvector (ADR 0004). Os padrões servem ao Docker Compose de desenvolvimento;
# a produção exige todas as variáveis (producao.py).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": ambiente.opcional("POSTGRES_DB", "farol"),
        "USER": ambiente.opcional("POSTGRES_USER", "farol"),
        "PASSWORD": ambiente.opcional("POSTGRES_PASSWORD", "farol"),
        "HOST": ambiente.opcional("POSTGRES_HOST", "localhost"),
        "PORT": ambiente.opcional("POSTGRES_PORT", "5432"),
    }
}

# Pessoa é o usuário desde a primeira migração: o Django não permite trocar depois.
AUTH_USER_MODEL = "contas.Pessoa"

# O Farol não guarda senhas (ACE-RF-02): a entrada é pela conta institucional.
AUTH_PASSWORD_VALIDATORS: list[dict] = []

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Arquivos enviados (importações, e depois os PDFs dos professores). Em desenvolvimento e nos
# testes ficam numa pasta local; em produção, o armazenamento é escolhido na fase 0 (ADR 0008).
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Tarefas em segundo plano: Celery com a fila no Redis (docs/arquitetura.md).
CELERY_BROKER_URL = ambiente.opcional("REDIS_URL", "redis://localhost:6379/0")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_IGNORE_RESULT = True

# E-mail: no desenvolvimento, o Mailpit captura tudo (ADR 0008).
EMAIL_HOST = ambiente.opcional("EMAIL_HOST", "localhost")
EMAIL_PORT = int(ambiente.opcional("EMAIL_PORT", "1025"))
DEFAULT_FROM_EMAIL = ambiente.opcional("DEFAULT_FROM_EMAIL", "Farol <nao-responda@farol.local>")

# API: sessão do Django na mesma origem, sem JWT (ADR 0007). Toda rota exige login,
# a não ser que diga o contrário, como a rota de saúde.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["nucleo.api.autenticacao.AutenticacaoPorSessao"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Contrato da API em OpenAPI, gerado do código e versionado em backend/openapi.yaml.
# O front-end gera os seus tipos a partir dele (ADR 0007).
SPECTACULAR_SETTINGS = {
    "TITLE": "API do Farol",
    "DESCRIPTION": "API REST do Farol, tutor de estudos com IA da UNIMATER.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    # Um só nome para o conjunto de perfis, nos campos perfis, perfil_ativo e perfil.
    "ENUM_NAME_OVERRIDES": {"PerfilEnum": "contas.models.Perfil.choices"},
}
