"""Permissão por disciplina do núcleo, isolada dos outros módulos (ACE-T31).

O núcleo não depende de nenhum módulo (ADR 0007): quem decide se a pessoa tem acesso é uma função
configurada em FAROL_ACESSO. Aqui as funções são falsas; com as reais, o teste está em
farol/testes/test_acesso_a_disciplina.py.
"""

from types import SimpleNamespace

import pytest
from django.test import override_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate

from nucleo.permissoes import AcessoADisciplina, acesso_a_disciplina

PESSOA = SimpleNamespace(id=7, is_authenticated=True)
CONSULTAS: list[tuple] = []
PERMITIDAS = {10}


def perfil_falso(pessoa, sessao):
    return sessao.get("perfil")


def acesso_falso(pessoa, perfil, disciplina_id):
    CONSULTAS.append((pessoa.id, perfil, disciplina_id))
    return disciplina_id in PERMITIDAS


@pytest.fixture(autouse=True)
def funcoes_falsas():
    CONSULTAS.clear()
    with override_settings(
        FAROL_ACESSO={
            "PERFIL_ATIVO": f"{__name__}.perfil_falso",
            "ACESSO_A_DISCIPLINA": f"{__name__}.acesso_falso",
        }
    ):
        yield


@api_view(["GET"])
@permission_classes([AcessoADisciplina])
def qualquer_papel(request, disciplina_id):
    return Response({"ok": True})


@api_view(["GET"])
@permission_classes([acesso_a_disciplina("professor")])
def so_professor(request, disciplina_id):
    return Response({"ok": True})


def chamar(view, disciplina_id, perfil="aluno", autenticado=True):
    requisicao = APIRequestFactory().get("/x")
    requisicao.session = {"perfil": perfil}
    if autenticado:
        force_authenticate(requisicao, user=PESSOA)
    return view(requisicao, disciplina_id=disciplina_id)


def test_permite_quando_a_funcao_configurada_autoriza():
    assert chamar(qualquer_papel, 10).status_code == 200


def test_nega_quando_a_funcao_configurada_recusa():
    assert chamar(qualquer_papel, 11).status_code == 403


def test_a_funcao_recebe_a_pessoa_o_perfil_em_uso_e_a_disciplina_da_rota():
    chamar(qualquer_papel, 10, perfil="professor")

    assert CONSULTAS == [(7, "professor", 10)]


def test_sem_login_nem_chega_a_consultar_o_acesso():
    resposta = chamar(qualquer_papel, 10, autenticado=False)

    assert resposta.status_code in (401, 403)
    assert CONSULTAS == []


def test_rota_restrita_a_um_papel_nega_os_outros_sem_consultar_o_acesso():
    assert chamar(so_professor, 10, perfil="aluno").status_code == 403
    assert CONSULTAS == []
    assert chamar(so_professor, 10, perfil="professor").status_code == 200


def test_rota_sem_o_parametro_disciplina_id_e_negada_em_vez_de_liberada():
    @api_view(["GET"])
    @permission_classes([AcessoADisciplina])
    def mal_configurada(request):
        return Response({"ok": True})

    requisicao = APIRequestFactory().get("/x")
    requisicao.session = {"perfil": "aluno"}
    force_authenticate(requisicao, user=PESSOA)

    assert mal_configurada(requisicao).status_code == 403
