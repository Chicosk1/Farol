"""Adaptador da API compatível com a da OpenAI (TUT-T14, ADR 0009).

Os testes sobem um servidor HTTP falso na própria máquina, que responde como o Ollama: nenhum
modelo de verdade é chamado e nada sai para a internet.
"""

import json
import math
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from ia.adaptadores.compativel_openai import ErroDoProvedor, ProvedorCompativelOpenAI
from ia.porta import EventoFim, EventoTexto, TrechoNumerado


class ServidorFalso:
    """Guarda os pedidos recebidos e responde o que o teste mandar."""

    def __init__(self):
        self.pedidos: list[dict] = []
        self.status = 200
        self.vetores: list[list[float]] | None = None
        self.pedacos = ["Uma pilha ", "segue a ordem LIFO. [1]"]
        self.uso: dict | None = {"prompt_tokens": 120, "completion_tokens": 9}
        servidor = self

        class Tratador(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                servidor.pedidos.append(
                    {"caminho": self.path, "corpo": corpo, "cabecalhos": dict(self.headers)}
                )
                if servidor.status != 200:
                    self.send_response(servidor.status)
                    self.end_headers()
                    self.wfile.write(b'{"error": "modelo nao encontrado"}')
                    return
                if self.path.endswith("/embeddings"):
                    self._vetores(corpo)
                else:
                    self._resposta()

            def _vetores(self, corpo):
                entradas = corpo["input"]
                vetores = servidor.vetores or [[float(i + 1)] * 768 for i in range(len(entradas))]
                # Fora de ordem de propósito: o adaptador ordena pelo índice.
                dados = [{"index": i, "embedding": vetor} for i, vetor in enumerate(vetores)][::-1]
                self._json({"data": dados, "model": corpo["model"]})

            def _resposta(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                for pedaco in servidor.pedacos:
                    evento = {"choices": [{"index": 0, "delta": {"content": pedaco}}]}
                    self.wfile.write(f"data: {json.dumps(evento)}\n\n".encode())
                fim = {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
                self.wfile.write(f"data: {json.dumps(fim)}\n\n".encode())
                if servidor.uso:
                    uso = {"choices": [], "usage": servidor.uso}
                    self.wfile.write(f"data: {json.dumps(uso)}\n\n".encode())
                self.wfile.write(b"data: [DONE]\n\n")

            def _json(self, dados):
                texto = json.dumps(dados).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(texto)))
                self.end_headers()
                self.wfile.write(texto)

        self.http = ThreadingHTTPServer(("127.0.0.1", 0), Tratador)
        self.endereco = f"http://127.0.0.1:{self.http.server_port}/v1"
        threading.Thread(target=self.http.serve_forever, daemon=True).start()


@pytest.fixture
def servidor(settings):
    falso = ServidorFalso()
    settings.FAROL_IA_COMPATIVEL_OPENAI = {
        "ENDERECO": falso.endereco,
        "CHAVE": "",
        "MODELO_DE_RESPOSTAS": "gemma3:4b",
        "MODELO_DE_VETORES": "embeddinggemma",
        "TEMPO_LIMITE": 5,
    }
    yield falso
    falso.http.shutdown()


TRECHOS = [
    TrechoNumerado(1, "Uma pilha segue a ordem LIFO: o último a entrar é o primeiro a sair."),
    TrechoNumerado(2, "Uma fila segue a ordem FIFO."),
]


def test_os_vetores_sao_cortados_no_tamanho_do_banco_e_normalizados(servidor, settings):
    vetores = ProvedorCompativelOpenAI().embeddings(["pilha", "fila"])

    assert [len(v) for v in vetores] == [settings.FAROL_DIMENSAO_DO_VETOR] * 2
    for vetor in vetores:
        assert math.isclose(math.sqrt(sum(x * x for x in vetor)), 1.0)
    pedido = servidor.pedidos[0]
    assert pedido["caminho"] == "/v1/embeddings"
    assert pedido["corpo"] == {"model": "embeddinggemma", "input": ["pilha", "fila"]}


def test_os_vetores_voltam_na_ordem_dos_textos(servidor):
    servidor.vetores = [[1.0, 0.0] + [0.0] * 766, [0.0, 1.0] + [0.0] * 766]

    primeiro, segundo = ProvedorCompativelOpenAI().embeddings(["a", "b"])

    assert primeiro[0] == 1.0
    assert segundo[1] == 1.0


def test_muitos_textos_vao_em_lotes(servidor):
    ProvedorCompativelOpenAI().embeddings([f"texto {i}" for i in range(70)])

    assert [len(p["corpo"]["input"]) for p in servidor.pedidos] == [32, 32, 6]


def test_vetor_menor_que_o_do_banco_e_erro(servidor):
    servidor.vetores = [[1.0] * 100]

    with pytest.raises(ErroDoProvedor):
        ProvedorCompativelOpenAI().embeddings(["pilha"])


def test_a_resposta_chega_em_pedacos_e_termina_com_o_uso_de_tokens(servidor):
    eventos = list(ProvedorCompativelOpenAI().responder("REGRAS", TRECHOS, "O que é pilha?"))

    assert eventos == [
        EventoTexto("Uma pilha "),
        EventoTexto("segue a ordem LIFO. [1]"),
        EventoFim(tokens_entrada=120, tokens_saida=9),
    ]


def test_as_regras_vao_como_sistema_e_os_trechos_numerados_com_a_pergunta(servidor):
    list(ProvedorCompativelOpenAI().responder("REGRAS DO TUTOR", TRECHOS, "O que é pilha?"))

    corpo = servidor.pedidos[0]["corpo"]
    assert servidor.pedidos[0]["caminho"] == "/v1/chat/completions"
    assert corpo["model"] == "gemma3:4b"
    assert corpo["stream"] is True
    sistema, usuario = corpo["messages"]
    assert sistema == {"role": "system", "content": "REGRAS DO TUTOR"}
    assert usuario["role"] == "user"
    assert "[1] Uma pilha segue a ordem LIFO" in usuario["content"]
    assert "[2] Uma fila segue a ordem FIFO." in usuario["content"]
    assert usuario["content"].endswith("O que é pilha?")


def test_sem_o_uso_na_resposta_os_tokens_sao_estimados(servidor):
    servidor.uso = None

    fim = list(ProvedorCompativelOpenAI().responder("REGRAS", TRECHOS, "O que é pilha?"))[-1]

    assert isinstance(fim, EventoFim)
    assert fim.tokens_entrada > 0
    assert fim.tokens_saida > 0


def test_a_chave_vai_no_cabecalho_so_quando_existe(servidor, settings):
    ProvedorCompativelOpenAI().embeddings(["pilha"])
    settings.FAROL_IA_COMPATIVEL_OPENAI = {
        **settings.FAROL_IA_COMPATIVEL_OPENAI,
        "CHAVE": "chave-de-teste",
    }
    ProvedorCompativelOpenAI().embeddings(["pilha"])

    assert "Authorization" not in servidor.pedidos[0]["cabecalhos"]
    assert servidor.pedidos[1]["cabecalhos"]["Authorization"] == "Bearer chave-de-teste"


def test_erro_do_provedor_aparece_ja_no_primeiro_pedaco(servidor):
    servidor.status = 500
    eventos = ProvedorCompativelOpenAI().responder("REGRAS", TRECHOS, "O que é pilha?")

    with pytest.raises(ErroDoProvedor, match="500"):
        next(eventos)


def test_provedor_fora_do_ar_e_erro_do_provedor(servidor, settings):
    servidor.http.shutdown()
    servidor.http.server_close()

    with pytest.raises(ErroDoProvedor):
        ProvedorCompativelOpenAI().embeddings(["pilha"])
    with pytest.raises(ErroDoProvedor):
        next(ProvedorCompativelOpenAI().responder("REGRAS", TRECHOS, "O que é pilha?"))


def test_os_testes_do_farol_usam_sempre_o_adaptador_falso(settings):
    assert settings.FAROL_IA["ADAPTADOR"] == "ia.adaptadores.falso.ProvedorFalso"
