"""Geração dos rascunhos em segundo plano, validação e descarte (QUE-T20, QUE-T21).

O provedor é o falso; nos casos de resposta ruim, o teste troca a resposta dele. Dados fictícios.
"""

import json

import pytest
from django.conf import settings

from disciplinas.models import Disciplina
from ia import servicos as ia
from materiais.models import Material, Trecho
from questoes import servicos, tarefas
from questoes.models import PedidoGeracao, Questao

PILHA = "A pilha segue a regra LIFO: o último elemento a entrar é o primeiro a sair dela."
FILA = "A fila segue a regra FIFO: o primeiro elemento a entrar é o primeiro a sair dela."
ARVORE = "Uma árvore binária de busca guarda os menores valores na subárvore da esquerda."


def vetor() -> list[float]:
    return [1.0] + [0.0] * (settings.FAROL_DIMENSAO_DO_VETOR - 1)


@pytest.fixture
def disciplina(professor) -> Disciplina:
    return Disciplina.objects.create(
        codigo="SINF201",
        nome="Estruturas de Dados",
        turma="SINF2NA",
        semestre="2026/2",
        professor=professor,
    )


def aula(disciplina, numero: int, textos: list[str], status=Material.Status.PRONTO) -> Material:
    material = Material.objects.create(
        disciplina=disciplina,
        aula_numero=numero,
        aula_titulo=f"Aula {numero}",
        arquivo=f"materiais/aula-{numero}.pdf",
        status=status,
    )
    for ordem, texto in enumerate(textos):
        Trecho.objects.create(
            material=material,
            pagina=ordem + 1,
            ordem=0,
            texto=texto,
            inicio=0,
            fim=len(texto),
            vetor=vetor(),
        )
    return material


@pytest.fixture
def material(disciplina) -> Material:
    return aula(disciplina, 3, [PILHA, FILA])


def pedido(material, professor, quantidade=5) -> PedidoGeracao:
    return PedidoGeracao.objects.create(
        material=material, quantidade=quantidade, pedido_por=professor
    )


def questao_valida(trecho=1, **campos) -> dict:
    return {
        "enunciado": "Qual regra a pilha segue?",
        "alternativas": ["LIFO", "FIFO", "Por prioridade", "Aleatória"],
        "correta": 0,
        "justificativa": "Na pilha, o último a entrar é o primeiro a sair.",
        "topico": "Pilhas",
        "trecho": trecho,
    } | campos


@pytest.fixture
def modelo(monkeypatch):
    """Troca a resposta do provedor e guarda o que ele recebeu."""

    class Modelo:
        resposta: str | Exception | None = None
        chamadas: list[tuple] = []

    original = ia.gerar_questoes

    def gerar(regras, trechos, quantidade):
        Modelo.chamadas.append((regras, trechos, quantidade))
        if isinstance(Modelo.resposta, Exception):
            raise Modelo.resposta
        if Modelo.resposta is None:
            return original(regras, trechos, quantidade)
        return Modelo.resposta

    monkeypatch.setattr(ia, "gerar_questoes", gerar)
    Modelo.chamadas = []
    return Modelo


@pytest.mark.requisito("QUE-RF-02")
def test_a_tarefa_gera_os_rascunhos_pendentes_marcados_como_novos(material, professor):
    novo = pedido(material, professor, quantidade=6)

    assert tarefas.gerar.delay(novo.id).get() == PedidoGeracao.Status.PRONTO

    novo.refresh_from_db()
    assert (novo.geradas, novo.descartadas) == (6, 0)
    assert novo.terminado_em is not None
    rascunhos = Questao.objects.filter(pedido=novo)
    assert rascunhos.count() == 6
    for rascunho in rascunhos:
        assert rascunho.status == Questao.Status.PENDENTE
        assert rascunho.nova is True
        assert rascunho.material == material
        assert rascunho.trecho.material == material
        assert rascunho.alternativas[rascunho.correta] in rascunho.trecho.texto


@pytest.mark.requisito("QUE-RF-02")
def test_o_modelo_recebe_as_regras_fixas_e_so_os_trechos_da_aula_pedida(
    disciplina, material, professor, modelo
):
    aula(disciplina, 4, [ARVORE])

    servicos.processar_pedido(pedido(material, professor, quantidade=5).id)

    [(regras, trechos, quantidade)] = modelo.chamadas
    assert regras == servicos.REGRAS_DAS_QUESTOES
    assert "Use só o que está nos trechos" in regras
    assert [t.texto for t in trechos] == [PILHA, FILA]
    assert [t.numero for t in trechos] == [1, 2]
    assert quantidade == 5


@pytest.mark.requisito("QUE-RF-03")
def test_rascunho_citando_trecho_que_nao_e_da_aula_e_descartado(material, professor, modelo):
    modelo.resposta = json.dumps({"questoes": [questao_valida(1), questao_valida(3)]})
    novo = pedido(material, professor)

    servicos.processar_pedido(novo.id)

    novo.refresh_from_db()
    assert (novo.geradas, novo.descartadas) == (1, 1)
    [rascunho] = Questao.objects.filter(pedido=novo)
    assert rascunho.trecho.texto == PILHA


@pytest.mark.requisito("QUE-RF-03")
def test_rascunho_fora_do_formato_e_descartado(material, professor, modelo):
    modelo.resposta = json.dumps(
        {"questoes": [questao_valida(alternativas=["LIFO", "FIFO"]), questao_valida(2)]}
    )
    novo = pedido(material, professor)

    servicos.processar_pedido(novo.id)

    assert Questao.objects.filter(pedido=novo).count() == 1
    assert Questao.objects.get(pedido=novo).trecho.texto == FILA


@pytest.mark.requisito("QUE-RF-03")
def test_sem_nenhum_rascunho_valido_o_pedido_termina_com_erro(material, professor, modelo):
    modelo.resposta = "Desculpe, não consegui."
    novo = pedido(material, professor)

    servicos.processar_pedido(novo.id)

    novo.refresh_from_db()
    assert novo.status == PedidoGeracao.Status.ERRO
    assert not Questao.objects.exists()


def test_provedor_fora_do_ar_termina_com_erro_sem_rascunhos(material, professor, modelo):
    modelo.resposta = RuntimeError("provedor fora do ar")
    novo = pedido(material, professor)

    servicos.processar_pedido(novo.id)

    novo.refresh_from_db()
    assert novo.status == PedidoGeracao.Status.ERRO
    assert not Questao.objects.exists()


def test_aula_que_nao_esta_pronta_nao_gera_nada(disciplina, professor, modelo):
    retirada = aula(disciplina, 5, [PILHA], status=Material.Status.RETIRADO)
    novo = pedido(retirada, professor)

    servicos.processar_pedido(novo.id)

    novo.refresh_from_db()
    assert novo.status == PedidoGeracao.Status.ERRO
    assert modelo.chamadas == []


def test_trechos_curtos_como_titulos_nao_vao_para_o_modelo(disciplina, professor, modelo):
    material = aula(disciplina, 6, ["Aula 6", PILHA])

    servicos.processar_pedido(pedido(material, professor).id)

    [(_, trechos, _)] = modelo.chamadas
    assert [t.texto for t in trechos] == [PILHA]


def test_aula_longa_manda_trechos_espalhados_ate_o_limite(disciplina, professor, modelo):
    textos = [f"{PILHA} Exemplo número {i} da aula, com detalhes." for i in range(80)]
    material = aula(disciplina, 7, textos)

    servicos.processar_pedido(pedido(material, professor).id)

    [(_, trechos, _)] = modelo.chamadas
    assert len(trechos) == servicos.TRECHOS_POR_PEDIDO
    assert trechos[0].texto == textos[0]
    assert trechos[-1].texto != textos[servicos.TRECHOS_POR_PEDIDO - 1]  # chega ao fim da aula


def test_processar_o_mesmo_pedido_duas_vezes_nao_duplica_os_rascunhos(material, professor):
    novo = pedido(material, professor)

    servicos.processar_pedido(novo.id)
    servicos.processar_pedido(novo.id)

    assert Questao.objects.filter(pedido=novo).count() == 5
