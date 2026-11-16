"""Regras do módulo disciplinas (spec 001). Chamado pela API e pelos outros módulos."""

from django.contrib.postgres.lookups import Unaccent
from django.db.models import Exists, OuterRef, QuerySet
from django.db.models.functions import Lower

from contas.servicos import Perfil

from .models import Disciplina, Favorito, Matricula

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

    disciplinas = disciplinas.annotate(
        favorita=Exists(Favorito.objects.filter(pessoa=pessoa, disciplina=OuterRef("pk")))
    )
    if filtro == "favoritas":
        disciplinas = disciplinas.filter(favorita=True)

    return disciplinas.select_related("professor").order_by(Lower(Unaccent("nome")), "id")


def garantir_disciplina(
    codigo: str, nome: str, turma: str, semestre: str, professor
) -> tuple[Disciplina, bool]:
    """Cria a oferta da disciplina ou atualiza o nome e o professor. Devolve se foi criada.

    A oferta é identificada pelo código, pela turma e pelo semestre. Serve à importação de
    turmas (ACE-T41) e aos dados de demonstração.
    """
    disciplina, criada = Disciplina.objects.update_or_create(
        codigo=codigo,
        turma=turma,
        semestre=semestre,
        defaults={"nome": nome, "professor": professor},
    )
    return disciplina, criada


def garantir_matricula(aluno, disciplina: Disciplina) -> tuple[Matricula, bool]:
    """Garante a matrícula ativa do aluno na disciplina, reativando uma encerrada."""
    matricula, criada = Matricula.objects.update_or_create(
        aluno=aluno, disciplina=disciplina, defaults={"situacao": Matricula.Situacao.ATIVA}
    )
    return matricula, criada


def tem_acesso(pessoa, perfil: str | None, disciplina_id: int) -> bool:
    """Se a pessoa, no perfil em uso, pode acessar a disciplina (ACE-RF-05).

    O aluno precisa de matrícula ativa, e o professor, de lecionar a disciplina. Os outros
    perfis ainda não têm regra de acesso e são negados.
    """
    if perfil == Perfil.ALUNO:
        return Matricula.objects.filter(
            aluno=pessoa, disciplina_id=disciplina_id, situacao=Matricula.Situacao.ATIVA
        ).exists()
    if perfil == Perfil.PROFESSOR:
        return Disciplina.objects.filter(id=disciplina_id, professor=pessoa).exists()
    return False


def favoritar(pessoa, disciplina_id: int) -> None:
    """Marca a disciplina como favorita da pessoa. Marcar de novo não faz nada."""
    Favorito.objects.get_or_create(pessoa=pessoa, disciplina_id=disciplina_id)


def desfavoritar(pessoa, disciplina_id: int) -> None:
    """Tira a disciplina dos favoritos da pessoa. Não ser favorita não é erro."""
    Favorito.objects.filter(pessoa=pessoa, disciplina_id=disciplina_id).delete()
