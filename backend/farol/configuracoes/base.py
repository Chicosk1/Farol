"""Configurações comuns a todos os ambientes."""

from pathlib import Path

from . import ambiente

# Pasta backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    # Módulos do Farol (ADR 0007)
    "nucleo",
    "contas",
    "disciplinas",
    "materiais",
    "duvidas",
    "notificacoes",
    "tutor",
    "ia",
    "demonstracao",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Funções dos módulos que o núcleo usa na permissão por disciplina (nucleo/permissoes.py).
# Indicá-las aqui mantém o núcleo sem depender de contas nem de disciplinas (ADR 0007).
FAROL_ACESSO = {
    "PERFIL_ATIVO": "contas.servicos.perfil_ativo",
    "ACESSO_A_DISCIPLINA": "disciplinas.servicos.tem_acesso",
}

# Limites do PDF de uma aula (spec 002, confirmados pelo dono do produto em 2026-11-18).
FAROL_PDF_MAX_BYTES = 50 * 1024 * 1024
FAROL_PDF_MAX_PAGINAS = 300

# Similaridade mínima (0 a 1) para um trecho valer como base da resposta do tutor. Abaixo dela, o
# tutor responde "não encontrei" sem chamar o modelo (TUT-RF-04). O valor foi calibrado com o
# adaptador falso e precisa ser recalibrado com o provedor real, pelo conjunto de avaliação.
FAROL_TUTOR_SIMILARIDADE_MINIMA = 0.3

# Preço do provedor de IA por mil tokens, em reais, para o custo de cada pergunta (TUT-RNF-05).
# Fica em zero até a escolha do provedor (ADR 0005).
FAROL_IA_PRECO_POR_MIL_TOKENS = {"entrada": "0", "saida": "0"}

# Orçamento de IA por aluno por mês, em reais (TUT-RNF-05). Acima dele, a equipe é avisada.
FAROL_IA_ORCAMENTO_POR_ALUNO_MES = "2.00"

# Segredo do identificador pseudônimo do aluno (nucleo/pseudonimo.py). Fica fora do banco; trocá-lo
# muda todos os identificadores. O padrão só serve ao desenvolvimento e aos testes.
FAROL_SEGREDO_DO_PSEUDONIMO = ambiente.opcional(
    "FAROL_SEGREDO_PSEUDONIMO", "pseudonimo-de-desenvolvimento-nao-use-em-producao"
)

# Tamanho dos vetores de busca dos trechos. É fixo no banco: trocar o modelo de embeddings por
# um de outro tamanho exige uma migração (docs/arquitetura.md).
FAROL_DIMENSAO_DO_VETOR = 256

# Provedor de IA, atrás do módulo ia. Por padrão (desenvolvimento e testes) é o adaptador falso;
# a produção precisa indicar o adaptador do provedor escolhido (ADR 0005).
FAROL_IA = {"ADAPTADOR": "ia.adaptadores.falso.ProvedorFalso"}

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
                "django.contrib.messages.context_processors.messages",
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

# Sessão: expira depois de um período sem uso (ACE-RNF-02). Cada requisição renova o prazo; o
# padrão de 12 horas foi confirmado pelo dono do produto (ACE-RNF-02).
FAROL_SESSAO_HORAS = int(ambiente.opcional("FAROL_SESSAO_HORAS", "12"))
SESSION_COOKIE_AGE = FAROL_SESSAO_HORAS * 3600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SAMESITE = "Lax"

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
MEDIA_ROOT = Path(ambiente.opcional("FAROL_ARQUIVOS", str(BASE_DIR / "media")))

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Tarefas em segundo plano: Celery com a fila no Redis (docs/arquitetura.md).
CELERY_BROKER_URL = ambiente.opcional("REDIS_URL", "redis://localhost:6379/0")

# Redis do contador diário de perguntas ao tutor (TUT-RF-08). O mesmo servidor da fila.
FAROL_REDIS_URL = CELERY_BROKER_URL
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_IGNORE_RESULT = True
# Tarefas agendadas (serviço beat do Docker Compose), chamadas pelo nome.
CELERY_BEAT_SCHEDULE = {
    "orcamento-de-ia": {
        "task": "tutor.verificar_orcamento",
        "schedule": 24 * 3600,  # uma vez por dia
    },
}

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
    "ENUM_NAME_OVERRIDES": {
        "PerfilEnum": "contas.models.Perfil.choices",
        "StatusDaImportacaoEnum": "disciplinas.models.StatusDaImportacao",
        "StatusDoMaterialEnum": "materiais.models.StatusDoMaterial",
    },
}
