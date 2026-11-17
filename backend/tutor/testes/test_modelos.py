"""Modelos do tutor (TUT-T11). Dados fictícios."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from disciplinas.models import Disciplina
from materiais.models import Material, Trecho
from tutor.models import (
    Citacao,
    ConfiguracaoTutor,
    Conversa,
    JanelaProva,
    Mensagem,
    RegistroUso,
    RevisaoResposta,
)


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
def conversa(aluna, disciplina) -> Conversa:
    return Conversa.objects.create(aluno=aluna, disciplina=disciplina)


def test_a_configuracao_do_tutor_comeca_com_o_modo_pistas_ligado_e_limite_de_40(disciplina):
    configuracao = ConfiguracaoTutor.objects.create(disciplina=disciplina)

    assert configuracao.modo_pistas is True
    assert configuracao.limite_diario == 40
    assert configuracao.politica == ""


def test_cada_disciplina_tem_uma_so_configuracao(disciplina):
    ConfiguracaoTutor.objects.create(disciplina=disciplina)

    with pytest.raises(IntegrityError), transaction.atomic():
        ConfiguracaoTutor.objects.create(disciplina=disciplina)


@pytest.mark.parametrize("limite", [20, 40, 60])
def test_o_limite_diario_aceita_20_40_ou_60(disciplina, limite):
    ConfiguracaoTutor(disciplina=disciplina, limite_diario=limite).full_clean()


def test_o_limite_diario_recusa_outros_valores(disciplina):
    with pytest.raises(ValidationError):
        ConfiguracaoTutor(disciplina=disciplina, limite_diario=30).full_clean()


def test_mensagem_guarda_autor_tipo_e_avaliacao(conversa):
    pergunta = Mensagem.objects.create(
        conversa=conversa, autor=Mensagem.Autor.ALUNO, texto="O que é uma lista encadeada?"
    )
    resposta = Mensagem.objects.create(
        conversa=conversa,
        autor=Mensagem.Autor.TUTOR,
        texto="É uma sequência de nós.",
        tipo=Mensagem.Tipo.RESPOSTA,
    )

    assert pergunta.avaliacao == Mensagem.Avaliacao.NENHUMA
    assert [m.id for m in conversa.mensagens.all()] == [pergunta.id, resposta.id]


def test_o_tipo_da_mensagem_cobre_resposta_pistas_nao_encontrado_saudacao_e_erro():
    assert {t.value for t in Mensagem.Tipo} == {
        "resposta",
        "pistas",
        "nao_encontrado",
        "saudacao",
        "erro",
    }


def test_a_citacao_liga_a_mensagem_a_um_trecho_com_ordem(conversa, disciplina):
    material = Material.objects.create(
        disciplina=disciplina, aula_numero=4, aula_titulo="Listas", arquivo="x.pdf"
    )
    trecho = Trecho.objects.create(
        material=material, pagina=5, ordem=0, texto="t", inicio=0, fim=1, vetor=[0.0] * 256
    )
    mensagem = Mensagem.objects.create(conversa=conversa, autor=Mensagem.Autor.TUTOR, texto="x")

    citacao = Citacao.objects.create(mensagem=mensagem, trecho=trecho, ordem=1)

    assert citacao.rotulo == "Aula 4, p. 5"
    assert list(mensagem.citacoes.all()) == [citacao]


def test_a_janela_de_prova_pode_ficar_com_o_fim_em_aberto(disciplina, professor):
    janela = JanelaProva.objects.create(
        disciplina=disciplina, inicio=timezone.now(), criada_por=professor
    )

    assert janela.fim is None


def test_o_registro_de_uso_nao_guarda_o_aluno_so_o_pseudonimo():
    campos = {f.name for f in RegistroUso._meta.get_fields()}

    assert "aluno_pseudonimo" in campos
    assert "aluno" not in campos and "conversa" not in campos and "mensagem" not in campos


def test_o_registro_de_uso_guarda_pergunta_filtrada_trechos_e_custo(disciplina):
    registro = RegistroUso.objects.create(
        aluno_pseudonimo="abc123",
        disciplina=disciplina,
        pergunta_filtrada="o que é lista?",
        trechos=[1, 2],
        tipo="resposta",
        tokens_entrada=100,
        tokens_saida=20,
        custo="0.0012",
    )

    registro.refresh_from_db()
    assert (registro.trechos, registro.tokens_entrada) == ([1, 2], 100)


def test_a_revisao_de_resposta_comeca_pendente(conversa):
    mensagem = Mensagem.objects.create(
        conversa=conversa,
        autor=Mensagem.Autor.TUTOR,
        texto="x",
        avaliacao=Mensagem.Avaliacao.INCORRETA,
    )

    revisao = RevisaoResposta.objects.create(mensagem=mensagem)

    assert revisao.status == RevisaoResposta.Status.PENDENTE
