"""Permissão por disciplina com o banco real e as funções de contas e disciplinas (ACE-T31).

Requisito verificado: ACE-RF-05 (o servidor confere, em toda operação, se a pessoa tem permissão
na disciplina envolvida). Todos os dados são fictícios.
"""

import pytest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from nucleo.permissoes import AcessoADisciplina, acesso_a_disciplina


@api_view(["GET"])
@permission_classes([AcessoADisciplina])
def rota_de_qualquer_papel(request, disciplina_id):
    return Response({"disciplina": disciplina_id})


@api_view(["GET"])
@permission_classes([acesso_a_disciplina(Perfil.PROFESSOR)])
def rota_so_do_professor(request, disciplina_id):
    return Response({"disciplina": disciplina_id})


def chamar(view, pessoa, disciplina_id, perfil_ativo=None):
    requisicao = APIRequestFactory().get(f"/teste/{disciplina_id}")
    requisicao.session = {"perfil_ativo": perfil_ativo} if perfil_ativo else {}
    if pessoa:
        force_authenticate(requisicao, user=pessoa)
    return view(requisicao, disciplina_id=disciplina_id)


@pytest.fixture
def disciplina(professor) -> Disciplina:
    return Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )


@pytest.fixture
def outra_pessoa(db) -> Pessoa:
    return Pessoa.objects.create_user(
        email="bruno.dias@exemplo.edu.br", nome="Bruno Dias", perfis=[Perfil.ALUNO]
    )


@pytest.mark.requisito("ACE-RF-05")
def test_aluno_matriculado_acessa_a_disciplina(aluna, disciplina):
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)

    assert chamar(rota_de_qualquer_papel, aluna, disciplina.id).status_code == 200


@pytest.mark.requisito("ACE-RF-05")
def test_professor_da_disciplina_acessa(professor, disciplina):
    assert chamar(rota_de_qualquer_papel, professor, disciplina.id).status_code == 200


@pytest.mark.requisito("ACE-RF-05")
def test_aluno_sem_matricula_e_negado(outra_pessoa, disciplina):
    assert chamar(rota_de_qualquer_papel, outra_pessoa, disciplina.id).status_code == 403


@pytest.mark.requisito("ACE-RF-05")
def test_matricula_encerrada_nao_da_acesso(aluna, disciplina):
    Matricula.objects.create(
        aluno=aluna, disciplina=disciplina, situacao=Matricula.Situacao.ENCERRADA
    )

    assert chamar(rota_de_qualquer_papel, aluna, disciplina.id).status_code == 403


@pytest.mark.requisito("ACE-RF-05")
def test_professor_de_outra_disciplina_e_negado(disciplina):
    outro = Pessoa.objects.create_user(
        email="marta.ribeiro@exemplo.edu.br", nome="Marta Ribeiro", perfis=[Perfil.PROFESSOR]
    )

    assert chamar(rota_de_qualquer_papel, outro, disciplina.id).status_code == 403


@pytest.mark.requisito("ACE-RF-05")
def test_disciplina_que_nao_existe_tambem_e_negada_sem_revelar_se_existe(aluna):
    assert chamar(rota_de_qualquer_papel, aluna, 999_999).status_code == 403


@pytest.mark.requisito("ACE-RF-05")
def test_sem_login_a_resposta_e_negada(disciplina):
    resposta = chamar(rota_de_qualquer_papel, None, disciplina.id)

    assert resposta.status_code in (401, 403)


@pytest.mark.requisito("ACE-RF-05")
def test_o_acesso_segue_o_perfil_em_uso(disciplina, professor):
    """Quem tem dois perfis só vale como aluno ou como professor, conforme o perfil ativo."""
    professor.perfis = [Perfil.PROFESSOR, Perfil.ALUNO]
    professor.save()

    como_professor = chamar(rota_de_qualquer_papel, professor, disciplina.id, "professor")
    como_aluno = chamar(rota_de_qualquer_papel, professor, disciplina.id, "aluno")

    assert como_professor.status_code == 200
    assert como_aluno.status_code == 403  # como aluno, não tem matrícula nela


@pytest.mark.requisito("ACE-RF-05")
def test_rota_restrita_ao_professor_nega_o_aluno_matriculado(aluna, professor, disciplina):
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)

    assert chamar(rota_so_do_professor, aluna, disciplina.id).status_code == 403
    assert chamar(rota_so_do_professor, professor, disciplina.id).status_code == 200


@pytest.mark.requisito("ACE-RF-05")
def test_perfis_sem_regra_de_acesso_sao_negados(disciplina):
    admin = Pessoa.objects.create_user(
        email="ti@exemplo.edu.br", nome="Equipe de TI", perfis=[Perfil.ADMIN]
    )

    assert chamar(rota_de_qualquer_papel, admin, disciplina.id).status_code == 403
