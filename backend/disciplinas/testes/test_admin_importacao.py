"""Tela de importação de turmas no painel administrativo do Django (ACE-T42).

O administrador (perfil admin e equipe do Farol) envia o CSV, vê o relatório e consulta as
importações anteriores. Todos os dados são fictícios.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from contas.models import Perfil, Pessoa
from disciplinas.models import Importacao, Matricula

CABECALHO = "ra,nome,email,codigo_disciplina,nome_disciplina,turma,semestre,email_professor"
DISCIPLINA = "SINF201,Estruturas de Dados,SINF2NA,2026/2,carlos.mendes@exemplo.edu.br"


@pytest.fixture(autouse=True)
def arquivos_temporarios(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def equipe(db) -> Pessoa:
    return Pessoa.objects.create_user(
        email="ti@exemplo.edu.br", nome="Equipe de TI", perfis=[Perfil.ADMIN], is_staff=True
    )


@pytest.fixture
def cliente_equipe(equipe) -> Client:
    cliente = Client()
    cliente.force_login(equipe)
    return cliente


def csv_enviado(texto: str, nome: str = "turmas.csv") -> SimpleUploadedFile:
    return SimpleUploadedFile(nome, texto.encode("utf-8"), content_type="text/csv")


def enviar(cliente, texto: str, nome: str = "turmas.csv"):
    return cliente.post(
        reverse("admin:disciplinas_importacao_add"), {"arquivo": csv_enviado(texto, nome)}
    )


@pytest.mark.requisito("ACE-RF-06")
def test_a_equipe_ve_o_formulario_de_envio_com_o_formato_esperado(cliente_equipe):
    resposta = cliente_equipe.get(reverse("admin:disciplinas_importacao_add"))

    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert 'type="file"' in html
    assert "ra,nome,email,codigo_disciplina" in html  # o formato do CSV está na tela


@pytest.mark.requisito("ACE-RF-06")
def test_enviar_o_csv_importa_e_leva_ao_relatorio(cliente_equipe, equipe):
    resposta = enviar(
        cliente_equipe, f"{CABECALHO}\n1,Ana Souza,ana.souza@exemplo.edu.br,{DISCIPLINA}\n"
    )

    importacao = Importacao.objects.get()
    assert resposta.status_code == 302
    assert resposta.url == reverse("admin:disciplinas_importacao_change", args=[importacao.pk])
    assert importacao.enviada_por == equipe
    assert importacao.status == Importacao.Status.CONCLUIDA  # o Celery roda na hora nos testes
    assert Matricula.objects.count() == 1

    relatorio = cliente_equipe.get(resposta.url).content.decode()
    assert "Concluída" in relatorio
    assert "Linhas aceitas" in relatorio


@pytest.mark.requisito("ACE-RF-06")
def test_o_relatorio_lista_as_linhas_rejeitadas_com_o_motivo(cliente_equipe):
    texto = f"{CABECALHO}\n1,Ana,ana@exemplo.edu.br,{DISCIPLINA}\n2,Beto,quebrado,{DISCIPLINA}\n"
    enviar(cliente_equipe, texto)

    importacao = Importacao.objects.get()
    relatorio = cliente_equipe.get(
        reverse("admin:disciplinas_importacao_change", args=[importacao.pk])
    ).content.decode()

    assert "Linha 3" in relatorio
    assert "O e-mail do aluno é inválido." in relatorio


@pytest.mark.requisito("ACE-RF-06")
def test_arquivo_recusado_mostra_o_motivo_no_relatorio(cliente_equipe):
    enviar(cliente_equipe, "ra;nome\n1;A\n")

    importacao = Importacao.objects.get()
    relatorio = cliente_equipe.get(
        reverse("admin:disciplinas_importacao_change", args=[importacao.pk])
    ).content.decode()

    assert importacao.status == Importacao.Status.RECUSADA
    assert "Recusada" in relatorio
    assert "ponto e vírgula" in relatorio


@pytest.mark.requisito("ACE-RF-06")
def test_arquivo_que_nao_e_csv_e_recusado_no_formulario(cliente_equipe):
    resposta = enviar(cliente_equipe, "qualquer coisa", nome="turmas.xlsx")

    assert resposta.status_code == 200  # volta ao formulário, com o erro
    assert "Envie um arquivo CSV" in resposta.content.decode()
    assert Importacao.objects.count() == 0


@pytest.mark.requisito("ACE-RF-06")
def test_a_lista_mostra_as_importacoes_anteriores(cliente_equipe):
    enviar(cliente_equipe, f"{CABECALHO}\n1,Ana,ana@exemplo.edu.br,{DISCIPLINA}\n")

    resposta = cliente_equipe.get(reverse("admin:disciplinas_importacao_changelist"))

    assert resposta.status_code == 200
    assert "Equipe de TI" in resposta.content.decode()


@pytest.mark.requisito("ACE-RF-06")
def test_importacao_nao_pode_ser_editada_nem_apagada(cliente_equipe):
    enviar(cliente_equipe, f"{CABECALHO}\n1,Ana,ana@exemplo.edu.br,{DISCIPLINA}\n")
    pk = Importacao.objects.get().pk

    assert (
        cliente_equipe.post(
            reverse("admin:disciplinas_importacao_change", args=[pk]), {"aceitas": 999}
        ).status_code
        == 403
    )
    assert Importacao.objects.get().aceitas == 1
    assert (
        cliente_equipe.get(reverse("admin:disciplinas_importacao_delete", args=[pk])).status_code
        == 403
    )


@pytest.mark.requisito("ACE-RF-06")
def test_quem_e_equipe_mas_nao_tem_o_perfil_admin_nao_importa(db):
    sem_perfil = Pessoa.objects.create_user(
        email="x@exemplo.edu.br", nome="X", perfis=[Perfil.PROFESSOR], is_staff=True
    )
    cliente = Client()
    cliente.force_login(sem_perfil)

    assert cliente.get(reverse("admin:disciplinas_importacao_add")).status_code == 403
    assert enviar(cliente, f"{CABECALHO}\n").status_code == 403
    assert Importacao.objects.count() == 0


@pytest.mark.requisito("ACE-RF-06")
def test_quem_nao_e_equipe_e_mandado_para_o_login_do_painel(aluna):
    cliente = Client()
    cliente.force_login(aluna)

    resposta = cliente.get(reverse("admin:disciplinas_importacao_add"))

    assert resposta.status_code == 302
    assert "/admin/login/" in resposta.url
    assert Client().get(reverse("admin:index")).status_code == 302
