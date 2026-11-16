"""Regras do módulo disciplinas (spec 001). Chamado pela API e pelos outros módulos."""

from django.contrib.postgres.lookups import Unaccent
from django.db.models import QuerySet
from django.db.models.functions import Lower

from contas.servicos import Perfil

from .models import Disciplina, Matricula

FILTROS = ("todas", "favoritas", "com-tutor")


def listar_disciplinas(
    pessoa, perfil: str | None, busca: str = "", filtro: str = "todas"
) -> QuerySet[Disciplina]:
    """As disciplinas da pessoa no perfil em uso (ACE-RF-04), com busca e filtro (ACE-RF-10).

    O aluno vê as disciplinas em que tem matrícula ativa, e o professor, as que leciona.
    A busca é por parte do nome, sem diferenciar acentos nem maiúsculas.
    """
    if perfil == Perfil.ALUNO:
        disciplinas = Disciplina.objects.filter(
            matriculas__aluno=pessoa, matriculas__situacao=Matricula.Situacao.ATIVA
        )
    elif perfil == Perfil.PROFESSOR:
        disciplinas = Disciplina.objects.filter(professor=pessoa)
    else:
        return Disciplina.objects.none()

    busca = busca.strip()
    if busca:
        # icontains escapa % e _, então o texto vale como texto, e não como padrão.
        disciplinas = disciplinas.filter(nome__unaccent__icontains=busca)

    if filtro == "com-tutor":
        # Depende de saber se há material pronto, o que vem com a spec 002 (ACE-T34).
        return Disciplina.objects.none()

    return disciplinas.select_related("professor").order_by(Lower(Unaccent("nome")), "id")
