"""Configurações comuns a todos os ambientes."""

from pathlib import Path

from . import ambiente

# Pasta backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "rest_framework",
    # Módulos do Farol (ADR 0007)
    "nucleo",
    "contas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# API: sessão do Django na mesma origem, sem JWT (ADR 0007). Toda rota exige login,
# a não ser que diga o contrário, como a rota de saúde.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}
