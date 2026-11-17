"""Aviso de privacidade versionado e registro da ciência (ACE-T50, ACE-T51).

Cenários de aceite da História 4 da spec 001: o aluno que entra pela primeira vez vê o aviso e
só continua depois de confirmar; quando o texto muda, vê o aviso novo uma vez. Dados fictícios.
"""

from unittest import mock

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from contas import aviso
from contas.models import CienciaPrivacidade, Perfil, Pessoa


def confirmar(cliente, versao: str | None = None):
    versao = versao or aviso.VERSAO_ATUAL
    return cliente.post("/api/eu/ciencia-privacidade", {"versao": versao}, format="json")


@pytest.mark.requisito("ACE-RF-08")
def test_aluno_que_entra_pela_primeira_vez_precisa_ver_o_aviso(cliente_aluna):
    assert cliente_aluna.get("/api/eu").json()["precisa_ver_aviso"] is True


@pytest.mark.requisito("ACE-RF-08")
def test_depois_de_confirmar_o_aviso_nao_aparece_mais_e_a_ciencia_fica_guardada(
    cliente_aluna, aluna
):
    antes = timezone.now()

    resposta = confirmar(cliente_aluna)

    assert resposta.status_code == 204
    assert cliente_aluna.get("/api/eu").json()["precisa_ver_aviso"] is False
    ciencia = CienciaPrivacidade.objects.get()
    assert (ciencia.pessoa, ciencia.versao_aviso) == (aluna, aviso.VERSAO_ATUAL)
    assert antes <= ciencia.data <= timezone.now()  # a data da ciência é guardada


@pytest.mark.requisito("ACE-RF-08")
def test_confirmar_de_novo_nao_duplica_nem_muda_a_data(cliente_aluna):
    confirmar(cliente_aluna)
    primeira = CienciaPrivacidade.objects.get().data

    assert confirmar(cliente_aluna).status_code == 204

    assert CienciaPrivacidade.objects.count() == 1
    assert CienciaPrivacidade.objects.get().data == primeira


@pytest.mark.requisito("ACE-RF-08")
def test_quando_o_texto_muda_o_aluno_ve_o_aviso_novo_uma_vez(cliente_aluna):
    confirmar(cliente_aluna)
    assert cliente_aluna.get("/api/eu").json()["precisa_ver_aviso"] is False

    with mock.patch.object(aviso, "VERSAO_ATUAL", "2"):
        assert cliente_aluna.get("/api/eu").json()["precisa_ver_aviso"] is True
        assert cliente_aluna.get("/api/aviso-privacidade").json()["versao"] == "2"
        assert confirmar(cliente_aluna, "2").status_code == 204
        assert cliente_aluna.get("/api/eu").json()["precisa_ver_aviso"] is False

    # As duas ciências ficam guardadas, uma por versão.
    assert sorted(CienciaPrivacidade.objects.values_list("versao_aviso", flat=True)) == [
        aviso.VERSAO_ATUAL,
        "2",
    ]


@pytest.mark.requisito("ACE-RF-08")
def test_confirmar_uma_versao_desatualizada_e_recusado(cliente_aluna):
    with mock.patch.object(aviso, "VERSAO_ATUAL", "2"):
        resposta = confirmar(cliente_aluna, "1")

    assert resposta.status_code == 400
    assert CienciaPrivacidade.objects.count() == 0


@pytest.mark.requisito("ACE-RF-08")
def test_o_aviso_e_do_aluno_professor_nao_precisa_ver(cliente_professor):
    assert cliente_professor.get("/api/eu").json()["precisa_ver_aviso"] is False


@pytest.mark.requisito("ACE-RF-08")
def test_quem_tem_dois_perfis_so_ve_o_aviso_quando_esta_como_aluno(professor):
    professor.perfis = [Perfil.PROFESSOR, Perfil.ALUNO]
    professor.save()
    cliente = APIClient()
    cliente.force_login(professor)

    como_professor = cliente.get("/api/eu").json()["precisa_ver_aviso"]
    cliente.post("/api/eu/perfil-ativo", {"perfil": "aluno"}, format="json")
    como_aluno = cliente.get("/api/eu").json()["precisa_ver_aviso"]

    assert (como_professor, como_aluno) == (False, True)


@pytest.mark.requisito("ACE-RF-08")
def test_a_ciencia_e_de_cada_pessoa(cliente_aluna):
    outra = Pessoa.objects.create_user(
        email="bruno.dias@exemplo.edu.br", nome="Bruno Dias", perfis=[Perfil.ALUNO]
    )
    cliente_da_outra = APIClient()
    cliente_da_outra.force_login(outra)

    confirmar(cliente_aluna)

    assert cliente_da_outra.get("/api/eu").json()["precisa_ver_aviso"] is True


@pytest.mark.requisito("ACE-RF-08")
def test_o_aviso_diz_o_que_e_registrado_para_que_e_por_quanto_tempo(cliente_aluna):
    resposta = cliente_aluna.get("/api/aviso-privacidade")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["versao"] == aviso.VERSAO_ATUAL
    titulos = [item["titulo"] for item in corpo["itens"]]
    assert titulos == [
        "O que é registrado",
        "Para quê",
        "Por quanto tempo",
        "Os seus direitos",
    ]
    assert all(item["texto"].strip() for item in corpo["itens"])
    assert "12 meses" in corpo["itens"][2]["texto"]


@pytest.mark.requisito("ACE-RF-08")
def test_o_aviso_promete_so_o_que_a_constituicao_garante(cliente_aluna):
    texto = " ".join(
        i["texto"] for i in cliente_aluna.get("/api/aviso-privacidade").json()["itens"]
    )

    # Princípio IV: o professor não vê quem perguntou, e o aluno pode ver e apagar o histórico.
    assert "não vê quem perguntou" in texto
    assert "apagar" in texto


def test_as_rotas_do_aviso_exigem_login(cliente):
    assert cliente.get("/api/aviso-privacidade").status_code == 401
    assert confirmar(cliente).status_code == 401


def test_confirmar_logado_sem_token_csrf_e_recusado(aluna):
    cliente = APIClient(enforce_csrf_checks=True)
    cliente.force_login(aluna)

    assert confirmar(cliente).status_code == 403
