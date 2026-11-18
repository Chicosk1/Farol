"""O radar da turma: indicadores, tópicos, acertos, sugestão e a regra dos 5 alunos
(RAD-T20 a RAD-T24, RAD-T30, RAD-T50). Dados sintéticos e fictícios."""

from datetime import timedelta

import pytest
from django.conf import settings
from django.core import mail
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from duvidas.models import Duvida
from materiais.models import Material, Trecho
from questoes.models import Questao
from radar import servicos
from tutor.models import ConfiguracaoTutor

from .sinteticos import perguntas, respostas


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


def aula(disciplina, numero, titulo) -> Trecho:
    material = Material.objects.create(
        disciplina=disciplina,
        aula_numero=numero,
        aula_titulo=titulo,
        arquivo=f"materiais/aula-{numero}.pdf",
        status=Material.Status.PRONTO,
    )
    return Trecho.objects.create(
        material=material,
        pagina=1,
        ordem=0,
        texto=f"Texto da aula {numero} sobre {titulo}.",
        inicio=0,
        fim=10,
        vetor=[1.0] + [0.0] * (settings.FAROL_DIMENSAO_DO_VETOR - 1),
    )


def questao(trecho, topico) -> Questao:
    return Questao.objects.create(
        material=trecho.material,
        enunciado=f"Questão sobre {topico}?",
        alternativas=["A", "B", "C", "D"],
        correta=0,
        justificativa="Porque o material diz.",
        topico=topico,
        trecho=trecho,
        status="publicada",
    )


@pytest.fixture
def segunda():
    return servicos.semana_atual()


def ver(cliente, disciplina, semana=None):
    caminho = f"/api/disciplinas/{disciplina.id}/radar"
    return cliente.get(caminho if semana is None else f"{caminho}?semana={semana}")


@pytest.mark.requisito("RAD-RF-02", "RAD-RF-03", "RAD-RF-04")
def test_os_topicos_vem_das_aulas_com_5_alunos_ou_mais(cliente_professor, disciplina, segunda):
    arvores = aula(disciplina, 5, "Árvores AVL")
    pilhas = aula(disciplina, 3, "Pilhas e filas")
    hash_ = aula(disciplina, 7, "Tabelas hash")
    perguntas(disciplina, arvores, 20, segunda)
    perguntas(disciplina, pilhas, 5, segunda, prefixo="p")
    perguntas(disciplina, hash_, 4, segunda, prefixo="h")  # só 4 alunos: não aparece
    Duvida.objects.create(disciplina=disciplina, texto="Cai na prova?")

    dados = ver(cliente_professor, disciplina).json()

    assert [(t["nome"], t["alunos"]) for t in dados["topicos"]] == [
        ("Aula 5 · Árvores AVL", 20),
        ("Aula 3 · Pilhas e filas", 5),
    ]
    assert len(dados["topicos"][0]["exemplos"]) == 3
    assert dados["topicos"][0]["material"] == arvores.material_id
    assert dados["indicadores"] == {
        "alunos_ativos": 29,
        "matriculados": 1,
        "perguntas": 29,
        "acerto_medio": None,
        "duvidas_sem_resposta": 1,
    }
    assert dados["pouco_uso"] is False


@pytest.mark.requisito("RAD-RF-07")
def test_taxa_de_acerto_so_com_5_alunos_e_do_menor_para_o_maior(
    cliente_professor, disciplina, segunda
):
    trecho = aula(disciplina, 3, "Pilhas e filas")
    perguntas(disciplina, trecho, 5, segunda)
    respostas(questao(trecho, "Filas"), 10, 8, segunda)
    respostas(questao(trecho, "Pilhas"), 6, 3, segunda)
    respostas(questao(trecho, "Deques"), 4, 0, segunda)  # 4 alunos: sem taxa

    dados = ver(cliente_professor, disciplina).json()

    assert [(a["topico"], a["taxa"]) for a in dados["acertos"]] == [("Pilhas", 50), ("Filas", 80)]
    assert dados["indicadores"]["acerto_medio"] == 55
    assert [q["taxa"] for q in dados["questoes_com_menor_acerto"]] == [50, 80]


@pytest.mark.requisito("RAD-RF-08")
def test_a_sugestao_combina_mais_duvidas_e_menor_acerto(cliente_professor, disciplina, segunda):
    arvores = aula(disciplina, 5, "Árvores AVL")
    pilhas = aula(disciplina, 3, "Pilhas e filas")
    grafos = aula(disciplina, 9, "Grafos")
    perguntas(disciplina, arvores, 12, segunda)
    perguntas(disciplina, pilhas, 12, segunda, prefixo="p")
    respostas(questao(arvores, "AVL"), 10, 9, segunda)
    respostas(questao(pilhas, "Pilhas"), 10, 2, segunda)
    respostas(questao(grafos, "Grafos"), 10, 5, segunda)

    sugestao = ver(cliente_professor, disciplina).json()["sugestao"]

    assert [s["nome"] for s in sugestao] == [
        "Aula 3 · Pilhas e filas",
        "Aula 5 · Árvores AVL",
        "Aula 9 · Grafos",
    ]
    assert sugestao[0]["material"] == pilhas.material_id


def test_semana_com_pouco_uso_mostra_so_os_indicadores(cliente_professor, disciplina, segunda):
    trecho = aula(disciplina, 3, "Pilhas e filas")
    perguntas(disciplina, trecho, 3, segunda)

    dados = ver(cliente_professor, disciplina).json()

    assert dados["pouco_uso"] is True
    assert dados["topicos"] == []
    assert dados["indicadores"]["alunos_ativos"] == 3


@pytest.mark.requisito("RAD-RF-09")
def test_a_semana_anterior_mostra_os_dados_daquela_semana(cliente_professor, disciplina, segunda):
    trecho = aula(disciplina, 3, "Pilhas e filas")
    perguntas(disciplina, trecho, 6, segunda - timedelta(weeks=1))

    atual = ver(cliente_professor, disciplina).json()
    anterior = ver(cliente_professor, disciplina, segunda - timedelta(weeks=1)).json()

    assert atual["indicadores"]["perguntas"] == 0
    assert anterior["indicadores"]["perguntas"] == 6
    semanas = cliente_professor.get(f"/api/disciplinas/{disciplina.id}/radar/semanas").json()
    assert semanas[0]["atual"] is True
    assert semanas[1]["semana"] == str(segunda - timedelta(weeks=1))


@pytest.mark.requisito("RAD-RF-05")
def test_o_professor_esconde_um_exemplo_e_ele_nao_volta(cliente_professor, disciplina, segunda):
    trecho = aula(disciplina, 3, "Pilhas e filas")
    perguntas(disciplina, trecho, 5, segunda)
    [topico] = ver(cliente_professor, disciplina).json()["topicos"]
    escondido = topico["exemplos"][0]

    resposta = cliente_professor.post(
        f"/api/disciplinas/{disciplina.id}/radar/exemplos-ocultos",
        {"texto": escondido},
        format="json",
    )

    assert resposta.status_code == 204
    [depois] = ver(cliente_professor, disciplina).json()["topicos"]
    assert escondido not in depois["exemplos"]


@pytest.mark.requisito("RAD-RF-06")
def test_a_resposta_nao_tem_dado_de_aluno(cliente_professor, aluna, disciplina, segunda):
    trecho = aula(disciplina, 3, "Pilhas e filas")
    perguntas(disciplina, trecho, 6, segunda, prefixo="pseudo")
    respostas(questao(trecho, "Pilhas"), 6, 3, segunda, prefixo="pseudo")

    conteudo = ver(cliente_professor, disciplina).content.decode()

    for proibido in (aluna.nome, aluna.email, "pseudo-", "10:00"):
        assert proibido not in conteudo


def test_so_o_professor_da_disciplina_ve_o_radar(cliente_aluna, disciplina):
    outro = Pessoa.objects.create_user(
        email="paula.lima@exemplo.edu.br", nome="Paula Lima", perfis=[Perfil.PROFESSOR]
    )
    cliente = APIClient()
    cliente.force_login(outro)

    assert ver(cliente_aluna, disciplina).status_code == 403
    assert ver(cliente, disciplina).status_code == 403


@pytest.mark.requisito("RAD-RF-10")
def test_o_resumo_semanal_vai_ao_professor_e_respeita_o_desligado(professor, disciplina, segunda):
    trecho = aula(disciplina, 3, "Pilhas e filas")
    perguntas(disciplina, trecho, 6, segunda - timedelta(weeks=1))

    assert servicos.enviar_resumos() == 1
    [email] = mail.outbox
    assert email.to == [professor.email]
    assert "Aula 3 · Pilhas e filas (6 alunos)" in email.body
    assert f"/disciplinas/{disciplina.id}/radar" in email.body

    ConfiguracaoTutor.objects.update_or_create(
        disciplina=disciplina, defaults={"resumo_semanal": False}
    )
    assert servicos.enviar_resumos() == 0


def test_semana_sem_uso_nao_manda_resumo(professor, disciplina):
    assert servicos.enviar_resumos() == 0


def test_a_tarefa_da_madrugada_calcula_todas_as_disciplinas(disciplina):
    assert servicos.calcular_todos() == 1
