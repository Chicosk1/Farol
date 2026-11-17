"""Toda rota com disciplina na URL confere a permissão por disciplina (ACE-T32, ACE-CS-03).

Esquecer a permissão numa rota nova é o jeito mais fácil de abrir um acesso indevido. Este teste
percorre todas as rotas da API e falha se alguma que recebe `disciplina_id` não usar
nucleo.permissoes.AcessoADisciplina.
"""

import pytest
from django.urls import URLPattern, URLResolver, get_resolver

from nucleo.permissoes import AcessoADisciplina


def todas_as_rotas(padroes=None, prefixo=""):
    for padrao in padroes if padroes is not None else get_resolver().url_patterns:
        texto = prefixo + str(padrao.pattern)
        if isinstance(padrao, URLResolver):
            yield from todas_as_rotas(padrao.url_patterns, texto)
        elif isinstance(padrao, URLPattern):
            yield texto, padrao.callback


def rotas_com_disciplina():
    return [(texto, view) for texto, view in todas_as_rotas() if "disciplina_id" in texto]


@pytest.mark.requisito("ACE-CS-03")
def test_existem_rotas_com_disciplina_para_o_teste_valer_alguma_coisa():
    assert rotas_com_disciplina(), "nenhuma rota com disciplina_id encontrada"


@pytest.mark.requisito("ACE-CS-03")
@pytest.mark.parametrize(("texto", "view"), rotas_com_disciplina(), ids=lambda v: str(v)[:60])
def test_a_rota_exige_acesso_a_disciplina(texto, view):
    permissoes = getattr(view.cls, "permission_classes", [])

    assert any(issubclass(p, AcessoADisciplina) for p in permissoes), (
        f"{texto} recebe disciplina_id mas não usa AcessoADisciplina (nucleo/permissoes.py)"
    )
