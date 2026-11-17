"""Quando o material não responde, o tutor diz isso sem chamar o modelo (TUT-T31, TUT-T30).

Cenários 1 e 2 da História 2 da spec 003: pergunta sem trecho relevante e pergunta
administrativa recebem "Não encontrei isso no material da disciplina.", e o modelo de linguagem
nem é chamado, o que também economiza custo. A IA é o adaptador falso. Dados fictícios.
"""

from unittest import mock

import pytest
from django.test import override_settings

from disciplinas.models import Disciplina
from ia import servicos as ia
from materiais.models import Material, Trecho
from tutor import servicos
from tutor.servicos import Citacao, Fim, Texto

TEXTOS = [
    "Uma lista encadeada é formada por nós com ponteiros para o próximo nó.",
    "Uma pilha segue a ordem LIFO: o último elemento inserido é o primeiro a sair.",
    "Uma árvore binária tem no máximo dois filhos por nó, esquerdo e direito.",
]


@pytest.fixture
def disciplina(professor) -> Disciplina:
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
        aula_titulo="Estruturas lineares",
        arquivo="x.pdf",
        status=Material.Status.PRONTO,
    )
    for pagina, texto in enumerate(TEXTOS, start=1):
        Trecho.objects.create(
            material=material,
            pagina=pagina,
            ordem=0,
            texto=texto,
            inicio=0,
            fim=len(texto),
            vetor=ia.gerar_embedding(texto),
        )
    return disciplina


def perguntar(disciplina, pergunta: str, modo_pistas: bool = False) -> list:
    return list(servicos.responder_pergunta(disciplina.id, pergunta, modo_pistas=modo_pistas))


@pytest.mark.requisito("TUT-RF-04")
@pytest.mark.parametrize(
    "pergunta",
    [
        "Isso cai na prova?",
        "Qual é a data da prova final?",
        "Quanto vale a presença na nota?",
        "Qual é a capital da França?",
    ],
)
def test_pergunta_sem_base_no_material_responde_nao_encontrei_sem_chamar_o_modelo(
    disciplina, pergunta
):
    with mock.patch.object(servicos.ia, "responder") as modelo:
        eventos = perguntar(disciplina, pergunta)

    modelo.assert_not_called()
    assert [e.texto for e in eventos if isinstance(e, Texto)] == [
        "Não encontrei isso no material da disciplina."
    ]
    fim = eventos[-1]
    assert isinstance(fim, Fim)
    assert fim.tipo == "nao_encontrado"
    assert (fim.tokens_entrada, fim.tokens_saida) == (0, 0)  # sem custo de modelo
    assert not [e for e in eventos if isinstance(e, Citacao)]


@pytest.mark.requisito("TUT-RF-04")
def test_pergunta_sem_nenhuma_palavra_util_tambem_responde_nao_encontrei(disciplina):
    with mock.patch.object(servicos.ia, "responder") as modelo:
        eventos = perguntar(disciplina, "??? !!")

    modelo.assert_not_called()
    assert eventos[-1].tipo == "nao_encontrado"


@pytest.mark.requisito("TUT-RF-01")
def test_pergunta_que_o_material_explica_chama_o_modelo_so_com_os_trechos_relevantes(
    disciplina,
):
    with mock.patch.object(servicos.ia, "responder", wraps=servicos.ia.responder) as modelo:
        eventos = perguntar(disciplina, "O que é uma lista encadeada?")

    modelo.assert_called_once()
    trechos_enviados = modelo.call_args.args[1]
    assert [t.texto for t in trechos_enviados] == [TEXTOS[0]]  # só o que passa do limite
    assert eventos[-1].tipo == "resposta"
    (citacao,) = [e for e in eventos if isinstance(e, Citacao)]
    assert citacao.rotulo == "Aula 4, p. 1"


@pytest.mark.requisito("TUT-RF-01")
def test_disciplina_sem_material_pronto_responde_nao_encontrei(disciplina):
    Material.objects.update(status=Material.Status.RETIRADO)

    with mock.patch.object(servicos.ia, "responder") as modelo:
        eventos = perguntar(disciplina, "O que é uma lista encadeada?")

    modelo.assert_not_called()
    assert eventos[-1].tipo == "nao_encontrado"


def test_o_limite_de_similaridade_vem_da_configuracao(disciplina):
    with (
        override_settings(FAROL_TUTOR_SIMILARIDADE_MINIMA=0.99),
        mock.patch.object(servicos.ia, "responder") as modelo,
    ):
        eventos = perguntar(disciplina, "O que é uma lista encadeada?")

    modelo.assert_not_called()
    assert eventos[-1].tipo == "nao_encontrado"
