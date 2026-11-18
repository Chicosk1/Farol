"""POST /api/disciplinas/{id}/tutor/perguntas: a pergunta e a resposta em streaming (TUT-T23).

A resposta chega em eventos SSE: inicio, texto (aos poucos), citacao e fim. A pergunta é filtrada
antes de ir ao provedor e de ser guardada; o registro de uso só leva o identificador pseudônimo.
A IA é o adaptador falso. Dados fictícios.
"""

import json
from unittest import mock

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from disciplinas.models import Disciplina, Matricula
from ia import servicos as ia
from materiais.models import Material, Trecho
from nucleo.pseudonimo import pseudonimo_do_aluno
from tutor import servicos
from tutor.models import Citacao, Conversa, Mensagem, RegistroUso

LISTA = "Uma lista encadeada é formada por nós com ponteiros para o próximo nó."
PILHA = "Uma pilha segue a ordem LIFO: o último elemento inserido é o primeiro a sair."


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
    material = Material.objects.create(
        disciplina=disciplina,
        aula_numero=4,
        aula_titulo="Estruturas lineares",
        arquivo="x.pdf",
        status=Material.Status.PRONTO,
    )
    for pagina, texto in ((5, LISTA), (7, PILHA)):
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


def url(disciplina) -> str:
    return f"/api/disciplinas/{disciplina.id}/tutor/perguntas"


def perguntar(cliente, disciplina, texto: str):
    return cliente.post(url(disciplina), {"texto": texto}, format="json")


def eventos_de(resposta) -> list[tuple[str, dict]]:
    corpo = b"".join(resposta.streaming_content).decode()
    eventos = []
    for bloco in corpo.strip().split("\n\n"):
        linhas = dict(linha.split(": ", 1) for linha in bloco.split("\n"))
        eventos.append((linhas["event"], json.loads(linhas["data"])))
    return eventos


@pytest.mark.requisito("TUT-RF-13")
@override_settings(FAROL_TUTOR_SIMILARIDADE_MINIMA=0.1)  # para os dois trechos entrarem
def test_a_resposta_chega_em_eventos_sse_inicio_texto_citacao_e_fim(cliente_aluna, disciplina):
    resposta = perguntar(cliente_aluna, disciplina, "Compare a lista encadeada e a pilha")

    assert resposta.status_code == 200
    assert resposta["Content-Type"].startswith("text/event-stream")
    assert resposta["Cache-Control"] == "no-cache"
    eventos = eventos_de(resposta)
    tipos = [tipo for tipo, _ in eventos]
    assert tipos[0] == "inicio" and tipos[-1] == "fim"
    assert tipos.count("texto") >= 2  # aos poucos, uma frase de cada vez
    assert "citacao" in tipos


@pytest.mark.requisito("TUT-RF-02")
def test_a_resposta_tem_citacao_aula_e_pagina_que_abre_o_material(cliente_aluna, disciplina):
    eventos = eventos_de(perguntar(cliente_aluna, disciplina, "O que é uma lista encadeada?"))

    (citacao,) = [dados for tipo, dados in eventos if tipo == "citacao"]
    trecho = Trecho.objects.get(pagina=5)
    assert citacao == {
        "ordem": 1,
        "rotulo": "Aula 4, p. 5",
        "trecho_id": trecho.id,
        "material_id": trecho.material_id,
        "pagina": 5,
    }
    texto = "".join(dados["texto"] for tipo, dados in eventos if tipo == "texto")
    assert "[1]" in texto and "lista encadeada" in texto.lower()
    assert eventos[-1][1]["tipo"] == "resposta"


@pytest.mark.requisito("TUT-RF-12")
def test_a_conversa_fica_guardada_com_a_pergunta_a_resposta_e_as_citacoes(
    cliente_aluna, aluna, disciplina
):
    eventos = eventos_de(perguntar(cliente_aluna, disciplina, "O que é uma lista encadeada?"))

    conversa = Conversa.objects.get()
    assert (conversa.aluno, conversa.disciplina) == (aluna, disciplina)
    assert eventos[0][1] == {"conversa_id": conversa.id}
    pergunta, resposta = conversa.mensagens.all()
    assert (pergunta.autor, pergunta.texto) == ("aluno", "O que é uma lista encadeada?")
    assert (resposta.autor, resposta.tipo) == ("tutor", "resposta")
    assert eventos[-1][1]["mensagem_id"] == resposta.id
    assert [c.rotulo for c in Citacao.objects.filter(mensagem=resposta)] == ["Aula 4, p. 5"]


def test_a_segunda_pergunta_continua_na_mesma_conversa(cliente_aluna, disciplina):
    eventos_de(perguntar(cliente_aluna, disciplina, "O que é uma lista encadeada?"))
    eventos_de(perguntar(cliente_aluna, disciplina, "E uma pilha?"))

    assert Conversa.objects.count() == 1
    assert Mensagem.objects.count() == 4


@pytest.mark.requisito("TUT-RF-12")
def test_o_registro_de_uso_guarda_so_o_pseudonimo_a_pergunta_filtrada_e_os_trechos(
    cliente_aluna, aluna, disciplina
):
    eventos_de(perguntar(cliente_aluna, disciplina, "O que é uma lista encadeada?"))

    registro = RegistroUso.objects.get()
    assert registro.aluno_pseudonimo == pseudonimo_do_aluno(aluna.id, disciplina.id)
    assert registro.disciplina == disciplina
    assert registro.pergunta_filtrada == "O que é uma lista encadeada?"
    assert registro.trechos == [Trecho.objects.get(pagina=5).id]
    assert registro.tipo == "resposta"
    assert registro.tokens_entrada > 0 and registro.tokens_saida > 0


@pytest.mark.requisito("TUT-RF-11")
def test_dados_pessoais_saem_da_pergunta_antes_do_provedor_do_registro_e_do_historico(
    cliente_aluna, disciplina
):
    texto = "Sou Ana Souza, CPF 123.456.789-09, ana@exemplo.edu.br: o que é uma lista encadeada?"
    with mock.patch.object(servicos.ia, "responder", wraps=servicos.ia.responder) as modelo:
        eventos_de(perguntar(cliente_aluna, disciplina, texto))

    enviada = modelo.call_args.args[2]
    guardadas = [RegistroUso.objects.get().pergunta_filtrada, Mensagem.objects.first().texto]
    for texto_filtrado in [enviada, *guardadas]:
        for dado in ("Ana", "Souza", "123.456.789-09", "ana@exemplo.edu.br"):
            assert dado not in texto_filtrado
        assert "lista encadeada" in texto_filtrado


@pytest.mark.requisito("TUT-RF-04")
def test_pergunta_sem_base_responde_nao_encontrei_e_tambem_fica_registrada(
    cliente_aluna, disciplina
):
    eventos = eventos_de(perguntar(cliente_aluna, disciplina, "Isso cai na prova?"))

    assert eventos[-1][1]["tipo"] == "nao_encontrado"
    assert [d["texto"] for t, d in eventos if t == "texto"] == [
        "Não encontrei isso no material da disciplina."
    ]
    assert Mensagem.objects.last().tipo == "nao_encontrado"
    assert RegistroUso.objects.get().tipo == "nao_encontrado"


@pytest.mark.requisito("TUT-RF-05")
def test_o_modo_pistas_da_disciplina_vale_para_a_resposta(cliente_aluna, disciplina):
    eventos = eventos_de(
        perguntar(cliente_aluna, disciplina, "Me dá a resposta do exercício de pilha")
    )

    assert eventos[-1][1]["tipo"] == "pistas"  # o modo pistas vem ligado por padrão


@pytest.mark.parametrize("texto", ["", "   ", "x" * 1001])
def test_pergunta_vazia_ou_com_mais_de_1000_caracteres_recebe_400(cliente_aluna, disciplina, texto):
    assert perguntar(cliente_aluna, disciplina, texto).status_code == 400
    assert Mensagem.objects.count() == 0


def test_provedor_fora_do_ar_antes_da_resposta_recebe_503_e_nada_e_guardado(
    cliente_aluna, disciplina
):
    with mock.patch.object(servicos.ia, "responder", side_effect=RuntimeError("fora do ar")):
        resposta = perguntar(cliente_aluna, disciplina, "O que é uma lista encadeada?")

    assert resposta.status_code == 503
    assert Mensagem.objects.count() == 0
    assert RegistroUso.objects.count() == 0


def test_falha_no_meio_da_resposta_envia_um_evento_de_erro_e_guarda_a_mensagem_de_erro(
    cliente_aluna, disciplina
):
    def quebra_no_meio(*args):
        yield ia.EventoTexto("Uma lista encadeada é formada por nós. [1] Mais")
        raise RuntimeError("caiu")

    with mock.patch.object(servicos.ia, "responder", quebra_no_meio):
        eventos = eventos_de(perguntar(cliente_aluna, disciplina, "O que é uma lista encadeada?"))

    assert eventos[-1][0] == "erro"
    assert Mensagem.objects.last().tipo == "erro"


@pytest.mark.requisito("TUT-RF-12")
def test_professor_nao_pergunta_ao_tutor_como_aluno(cliente_professor, disciplina):
    assert perguntar(cliente_professor, disciplina, "O que é uma pilha?").status_code == 403


@pytest.mark.requisito("ACE-RF-05")
def test_aluno_sem_matricula_recebe_403_e_sem_login_recebe_401(cliente, disciplina):
    from contas.models import Perfil, Pessoa

    outro = Pessoa.objects.create_user(
        email="bruno.dias@exemplo.edu.br", nome="Bruno Dias", perfis=[Perfil.ALUNO]
    )
    cliente_do_outro = APIClient()
    cliente_do_outro.force_login(outro)

    assert perguntar(cliente_do_outro, disciplina, "O que é uma pilha?").status_code == 403
    assert perguntar(cliente, disciplina, "O que é uma pilha?").status_code == 401


@pytest.mark.requisito("TUT-RF-13")
def test_o_navegador_pede_eventos_e_recebe_a_resposta_em_streaming(cliente_aluna, disciplina):
    """O fetch do front-end manda Accept: text/event-stream (TUT-T29)."""
    resposta = cliente_aluna.post(
        url(disciplina),
        {"texto": "O que é uma lista encadeada?"},
        format="json",
        HTTP_ACCEPT="text/event-stream",
    )

    assert resposta.status_code == 200
    assert resposta["Content-Type"].startswith("text/event-stream")
    assert [tipo for tipo, _ in eventos_de(resposta)][0] == "inicio"


@pytest.mark.requisito("TUT-RF-13")
def test_a_recusa_vem_em_json_mesmo_quando_o_navegador_pede_eventos(cliente_aluna, disciplina):
    resposta = cliente_aluna.post(
        url(disciplina), {"texto": ""}, format="json", HTTP_ACCEPT="text/event-stream"
    )

    assert resposta.status_code == 400
    assert "texto" in json.loads(resposta.content)
