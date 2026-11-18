"""Rotas de importação: POST /api/importacoes e GET /api/importacoes/{id} (ACE-T43).

Só o perfil administrador envia arquivos e vê relatórios. Nos testes, o Celery roda na hora
(CELERY_TASK_ALWAYS_EAGER), então o relatório já está pronto depois do envio.
"""

from unittest import mock

import pytest
from celery.canvas import Signature
from django.core.files.uploadedfile import SimpleUploadedFile

from contas.models import Perfil, Pessoa
from disciplinas import tarefas
from disciplinas.models import Disciplina, Importacao, Matricula

CABECALHO = "ra,nome,email,codigo_disciplina,nome_disciplina,turma,semestre,email_professor"
DISCIPLINA = "SINF201,Estruturas de Dados,SINF2NA,2026/2,carlos.mendes@exemplo.edu.br"
LINHA = f"1,Ana Souza,ana.souza@exemplo.edu.br,{DISCIPLINA}"


@pytest.fixture(autouse=True)
def arquivos_temporarios(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


def arquivo(texto: str = f"{CABECALHO}\n{LINHA}\n", nome: str = "turmas.csv") -> SimpleUploadedFile:
    return SimpleUploadedFile(nome, texto.encode("utf-8"), content_type="text/csv")


def enviar(cliente, **dados):
    return cliente.post("/api/importacoes", dados or {"arquivo": arquivo()}, format="multipart")


@pytest.mark.requisito("ACE-RF-06")
def test_admin_envia_o_csv_e_depois_le_o_relatorio(cliente_admin):
    resposta = enviar(cliente_admin)

    assert resposta.status_code == 202
    corpo = resposta.json()
    assert set(corpo) == {"id", "status"}

    relatorio = cliente_admin.get(f"/api/importacoes/{corpo['id']}")
    assert relatorio.status_code == 200
    assert relatorio.json() | {"enviada_em": None} == {
        "id": corpo["id"],
        "status": "concluida",
        "aceitas": 1,
        "rejeitadas": [],
        "matriculas_encerradas": 0,
        "erro": "",
        "aviso": "",
        "enviada_em": None,
    }
    assert Disciplina.objects.filter(codigo="SINF201").exists()
    assert Matricula.objects.count() == 1


@pytest.mark.requisito("ACE-RF-06")
def test_o_relatorio_traz_as_linhas_rejeitadas_com_o_motivo(cliente_admin):
    texto = f"{CABECALHO}\n{LINHA}\n2,Beto,quebrado,{DISCIPLINA}\n"

    importacao_id = enviar(cliente_admin, arquivo=arquivo(texto)).json()["id"]
    relatorio = cliente_admin.get(f"/api/importacoes/{importacao_id}").json()

    assert relatorio["aceitas"] == 1
    assert [r["linha"] for r in relatorio["rejeitadas"]] == [3]
    assert "e-mail" in relatorio["rejeitadas"][0]["motivo"]


@pytest.mark.requisito("ACE-RF-06")
def test_arquivo_com_problema_de_estrutura_aparece_como_recusado_no_relatorio(cliente_admin):
    importacao_id = enviar(cliente_admin, arquivo=arquivo("ra;nome\n1;A\n")).json()["id"]

    relatorio = cliente_admin.get(f"/api/importacoes/{importacao_id}").json()

    assert relatorio["status"] == "recusada"
    assert "vírgula" in relatorio["erro"]
    assert Matricula.objects.count() == 0


@pytest.mark.requisito("ACE-RF-06")
def test_o_processamento_vai_para_a_fila_do_celery(cliente_admin):
    with mock.patch.object(Signature, "apply_async", autospec=True) as enfileirar:
        resposta = enviar(cliente_admin)

    enfileirar.assert_called_once()
    assinatura = enfileirar.call_args.args[0]
    assert assinatura.task == "disciplinas.processar_importacao"
    assert assinatura.args == (resposta.json()["id"],)
    assert Importacao.objects.get(pk=resposta.json()["id"]).status == "pendente"


@pytest.mark.requisito("ACE-RF-06")
def test_a_tarefa_do_celery_so_chama_o_servico_e_devolve_o_status(cliente_admin):
    importacao_id = Importacao.objects.create(arquivo=arquivo()).id

    assert tarefas.processar_importacao(importacao_id) == "concluida"


@pytest.mark.requisito("ACE-RF-06")
@pytest.mark.parametrize("papel", ["aluna", "professor"])
def test_quem_nao_e_admin_recebe_403_e_nada_e_importado(papel, request):
    pessoa = request.getfixturevalue(papel)
    from rest_framework.test import APIClient

    cliente = APIClient()
    cliente.force_login(pessoa)

    assert enviar(cliente).status_code == 403
    assert cliente.get("/api/importacoes/1").status_code == 403
    assert Importacao.objects.count() == 0


@pytest.mark.requisito("ACE-RF-06")
def test_admin_com_outro_perfil_ativo_tambem_recebe_403(admin, cliente_admin):
    admin.perfis = [Perfil.ALUNO, Perfil.ADMIN]
    admin.save()
    cliente_admin.post("/api/eu/perfil-ativo", {"perfil": "aluno"}, format="json")

    assert enviar(cliente_admin).status_code == 403


def test_exige_login(cliente):
    assert enviar(cliente).status_code == 401
    assert cliente.get("/api/importacoes/1").status_code == 401


@pytest.mark.requisito("ACE-RF-06")
def test_envio_sem_arquivo_ou_com_arquivo_que_nao_e_csv_recebe_400(cliente_admin):
    assert cliente_admin.post("/api/importacoes", {}, format="multipart").status_code == 400
    assert enviar(cliente_admin, arquivo=arquivo(nome="turmas.xlsx")).status_code == 400
    assert Importacao.objects.count() == 0


@pytest.mark.requisito("ACE-RF-06")
def test_arquivo_acima_de_5_mb_recebe_400(cliente_admin):
    grande = SimpleUploadedFile("turmas.csv", b"x" * (5 * 1024 * 1024 + 1), content_type="text/csv")

    assert enviar(cliente_admin, arquivo=grande).status_code == 400


def test_relatorio_que_nao_existe_recebe_404(cliente_admin):
    assert cliente_admin.get("/api/importacoes/999999").status_code == 404


def test_as_rotas_de_importacao_so_aceitam_os_metodos_certos(cliente_admin):
    assert cliente_admin.get("/api/importacoes").status_code == 405
    assert cliente_admin.post("/api/importacoes/1").status_code == 405
    assert Pessoa.objects.count() == 1
