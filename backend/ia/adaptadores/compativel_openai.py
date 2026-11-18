"""Adaptador para a API compatível com a da OpenAI (ADR 0009).

Fala com o Ollama do Docker Compose e com qualquer provedor que ofereça as rotas
`/v1/chat/completions` (com streaming) e `/v1/embeddings`. Usa só a biblioteca padrão, sem SDK.
O endereço, os modelos e a chave vêm de FAROL_IA_COMPATIVEL_OPENAI (variáveis FAROL_IA_*).
"""

import json
import math
import urllib.error
import urllib.request
from collections.abc import Iterator

from django.conf import settings

from ..porta import EventoFim, EventoResposta, EventoTexto, TrechoNumerado

TEXTOS_POR_LOTE = 32  # vetores pedidos de uma vez: o processamento de um PDF gera centenas
CARACTERES_POR_TOKEN = 4  # estimativa, quando o provedor não informa o uso


class ErroDoProvedor(RuntimeError):
    """O provedor não respondeu, ou respondeu com erro. O tutor mostra "indisponível"."""


def _configuracao() -> dict:
    return settings.FAROL_IA_COMPATIVEL_OPENAI


def _pedir(caminho: str, corpo: dict):
    """Envia o pedido e devolve a resposta aberta, ou ErroDoProvedor."""
    configuracao = _configuracao()
    cabecalhos = {"Content-Type": "application/json"}
    if configuracao["CHAVE"]:
        cabecalhos["Authorization"] = f"Bearer {configuracao['CHAVE']}"
    pedido = urllib.request.Request(
        configuracao["ENDERECO"].rstrip("/") + caminho,
        data=json.dumps(corpo).encode(),
        headers=cabecalhos,
        method="POST",
    )
    try:
        return urllib.request.urlopen(pedido, timeout=configuracao["TEMPO_LIMITE"])
    except urllib.error.HTTPError as erro:
        detalhe = erro.read()[:300].decode(errors="replace")
        raise ErroDoProvedor(f"O provedor de IA respondeu {erro.code}: {detalhe}") from erro
    except OSError as erro:  # URLError, recusa de conexão e tempo esgotado
        raise ErroDoProvedor(f"Não foi possível falar com o provedor de IA: {erro}") from erro


def _no_tamanho_do_banco(vetor: list[float]) -> list[float]:
    """Corta o vetor no tamanho do banco e devolve o comprimento a 1.

    Vale para modelos treinados para isso (Matryoshka), como o embeddinggemma: as primeiras
    posições do vetor já guardam o essencial do significado.
    """
    dimensao = settings.FAROL_DIMENSAO_DO_VETOR
    if len(vetor) < dimensao:
        raise ErroDoProvedor(
            f"O modelo de vetores devolveu {len(vetor)} posições; o banco usa {dimensao}."
        )
    cortado = vetor[:dimensao]
    comprimento = math.sqrt(sum(x * x for x in cortado))
    if comprimento == 0:
        raise ErroDoProvedor("O modelo de vetores devolveu um vetor nulo.")
    return [x / comprimento for x in cortado]


def _mensagens(regras: str, trechos: list[TrechoNumerado], pergunta: str) -> list[dict]:
    """As regras vão como instrução do sistema; os trechos e a pergunta, separados, como usuário."""
    material = "\n\n".join(f"[{trecho.numero}] {trecho.texto}" for trecho in trechos)
    return [
        {"role": "system", "content": regras},
        {
            "role": "user",
            "content": f"Trechos do material:\n\n{material}\n\nPergunta do aluno: {pergunta}",
        },
    ]


def _eventos_do_stream(resposta) -> Iterator[dict]:
    """Os objetos JSON das linhas `data:` do stream (SSE), até o `[DONE]`."""
    for linha in resposta:
        linha = linha.decode().strip()
        if not linha.startswith("data:"):
            continue
        dados = linha.removeprefix("data:").strip()
        if dados == "[DONE]":
            return
        yield json.loads(dados)


class ProvedorCompativelOpenAI:
    def embeddings(self, textos: list[str]) -> list[list[float]]:
        modelo = _configuracao()["MODELO_DE_VETORES"]
        vetores: list[list[float]] = []
        for inicio in range(0, len(textos), TEXTOS_POR_LOTE):
            lote = textos[inicio : inicio + TEXTOS_POR_LOTE]
            with _pedir("/embeddings", {"model": modelo, "input": lote}) as resposta:
                dados = json.load(resposta)["data"]
            if len(dados) != len(lote):
                raise ErroDoProvedor("O provedor devolveu um número errado de vetores.")
            ordenados = sorted(dados, key=lambda item: item["index"])
            vetores.extend(_no_tamanho_do_banco(item["embedding"]) for item in ordenados)
        return vetores

    def responder(
        self, regras: str, trechos: list[TrechoNumerado], pergunta: str
    ) -> Iterator[EventoResposta]:
        """Gerador: o pedido só sai no primeiro `next`, e a falha aparece ali mesmo."""
        mensagens = _mensagens(regras, trechos, pergunta)
        corpo = {
            "model": _configuracao()["MODELO_DE_RESPOSTAS"],
            "messages": mensagens,
            "stream": True,
            "stream_options": {"include_usage": True},
            "temperature": 0.2,  # respostas presas ao material, pouco criativas
        }
        uso = None
        produzido = 0
        with _pedir("/chat/completions", corpo) as resposta:
            for evento in _eventos_do_stream(resposta):
                uso = evento.get("usage") or uso
                for escolha in evento.get("choices") or []:
                    texto = (escolha.get("delta") or {}).get("content")
                    if texto:
                        produzido += len(texto)
                        yield EventoTexto(texto)
        if uso:
            yield EventoFim(uso["prompt_tokens"], uso["completion_tokens"])
        else:
            entrada = sum(len(m["content"]) for m in mensagens)
            yield EventoFim(
                max(1, entrada // CARACTERES_POR_TOKEN), max(1, produzido // CARACTERES_POR_TOKEN)
            )
