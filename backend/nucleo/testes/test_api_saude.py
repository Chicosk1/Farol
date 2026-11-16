"""Rota de saúde: diz se a API está no ar (ACE-T11)."""

from rest_framework.test import APIClient


def test_saude_responde_ok_sem_login():
    resposta = APIClient().get("/api/saude")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_saude_so_aceita_leitura():
    resposta = APIClient().post("/api/saude")

    assert resposta.status_code == 405
