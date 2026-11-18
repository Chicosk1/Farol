"""Configurações de produção. Tudo o que é sensível vem de variáveis de ambiente obrigatórias:
sem elas, o Django não sobe e diz qual variável falta.
"""

from pathlib import Path

from . import ambiente
from .base import *  # noqa: F403
from .base import DATABASES

DEBUG = False

# Em produção, a única forma de entrar é o login institucional (ACE-RNF-03).
# Fixo no código, de propósito: nenhuma variável de ambiente liga o atalho.
FAROL_LOGIN_DESENVOLVIMENTO = False

SECRET_KEY = ambiente.obrigatoria("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = ambiente.lista(ambiente.obrigatoria("DJANGO_ALLOWED_HOSTS"))

# Pasta dos arquivos enviados (PDFs e importações), em disco com backup. A escolha entre disco e
# S3 compatível fica para a fase 0 e não muda o código (ADR 0008).
MEDIA_ROOT = Path(ambiente.obrigatoria("FAROL_ARQUIVOS"))

# Sem segredo próprio, os identificadores pseudônimos seriam previsíveis.
FAROL_SEGREDO_DO_PSEUDONIMO = ambiente.obrigatoria("FAROL_SEGREDO_PSEUDONIMO")

# Em produção, o adaptador de IA é escolhido de propósito: nunca vale o falso por esquecimento.
FAROL_IA = {"ADAPTADOR": ambiente.obrigatoria("FAROL_IA_ADAPTADOR")}

DATABASES = {
    "default": {
        **DATABASES["default"],
        "NAME": ambiente.obrigatoria("POSTGRES_DB"),
        "USER": ambiente.obrigatoria("POSTGRES_USER"),
        "PASSWORD": ambiente.obrigatoria("POSTGRES_PASSWORD"),
        "HOST": ambiente.obrigatoria("POSTGRES_HOST"),
    }
}

# HTTPS em toda comunicação (ACE-RNF-02). O certificado fica no proxy à frente do Django, que
# avisa pelo cabeçalho X-Forwarded-Proto que a conexão original era segura.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(ambiente.opcional("DJANGO_HSTS_SEGUNDOS", str(365 * 24 * 3600)))
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]
