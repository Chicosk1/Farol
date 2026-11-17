"""Dados fictícios do protótipo (prototipo/js/data.js), criados de forma idempotente.

Nenhum dado real de aluno entra aqui (constituição, restrições do projeto).
"""

from dataclasses import dataclass

from contas import servicos as contas
from contas.servicos import Perfil
from disciplinas import servicos as disciplinas

DOMINIO = "exemplo.edu.br"  # reservado para dados fictícios
TURMA = "SINF2NA"
SEMESTRE = "2026/2"

ALUNA = {"email": f"ana.souza@{DOMINIO}", "nome": "Ana Souza", "perfis": [Perfil.ALUNO]}

# Quem importa turmas pelo painel administrativo (disciplinas/admin.py).
EQUIPE_DE_TI = {
    "email": f"ti@{DOMINIO}",
    "nome": "Equipe de TI",
    "perfis": [Perfil.ADMIN],
    "equipe": True,
}

# As seis disciplinas do 2º período de Sistemas de Informação, cada uma com o seu professor.
DISCIPLINAS = [
    ("SINF201", "Estruturas de Dados", "carlos.mendes", "Carlos Mendes"),
    ("SINF202", "Banco de Dados I", "marta.ribeiro", "Marta Ribeiro"),
    ("SINF203", "Programação Orientada a Objetos", "joao.pereira", "João Pereira"),
    ("SINF204", "Matemática Discreta", "luciana.alves", "Luciana Alves"),
    ("SINF205", "Cálculo Diferencial e Integral", "rogerio.lima", "Rogério Lima"),
    ("SINF206", "Engenharia de Software I", "paulo.nunes", "Paulo Nunes"),
]


@dataclass
class Relatorio:
    criados: int = 0
    existentes: int = 0

    def contar(self, criado: bool) -> None:
        if criado:
            self.criados += 1
        else:
            self.existentes += 1


def popular() -> Relatorio:
    """Cria o que falta e restaura o que mudou, sem duplicar nada ao rodar de novo."""
    relatorio = Relatorio()
    aluna, criada = contas.criar_ou_atualizar_pessoa(**ALUNA)
    relatorio.contar(criada)
    _, criada = contas.criar_ou_atualizar_pessoa(**EQUIPE_DE_TI)
    relatorio.contar(criada)
    for codigo, nome, usuario, nome_do_professor in DISCIPLINAS:
        professor, criado = contas.criar_ou_atualizar_pessoa(
            email=f"{usuario}@{DOMINIO}", nome=nome_do_professor, perfis=[Perfil.PROFESSOR]
        )
        relatorio.contar(criado)
        disciplina, criada = disciplinas.garantir_disciplina(
            codigo=codigo, nome=nome, turma=TURMA, semestre=SEMESTRE, professor=professor
        )
        relatorio.contar(criada)
        _, criada = disciplinas.garantir_matricula(aluna, disciplina)
        relatorio.contar(criada)
    return relatorio
