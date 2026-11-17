from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import SessionAuthentication


class AutenticacaoPorSessao(SessionAuthentication):
    """Sessão do Django (cookie HttpOnly e CSRF), mas quem não entrou recebe 401, e não 403.

    O 401 diz ao front-end que é preciso entrar; o 403 fica para "entrou, mas não pode" e para
    a falha do token CSRF.
    """

    def authenticate_header(self, request) -> str:
        return "Session"


class EsquemaDaSessao(OpenApiAuthenticationExtension):
    """Descreve a autenticação por sessão no contrato OpenAPI."""

    target_class = AutenticacaoPorSessao
    name = "cookieAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "apiKey", "in": "cookie", "name": "sessionid"}
