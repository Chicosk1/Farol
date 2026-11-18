"""Regras do módulo questoes (spec 005). Chamado pela API, pelas tarefas e por outros módulos."""

import logging

from django.db import transaction
from django.utils import timezone

from ia import servicos as ia
from ia.servicos import TrechoNumerado
from materiais import servicos as materiais

from .esquema import ler_questoes
from .models import PedidoGeracao, Questao

logger = logging.getLogger(__name__)

TRECHOS_POR_PEDIDO = 30  # cabe no contexto do modelo e cobre a aula toda
TAMANHO_MINIMO_DO_TRECHO = 40  # títulos e rodapés soltos não rendem questão

# Instruções fixas do modelo: o professor não as edita, e o servidor confere o resultado.
REGRAS_DAS_QUESTOES = """Você cria questões de múltipla escolha para alunos de graduação, só com o \
conteúdo dos trechos numerados do material de uma aula.

Regras:
1. Cada questão tem um enunciado, exatamente 4 alternativas, uma só correta, uma justificativa \
curta e o tópico (de 2 a 5 palavras).
2. Use só o que está nos trechos. Não invente fatos nem use conhecimento de fora.
3. Em "trecho", ponha o número do trecho de onde saiu a resposta correta.
4. As alternativas erradas devem ser plausíveis, mas erradas segundo o material.
5. Em "correta", ponha a posição da alternativa correta, de 0 a 3, variando entre as questões.
6. Escreva em português do Brasil.

Responda só com um JSON neste formato:
{"questoes": [{"enunciado": "...", "alternativas": ["...", "...", "...", "..."], \
"correta": 0, "justificativa": "...", "topico": "...", "trecho": 1}]}"""


def _terminar(pedido: PedidoGeracao, status: str, geradas: int = 0, descartadas: int = 0) -> None:
    pedido.status = status
    pedido.geradas = geradas
    pedido.descartadas = descartadas
    pedido.terminado_em = timezone.now()
    pedido.save(update_fields=["status", "geradas", "descartadas", "terminado_em"])


def processar_pedido(pedido_id: int) -> PedidoGeracao:
    """Gera os rascunhos do pedido e guarda só os que passam na validação (QUE-RF-02 e 03).

    Os rascunhos entram todos de uma vez, ou nenhum: o professor nunca vê um lote pela metade.
    Sem nenhum rascunho válido, o pedido termina com erro e o professor pode tentar de novo.
    """
    pedido = PedidoGeracao.objects.get(pk=pedido_id)
    if pedido.status != PedidoGeracao.Status.PROCESSANDO:
        return pedido  # já processado: a tarefa pode ser entregue duas vezes
    trechos = [
        trecho
        for trecho in materiais.trechos_da_aula(pedido.material_id, TRECHOS_POR_PEDIDO * 2)
        if len(trecho.texto.strip()) >= TAMANHO_MINIMO_DO_TRECHO
    ][:TRECHOS_POR_PEDIDO]
    if not trechos:
        _terminar(pedido, PedidoGeracao.Status.ERRO)
        return pedido
    por_numero = {numero: trecho for numero, trecho in enumerate(trechos, start=1)}
    numerados = [TrechoNumerado(numero, t.texto) for numero, t in por_numero.items()]
    try:
        texto = ia.gerar_questoes(REGRAS_DAS_QUESTOES, numerados, pedido.quantidade)
    except Exception:  # provedor fora do ar ou com erro: o professor tenta de novo
        logger.exception("Falha ao gerar as questões do pedido %s", pedido.id)
        _terminar(pedido, PedidoGeracao.Status.ERRO)
        return pedido
    leitura = ler_questoes(texto, set(por_numero), pedido.quantidade)
    with transaction.atomic():
        Questao.objects.bulk_create(
            Questao(
                material_id=pedido.material_id,
                pedido=pedido,
                enunciado=gerada.enunciado,
                alternativas=gerada.alternativas,
                correta=gerada.correta,
                justificativa=gerada.justificativa,
                topico=gerada.topico,
                trecho_id=por_numero[gerada.trecho].id,
            )
            for gerada in leitura.aceitas
        )
        status = PedidoGeracao.Status.PRONTO if leitura.aceitas else PedidoGeracao.Status.ERRO
        _terminar(pedido, status, len(leitura.aceitas), leitura.descartadas)
    return pedido
