"""Login com o Google pelo django-allauth (ACE-RF-01, ACE-RF-02).

Só HTTP: os adaptadores ligam o fluxo do allauth às regras de contas/servicos.py e mandam
cada erro de volta para a tela de entrada do front-end, que mostra a mensagem certa.
"""

from urllib.parse import urlencode

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpResponseRedirect

from contas import servicos

TELA_DE_ENTRADA = "/entrar"


def _voltar_para_a_entrada(erro: str) -> HttpResponseRedirect:
    return HttpResponseRedirect(f"{TELA_DE_ENTRADA}?{urlencode({'erro': erro})}")


class AdaptadorDeContas(DefaultAccountAdapter):
    def respond_user_inactive(self, request, user):
        return _voltar_para_a_entrada("conta_desativada")


class AdaptadorDoGoogle(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin) -> None:
        """Antes de abrir a sessão: só a conta de e-mail verificado, de pessoa ativa, entra."""
        dados = sociallogin.account.extra_data
        email = dados.get("email") or ""
        try:
            servicos.conferir_conta_do_google(
                email, dados.get("email_verified") in (True, "true"), dados.get("hd")
            )
        except servicos.ContaNaoVerificada:
            raise ImmediateHttpResponse(_voltar_para_a_entrada("conta_nao_verificada")) from None
        except servicos.ContaExterna:
            raise ImmediateHttpResponse(_voltar_para_a_entrada("conta_externa")) from None
        if servicos.pessoa_desativada(email):
            raise ImmediateHttpResponse(_voltar_para_a_entrada("conta_desativada"))

    def populate_user(self, request, sociallogin, data):
        pessoa = super().populate_user(request, sociallogin, data)
        servicos.preparar_pessoa_nova(pessoa, data.get("name") or "")
        return pessoa

    def on_authentication_error(
        self, request, provider, error=None, exception=None, extra_context=None
    ) -> None:
        """Cancelar no Google ou qualquer falha no caminho volta para a entrada."""
        raise ImmediateHttpResponse(_voltar_para_a_entrada("falha"))
