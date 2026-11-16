"""Regras do módulo disciplinas (spec 001). Chamado pela API e pelos outros módulos."""

from collections import defaultdict

from django.contrib.postgres.lookups import Unaccent
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Exists, OuterRef, QuerySet
from django.db.models.functions import Lower
from django.utils import timezone

from contas import servicos as contas
from contas.servicos import Perfil

from . import leitura_csv
from .models import Disciplina, Favorito, Importacao, Matricula

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


def criar_importacao(conteudo: bytes, nome_do_arquivo: str, enviada_por) -> Importacao:
    """Guarda o arquivo enviado e cria a importação pendente. O processamento é separado
    (processar_importacao), para poder rodar em segundo plano."""
    importacao = Importacao(enviada_por=enviada_por)
    importacao.arquivo.save(nome_do_arquivo, ContentFile(conteudo), save=False)
    importacao.save()
    return importacao


def processar_importacao(importacao_id: int) -> Importacao:
    """Importa turmas, disciplinas e matrículas do CSV e guarda o relatório (ACE-RF-06 e 07).

    Idempotente: importar o mesmo arquivo de novo não duplica nada. Uma matrícula ativa que não
    aparece mais numa disciplina do arquivo é encerrada, mas só quando nenhuma linha foi
    rejeitada, para um erro de digitação não tirar o acesso de ninguém.
    """
    importacao = Importacao.objects.get(pk=importacao_id)
    importacao.status = Importacao.Status.PROCESSANDO
    importacao.save(update_fields=["status"])

    with importacao.arquivo.open("rb") as arquivo:
        conteudo = arquivo.read()
    try:
        linhas = leitura_csv.ler(conteudo)
    except leitura_csv.ArquivoRecusado as recusa:
        importacao.status = Importacao.Status.RECUSADA
        importacao.erro = str(recusa)
        importacao.save()
        return importacao

    aceitas, rejeitadas = leitura_csv.validar(linhas)
    with transaction.atomic():
        encerradas = _aplicar_importacao(aceitas, encerrar_ausentes=not rejeitadas)

    importacao.status = Importacao.Status.CONCLUIDA
    importacao.aceitas = len(aceitas)
    importacao.rejeitadas = rejeitadas
    importacao.matriculas_encerradas = encerradas
    if rejeitadas:
        importacao.aviso = (
            "Há linhas rejeitadas, então nenhuma matrícula foi encerrada. Corrija as linhas "
            "e importe o arquivo de novo para encerrar as matrículas dos alunos que saíram."
        )
    importacao.save()
    return importacao


def _aplicar_importacao(aceitas: list[leitura_csv.Linha], encerrar_ausentes: bool) -> int:
    pessoas: dict[tuple[str, str], object] = {}
    disciplinas: dict[tuple[str, str, str], Disciplina] = {}
    alunos_por_disciplina: dict[int, set[int]] = defaultdict(set)

    for linha in aceitas:
        chave_professor = (linha.email_professor, Perfil.PROFESSOR)
        if chave_professor not in pessoas:
            pessoas[chave_professor], _ = contas.garantir_pessoa_com_perfil(
                linha.email_professor, Perfil.PROFESSOR
            )
        chave_aluno = (linha.email, Perfil.ALUNO)
        if chave_aluno not in pessoas:
            pessoas[chave_aluno], _ = contas.garantir_pessoa_com_perfil(
                linha.email, Perfil.ALUNO, nome=linha.nome
            )
        if linha.disciplina not in disciplinas:
            disciplinas[linha.disciplina], _ = garantir_disciplina(
                linha.codigo,
                linha.nome_disciplina,
                linha.turma,
                linha.semestre,
                pessoas[chave_professor],
            )
        disciplina = disciplinas[linha.disciplina]
        aluno = pessoas[chave_aluno]
        garantir_matricula(aluno, disciplina)
        alunos_por_disciplina[disciplina.id].add(aluno.id)

    encerradas = 0
    if encerrar_ausentes:
        for disciplina_id, alunos_ids in alunos_por_disciplina.items():
            encerradas += (
                Matricula.objects.filter(
                    disciplina_id=disciplina_id, situacao=Matricula.Situacao.ATIVA
                )
                .exclude(aluno_id__in=alunos_ids)
                .update(situacao=Matricula.Situacao.ENCERRADA, atualizada_em=timezone.now())
            )
    return encerradas
