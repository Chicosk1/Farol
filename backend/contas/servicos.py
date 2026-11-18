"""Regras do módulo contas (spec 001). Chamado pela API; usa os modelos."""

from collections.abc import MutableMapping

from . import aviso
from .models import CienciaPrivacidade, Pessoa, normalizar_email
from .models import Perfil as Perfil  # reexportado: os outros módulos usam o perfil pelo servicos

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


def criar_ou_atualizar_pessoa(
    email: str, nome: str, perfis: list[str], equipe: bool = False
) -> tuple[Pessoa, bool]:
    """Garante uma pessoa ativa, com o nome e os perfis dados. Devolve a pessoa e se foi criada.

    `equipe` dá acesso ao painel administrativo. Serve aos dados de demonstração; nunca cria
    senha (ACE-RF-02).
    """
    email = normalizar_email(email)
    try:
        pessoa = Pessoa.objects.get(email=email)
    except Pessoa.DoesNotExist:
        pessoa = Pessoa.objects.create_user(email=email, nome=nome, perfis=perfis, is_staff=equipe)
        return pessoa, True
    pessoa.nome = nome
    pessoa.perfis = list(perfis)
    pessoa.is_active = True
    pessoa.is_staff = equipe
    pessoa.save()
    return pessoa, False


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


def garantir_pessoa_com_perfil(
    email: str, perfil: str, nome: str | None = None
) -> tuple[Pessoa, bool]:
    """Garante uma pessoa com o perfil dado, sem tirar os perfis que ela já tem.

    Serve à importação de turmas: o mesmo e-mail pode ser professor numa disciplina e aluno em
    outra. O nome só muda se for informado, e uma pessoa desativada continua desativada.
    Devolve a pessoa e se foi criada.
    """
    email = normalizar_email(email)
    try:
        pessoa = Pessoa.objects.get(email=email)
    except Pessoa.DoesNotExist:
        nome = nome or email.split("@")[0].replace(".", " ").replace("_", " ").title()
        return Pessoa.objects.create_user(email=email, nome=nome, perfis=[perfil]), True
    if perfil not in pessoa.perfis or (nome and nome != pessoa.nome):
        if perfil not in pessoa.perfis:
            pessoa.perfis = [*pessoa.perfis, perfil]
        if nome:
            pessoa.nome = nome
        pessoa.save()
    return pessoa, False


class VersaoDoAvisoDesatualizada(ValueError):
    """A pessoa confirmou a leitura de uma versão que não é mais a atual."""


def precisa_ver_aviso(pessoa: Pessoa, perfil: str | None) -> bool:
    """O aviso vale para o aluno: na primeira entrada e a cada nova versão (ACE-RF-08)."""
    if perfil != Perfil.ALUNO:
        return False
    return not CienciaPrivacidade.objects.filter(
        pessoa=pessoa, versao_aviso=aviso.VERSAO_ATUAL
    ).exists()


def registrar_ciencia(pessoa: Pessoa, versao: str) -> None:
    """Guarda que a pessoa leu a versão atual do aviso. Confirmar de novo não muda nada."""
    if versao != aviso.VERSAO_ATUAL:
        raise VersaoDoAvisoDesatualizada(versao)
    CienciaPrivacidade.objects.get_or_create(pessoa=pessoa, versao_aviso=versao)


def texto_do_aviso() -> dict:
    """A versão atual do aviso e o seu texto, para a tela mostrar."""
    return {"versao": aviso.VERSAO_ATUAL, "titulo": aviso.TITULO, "itens": aviso.ITENS}


def administradores() -> list[Pessoa]:
    """As pessoas ativas com o perfil de administrador, para avisos da equipe."""
    return [p for p in Pessoa.objects.filter(is_active=True) if Perfil.ADMIN in p.perfis]
