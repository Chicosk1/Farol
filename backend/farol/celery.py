"""App do Celery: tarefas em segundo plano, como ler PDFs, gerar questões e montar o radar.

Cada módulo põe as suas tarefas em `<modulo>/tarefas.py`, e elas só chamam serviços (ADR 0007).
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "farol.configuracoes.desenvolvimento")

app = Celery("farol")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(related_name="tarefas")
