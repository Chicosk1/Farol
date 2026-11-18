"""A primeira palavra do tutor chega dentro da meta de 3 s no p95 (TUT-T92, TUT-RNF-01).

Com o provedor falso e perguntas simultâneas, mede a busca e o começo da resposta no Farol. O
tempo com o provedor real é medido no servidor com o mesmo comando.
"""

from io import StringIO

import pytest
from django.core.management import call_command

from disciplinas.models import Disciplina
from ia import servicos as ia
from materiais.models import Material, Trecho
from tutor.management.commands.medir_tutor import percentil_95

TEXTO = "Uma lista encadeada é formada por nós com ponteiros para o próximo nó."


@pytest.mark.requisito("TUT-RNF-01")
@pytest.mark.django_db(transaction=True)  # as perguntas simultâneas abrem conexões próprias
def test_primeira_palavra_dentro_da_meta_com_perguntas_simultaneas(professor):
    disciplina = Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    material = Material.objects.create(
        disciplina=disciplina,
        aula_numero=4,
        aula_titulo="Listas",
        arquivo="x.pdf",
        status=Material.Status.PRONTO,
    )
    Trecho.objects.create(
        material=material,
        pagina=1,
        ordem=0,
        texto=TEXTO,
        inicio=0,
        fim=len(TEXTO),
        vetor=ia.gerar_embedding(TEXTO),
    )
    saida = StringIO()

    call_command("medir_tutor", disciplina=disciplina.id, perguntas=10, simultaneas=3, stdout=saida)

    assert "dentro da meta" in saida.getvalue()


def test_o_percentil_95():
    assert percentil_95([1.0] * 19 + [10.0]) == pytest.approx(1.45)
    assert percentil_95([2.0]) == 2.0
