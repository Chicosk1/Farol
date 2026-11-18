"""Leitura de variáveis de ambiente para as configurações.

Segredos e endereços nunca ficam no código: vêm do ambiente (arquivo `.env` no desenvolvimento).
"""

import os

from django.core.exceptions import ImproperlyConfigured


def obrigatoria(nome: str) -> str:
    """Devolve o valor da variável ou impede o Django de subir, dizendo qual variável falta."""
    valor = os.environ.get(nome, "").strip()
    if not valor:
        raise ImproperlyConfigured(f"Defina a variável de ambiente {nome}.")
    return valor


def opcional(nome: str, padrao: str) -> str:
    """Devolve o valor da variável ou o padrão, quando ela não existe ou está vazia."""
    return os.environ.get(nome, "").strip() or padrao


def fracao(nome: str, padrao: str) -> float:
    """Um número de 0 a 1 vindo da variável (ou o padrão). Fora disso, o Django não sobe."""
    texto = opcional(nome, padrao)
    try:
        valor = float(texto.replace(",", "."))
    except ValueError:
        raise ImproperlyConfigured(
            f"{nome} precisa ser um número de 0 a 1, e não {texto!r}."
        ) from None
    if not 0 <= valor <= 1:
        raise ImproperlyConfigured(f"{nome} precisa ser um número de 0 a 1, e não {texto!r}.")
    return valor


def definida_ou(nome: str, padrao: str) -> str:
    """Devolve o valor da variável como está, mesmo vazio, ou o padrão quando ela não existe."""
    return os.environ.get(nome, padrao)


def lista(valor: str) -> list[str]:
    """Separa um texto como `a.com, b.com` em itens, sem espaços nem itens vazios."""
    return [item.strip() for item in valor.split(",") if item.strip()]
