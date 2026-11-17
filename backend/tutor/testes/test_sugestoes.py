"""Sugestões de pergunta a partir dos títulos das aulas (TUT-T25, TUT-RF-14). Dados fictícios."""

import pytest

from disciplinas.models import Disciplina, Matricula
from materiais.models import Material
from tutor.models import Conversa, Mensagem


@pytest.fixture
def disciplina(professor, aluna) -> Disciplina:
    disciplina = Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )
    Matricula.objects.create(aluno=aluna, disciplina=disciplina)
    return disciplina


def material(disciplina, numero: int, titulo: str, status=Material.Status.PRONTO) -> Material:
    return Material.objects.create(
        disciplina=disciplina,
        aula_numero=numero,
        aula_titulo=titulo,
        arquivo="x.pdf",
        status=status,
    )


def sugestoes(cliente, disciplina) -> list[str]:
    return cliente.get(f"/api/disciplinas/{disciplina.id}/tutor").json()["sugestoes"]


@pytest.mark.requisito("TUT-RF-14")
def test_com_a_conversa_vazia_sugere_perguntas_das_tres_aulas_mais_recentes(
    cliente_aluna, disciplina
):
    material(disciplina, 2, "Busca binária")
    material(disciplina, 4, "Listas encadeadas")
    material(disciplina, 5, "Pilhas e filas")
    material(disciplina, 3, "Ordenação")

    assert sugestoes(cliente_aluna, disciplina) == [
        "Quais são as ideias principais da aula 5, Pilhas e filas?",
        "Quais são as ideias principais da aula 4, Listas encadeadas?",
        "Quais são as ideias principais da aula 3, Ordenação?",
    ]


@pytest.mark.requisito("TUT-RF-14")
def test_so_entram_aulas_com_material_pronto(cliente_aluna, disciplina):
    material(disciplina, 4, "Listas encadeadas")
    material(disciplina, 5, "Pilhas e filas", status=Material.Status.PROCESSANDO)
    material(disciplina, 6, "Árvores", status=Material.Status.RETIRADO)

    assert sugestoes(cliente_aluna, disciplina) == [
        "Quais são as ideias principais da aula 4, Listas encadeadas?"
    ]


@pytest.mark.requisito("TUT-RF-14")
def test_sem_material_ou_com_a_conversa_comecada_nao_ha_sugestoes(cliente_aluna, aluna, disciplina):
    assert sugestoes(cliente_aluna, disciplina) == []

    material(disciplina, 4, "Listas encadeadas")
    conversa = Conversa.objects.create(aluno=aluna, disciplina=disciplina)
    Mensagem.objects.create(conversa=conversa, autor="aluno", texto="O que é uma pilha?")

    assert sugestoes(cliente_aluna, disciplina) == []
