"""Revisão das questões pelo professor e o sigilo dos rascunhos (QUE-T30, QUE-T31).

Dados fictícios.
"""

import pytest
from django.conf import settings
from django.urls import get_resolver
from rest_framework.test import APIClient

from contas.models import Perfil, Pessoa
from disciplinas.models import Disciplina, Matricula
from materiais.models import Material, Trecho
from questoes.models import Questao

TEXTO = "A pilha segue a regra LIFO: o último elemento a entrar é o primeiro a sair dela."


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


@pytest.fixture
def material(disciplina) -> Material:
    return Material.objects.create(
        disciplina=disciplina,
        aula_numero=3,
        aula_titulo="Pilhas e filas",
        arquivo="materiais/aula-3.pdf",
        status=Material.Status.PRONTO,
    )


@pytest.fixture
def trecho(material) -> Trecho:
    return Trecho.objects.create(
        material=material,
        pagina=2,
        ordem=0,
        texto=TEXTO,
        inicio=0,
        fim=len(TEXTO),
        vetor=[1.0] + [0.0] * (settings.FAROL_DIMENSAO_DO_VETOR - 1),
    )


def questao(material, trecho, **campos) -> Questao:
    dados = {
        "material": material,
        "enunciado": "Qual regra a pilha segue?",
        "alternativas": ["LIFO", "FIFO", "Por prioridade", "Aleatória"],
        "correta": 0,
        "justificativa": "Na pilha, o último a entrar é o primeiro a sair.",
        "topico": "Pilhas",
        "trecho": trecho,
    }
    return Questao.objects.create(**(dados | campos))


def listar(cliente, disciplina, status="pendente"):
    return cliente.get(f"/api/disciplinas/{disciplina.id}/questoes?status={status}")


def mudar(cliente, alvo, **dados):
    return cliente.patch(f"/api/questoes/{alvo.id}", dados, format="json")


@pytest.mark.requisito("QUE-RF-06")
def test_o_professor_ve_as_questoes_por_status_com_as_contagens(
    cliente_professor, disciplina, material, trecho
):
    questao(material, trecho, enunciado="Primeiro rascunho da pilha?")
    questao(material, trecho, enunciado="Segundo rascunho da pilha?")
    questao(material, trecho, status="publicada")
    questao(material, trecho, status="descartada")

    dados = listar(cliente_professor, disciplina).json()

    assert dados["contagens"] == {"pendente": 2, "publicada": 1, "descartada": 1}
    assert [q["enunciado"] for q in dados["questoes"]] == [
        "Segundo rascunho da pilha?",
        "Primeiro rascunho da pilha?",
    ]
    primeira = dados["questoes"][0]
    assert primeira["aula_numero"] == 3
    assert primeira["aula_titulo"] == "Pilhas e filas"
    assert primeira["alternativas"][primeira["correta"]] == "LIFO"
    assert primeira["trecho"] == {"id": trecho.id, "pagina": 2}
    assert primeira["nova"] is True
    assert primeira["origem_retirada"] is False
    assert len(listar(cliente_professor, disciplina, "publicada").json()["questoes"]) == 1


def test_a_lista_pode_ser_filtrada_pela_aula(cliente_professor, disciplina, material, trecho):
    outra = Material.objects.create(
        disciplina=disciplina, aula_numero=4, aula_titulo="Árvores", arquivo="materiais/a4.pdf"
    )
    questao(material, trecho)
    questao(outra, trecho)

    resposta = cliente_professor.get(
        f"/api/disciplinas/{disciplina.id}/questoes?status=pendente&material={material.id}"
    )

    assert [q["material"] for q in resposta.json()["questoes"]] == [material.id]


@pytest.mark.requisito("QUE-RF-05", "QUE-RF-07")
def test_aprovar_publica_a_questao_e_tira_a_marca_de_novo(cliente_professor, material, trecho):
    rascunho = questao(material, trecho)

    resposta = mudar(cliente_professor, rascunho, status="publicada")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "publicada"
    rascunho.refresh_from_db()
    assert (rascunho.status, rascunho.nova, rascunho.editada) == ("publicada", False, False)


@pytest.mark.requisito("QUE-RF-05")
def test_editar_muda_o_rascunho_que_continua_pendente_e_marcado_como_editado(
    cliente_professor, material, trecho
):
    rascunho = questao(material, trecho)

    resposta = mudar(
        cliente_professor,
        rascunho,
        enunciado="  Que ordem de saída a pilha segue?  ",
        alternativas=["FIFO", "LIFO", "Por prioridade", "Aleatória"],
        correta=1,
    )

    assert resposta.status_code == 200
    rascunho.refresh_from_db()
    assert rascunho.enunciado == "Que ordem de saída a pilha segue?"
    assert rascunho.alternativas[rascunho.correta] == "LIFO"
    assert (rascunho.status, rascunho.editada) == ("pendente", True)


def test_salvar_sem_mudar_nada_nao_marca_como_editada(cliente_professor, material, trecho):
    rascunho = questao(material, trecho)

    mudar(cliente_professor, rascunho, enunciado=rascunho.enunciado)

    rascunho.refresh_from_db()
    assert rascunho.editada is False


@pytest.mark.requisito("QUE-RF-05")
@pytest.mark.parametrize(
    ("edicao", "campo"),
    [
        ({"enunciado": ""}, "enunciado"),
        ({"alternativas": ["LIFO", "FIFO", "Aleatória"]}, "alternativas"),
        ({"alternativas": ["LIFO", "LIFO", "FIFO", "Aleatória"]}, "alternativas"),
        ({"correta": 7}, "correta"),
        ({"justificativa": "curta"}, "justificativa"),
    ],
)
def test_edicao_que_quebra_o_formato_e_recusada_com_o_motivo(
    cliente_professor, material, trecho, edicao, campo
):
    rascunho = questao(material, trecho)

    resposta = mudar(cliente_professor, rascunho, **edicao)

    assert resposta.status_code == 400
    assert campo in resposta.json()
    rascunho.refresh_from_db()
    assert rascunho.enunciado == "Qual regra a pilha segue?"


@pytest.mark.requisito("QUE-RF-05")
def test_descartar_manda_para_descartadas(cliente_professor, material, trecho):
    rascunho = questao(material, trecho)

    assert mudar(cliente_professor, rascunho, status="descartada").json()["status"] == "descartada"


@pytest.mark.requisito("QUE-RF-05")
def test_voltar_para_pendentes_tira_a_questao_do_quiz(cliente_professor, material, trecho):
    publicada = questao(material, trecho, status="publicada")

    assert mudar(cliente_professor, publicada, status="pendente").json()["status"] == "pendente"


def test_questao_publicada_nao_e_editada_sem_voltar_para_pendentes(
    cliente_professor, material, trecho
):
    publicada = questao(material, trecho, status="publicada")

    resposta = mudar(cliente_professor, publicada, enunciado="Outro enunciado da questão?")

    assert resposta.status_code == 409
    assert "pendentes" in resposta.json()["detail"]


def test_descartada_nao_e_publicada_direto(cliente_professor, material, trecho):
    descartada = questao(material, trecho, status="descartada")

    assert mudar(cliente_professor, descartada, status="publicada").status_code == 409


def test_questao_de_material_retirado_fica_marcada_e_nao_e_publicada(
    cliente_professor, disciplina, material, trecho
):
    rascunho = questao(material, trecho)
    material.status = Material.Status.RETIRADO
    material.save()

    [vista] = listar(cliente_professor, disciplina).json()["questoes"]
    assert vista["origem_retirada"] is True
    assert mudar(cliente_professor, rascunho, status="publicada").status_code == 409


@pytest.mark.requisito("QUE-RF-04")
def test_o_aluno_nao_ve_nem_muda_rascunhos(cliente_aluna, disciplina, material, trecho):
    rascunho = questao(material, trecho)

    for status in ("pendente", "publicada", "descartada"):
        assert listar(cliente_aluna, disciplina, status).status_code == 403
    assert mudar(cliente_aluna, rascunho, status="publicada").status_code == 403
    rascunho.refresh_from_db()
    assert rascunho.status == "pendente"


def _caminhos_get_da_api(valores: dict) -> list[str]:
    """Todas as rotas da API cujos parâmetros sabemos preencher, com os valores do teste."""
    caminhos = set()
    for chave, (possibilidades, *_) in get_resolver().reverse_dict.items():
        if not isinstance(chave, str):
            continue
        for formato, parametros in possibilidades:
            if formato.startswith("api/") and all(p in valores for p in parametros):
                caminhos.add("/" + formato % valores)
    return sorted(caminhos)


@pytest.mark.requisito("QUE-RF-04")
def test_nenhuma_rota_do_aluno_devolve_o_texto_de_um_rascunho(
    cliente_aluna, disciplina, material, trecho
):
    """Percorre as rotas da API com GET, como a aluna, e procura o enunciado do rascunho."""
    rascunho = questao(material, trecho, enunciado="Enunciado secreto do rascunho pendente?")
    valores = {
        "disciplina_id": disciplina.id,
        "material_id": material.id,
        "trecho_id": trecho.id,
        "questao_id": rascunho.id,
    }
    cliente_aluna.raise_request_exception = False  # o PDF fictício não existe no disco
    caminhos = _caminhos_get_da_api(valores)

    assert f"/api/disciplinas/{disciplina.id}/questoes" in caminhos
    for caminho in caminhos:
        resposta = cliente_aluna.get(caminho)
        assert b"Enunciado secreto" not in resposta.content, caminho


def test_professor_de_outra_disciplina_nao_ve_nem_muda(material, trecho, disciplina):
    outro = Pessoa.objects.create_user(
        email="paula.lima@exemplo.edu.br", nome="Paula Lima", perfis=[Perfil.PROFESSOR]
    )
    cliente = APIClient()
    cliente.force_login(outro)
    rascunho = questao(material, trecho)

    assert listar(cliente, disciplina).status_code == 403
    assert mudar(cliente, rascunho, status="publicada").status_code == 403


def test_questao_que_nao_existe_recebe_404(cliente_professor):
    assert cliente_professor.patch("/api/questoes/999", {}, format="json").status_code == 404
