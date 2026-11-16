"""Regras do módulo contas (spec 001). Chamado pela API; usa os modelos."""

from collections.abc import MutableMapping

from .models import Pessoa, normalizar_email

CHAVE_PERFIL_ATIVO = "perfil_ativo"


class PessoaNaoEncontrada(LookupError):
    """Não há pessoa ativa com o e-mail informado."""


def pessoa_ativa_por_email(email: str) -> Pessoa:
    """A pessoa ativa com este e-mail, sem diferenciar maiúsculas nem espaços."""
    try:
        return Pessoa.objects.get(email=normalizar_email(email), is_active=True)
    except Pessoa.DoesNotExist:
        raise PessoaNaoEncontrada(email) from None


class PerfilInvalido(ValueError):
    """A pessoa pediu um perfil que não tem."""


def perfil_ativo(pessoa: Pessoa, sessao: MutableMapping) -> str | None:
    """Perfil em uso na sessão. Sem escolha válida, vale o primeiro perfil da pessoa (ACE-RF-03)."""
    escolhido = sessao.get(CHAVE_PERFIL_ATIVO)
    if escolhido in pessoa.perfis:
        return escolhido
    return pessoa.perfis[0] if pessoa.perfis else None


def trocar_perfil_ativo(pessoa: Pessoa, sessao: MutableMapping, perfil: str | None) -> str:
    """Troca o perfil da sessão sem sair. Só aceita um perfil que a pessoa tem (ACE-RF-03)."""
    if perfil not in pessoa.perfis:
        raise PerfilInvalido(f"A pessoa não tem o perfil {perfil!r}.")
    sessao[CHAVE_PERFIL_ATIVO] = perfil
    return perfil
