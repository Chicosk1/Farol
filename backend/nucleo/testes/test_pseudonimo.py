"""Identificador pseudônimo do aluno por disciplina (TUT-T91, TUT-RF-12).

Permite contar alunos distintos (regra dos 5 alunos do radar) sem revelar quem são: o mesmo aluno
tem o mesmo identificador numa disciplina, mas identificadores diferentes em disciplinas
diferentes, e o identificador não mostra o id nem permite descobri-lo sem o segredo.
"""

import re

import pytest
from django.test import override_settings

from nucleo.pseudonimo import pseudonimo_do_aluno


@pytest.mark.requisito("TUT-RF-12")
def test_o_mesmo_aluno_na_mesma_disciplina_tem_sempre_o_mesmo_identificador():
    assert pseudonimo_do_aluno(7, 3) == pseudonimo_do_aluno(7, 3)


@pytest.mark.requisito("TUT-RF-12")
def test_alunos_diferentes_na_mesma_disciplina_tem_identificadores_diferentes():
    identificadores = {pseudonimo_do_aluno(aluno, 3) for aluno in range(1, 201)}

    assert len(identificadores) == 200  # dá para contar alunos distintos


@pytest.mark.requisito("TUT-RF-12")
def test_o_mesmo_aluno_em_disciplinas_diferentes_tem_identificadores_diferentes():
    assert pseudonimo_do_aluno(7, 3) != pseudonimo_do_aluno(7, 4)


@pytest.mark.requisito("TUT-RF-12")
def test_o_identificador_e_um_hash_que_nao_mostra_o_id_do_aluno():
    identificador = pseudonimo_do_aluno(123456, 3)

    assert re.fullmatch(r"[0-9a-f]{64}", identificador)
    assert "123456" not in identificador


@pytest.mark.requisito("TUT-RF-12")
def test_sem_o_segredo_nao_ha_como_refazer_o_identificador():
    com_segredo_a = pseudonimo_do_aluno(7, 3)

    with override_settings(FAROL_SEGREDO_DO_PSEUDONIMO="outro-segredo"):
        com_segredo_b = pseudonimo_do_aluno(7, 3)

    assert com_segredo_a != com_segredo_b
