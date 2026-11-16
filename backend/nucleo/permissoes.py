"""Permissão por disciplina, reutilizável por todas as rotas da API (ACE-RF-05).

O núcleo não depende de nenhum módulo (ADR 0007). Por isso, quem sabe responder "esta pessoa tem
acesso a esta disciplina?" e "qual é o perfil em uso?" são funções dos módulos contas e
disciplinas, indicadas em FAROL_ACESSO (configuracoes/base.py) e carregadas só na hora de usar.

Uso numa rota com `disciplina_id` na URL:

    @permission_classes([AcessoADisciplina])                    # aluno matriculado ou professor
    @permission_classes([acesso_a_disciplina("professor")])     # só o professor da disciplina
"""

from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework.permissions import BasePermission


def _funcao(nome: str):
    return import_string(settings.FAROL_ACESSO[nome])


class AcessoADisciplina(BasePermission):
    """Nega, com 403, quem não tem acesso à disciplina da rota. Nunca libera por omissão.

    Uma disciplina que não existe recebe o mesmo 403 de uma que a pessoa não pode ver, para não
    revelar quais disciplinas existem. Uma rota sem `disciplina_id` na URL também é negada.
    """

    papeis: tuple[str, ...] | None = None  # None: qualquer perfil com acesso à disciplina

    def has_permission(self, request, view) -> bool:
        pessoa = request.user
        if not pessoa or not pessoa.is_authenticated:
            return False
        disciplina_id = view.kwargs.get("disciplina_id")
        if disciplina_id is None:
            return False
        perfil = _funcao("PERFIL_ATIVO")(pessoa, request.session)
        if self.papeis is not None and perfil not in self.papeis:
            return False
        return bool(_funcao("ACESSO_A_DISCIPLINA")(pessoa, perfil, disciplina_id))


def acesso_a_disciplina(*papeis: str) -> type[AcessoADisciplina]:
    """Permissão que, além de exigir acesso à disciplina, só aceita os perfis indicados."""
    return type("AcessoADisciplinaRestrito", (AcessoADisciplina,), {"papeis": tuple(papeis)})
