"""Dados fictícios do protótipo (prototipo/js/data.js), criados de forma idempotente.

Nenhum dado real de aluno entra aqui (constituição, restrições do projeto).
"""

from dataclasses import dataclass

from contas import servicos as contas
from contas.servicos import Perfil

# Pessoas do protótipo: a aluna do 2º período de Sistemas de Informação e o professor de
# Estruturas de Dados. O domínio exemplo.edu.br é reservado para dados fictícios.
PESSOAS = [
    {"email": "ana.souza@exemplo.edu.br", "nome": "Ana Souza", "perfis": [Perfil.ALUNO]},
    {
        "email": "carlos.mendes@exemplo.edu.br",
        "nome": "Carlos Mendes",
        "perfis": [Perfil.PROFESSOR],
    },
]


@dataclass
class Relatorio:
    criadas: int = 0
    existentes: int = 0


def popular() -> Relatorio:
    """Cria o que falta e restaura o que mudou, sem duplicar nada ao rodar de novo."""
    relatorio = Relatorio()
    for dados in PESSOAS:
        _, criada = contas.criar_ou_atualizar_pessoa(**dados)
        if criada:
            relatorio.criadas += 1
        else:
            relatorio.existentes += 1
    return relatorio
