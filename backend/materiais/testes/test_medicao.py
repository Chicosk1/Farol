"""O PDF de 40 páginas fica pronto bem antes da meta de 2 minutos (MAT-T90, MAT-RNF-01).

Com o provedor falso, mede a parte do Farol (leitura, divisão e gravação). O tempo com o provedor
real é medido no servidor com o mesmo comando.
"""

from io import StringIO

import pytest
from django.core.management import call_command

from materiais.models import Material


@pytest.fixture(autouse=True)
def arquivos_temporarios(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.mark.requisito("MAT-RNF-01")
def test_pdf_de_40_paginas_fica_pronto_dentro_da_meta(db):
    saida = StringIO()

    call_command("medir_processamento", stdout=saida)

    assert "40 páginas" in saida.getvalue()
    assert "status pronto" in saida.getvalue()
    assert "dentro da meta" in saida.getvalue()
    assert not Material.objects.exists()  # a medição não deixa nada no banco
