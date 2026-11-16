"""Contrato da API (ACE-T15): o OpenAPI versionado em backend/openapi.yaml é o que o código gera.

Para atualizar o arquivo depois de mudar uma rota:
    python manage.py spectacular --file openapi.yaml --validate --fail-on-warn
"""

from pathlib import Path

import pytest
import yaml
from django.conf import settings
from django.core.management import call_command

CONTRATO_VERSIONADO = Path(settings.BASE_DIR) / "openapi.yaml"


@pytest.fixture
def contrato_gerado(tmp_path) -> str:
    destino = tmp_path / "openapi.yaml"
    call_command("spectacular", "--file", str(destino), "--validate", "--fail-on-warn")
    return destino.read_text(encoding="utf-8")


def test_contrato_versionado_esta_atualizado(contrato_gerado):
    assert CONTRATO_VERSIONADO.read_text(encoding="utf-8") == contrato_gerado, (
        "backend/openapi.yaml está desatualizado. Rode: "
        "python manage.py spectacular --file openapi.yaml --validate --fail-on-warn"
    )


def test_contrato_descreve_a_rota_de_saude_sem_login(contrato_gerado):
    esquema = yaml.safe_load(contrato_gerado)
    operacao = esquema["paths"]["/api/saude"]["get"]

    referencia = operacao["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    componente = esquema["components"]["schemas"][referencia.rsplit("/", 1)[-1]]
    assert componente["properties"]["status"]["type"] == "string"
    assert componente["required"] == ["status"]
    # Uma exigência de segurança vazia ({}) quer dizer que a rota aceita quem não entrou.
    assert {} in operacao["security"]
