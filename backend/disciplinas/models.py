"""Modelos do módulo disciplinas (spec 001)."""

from django.conf import settings
from django.db import models


class Disciplina(models.Model):
    """Uma oferta de disciplina: o mesmo código pode existir em turmas e semestres diferentes."""

    codigo = models.CharField("código", max_length=30)
    nome = models.CharField("nome", max_length=200)
    turma = models.CharField("turma", max_length=30)
    semestre = models.CharField("semestre", max_length=10, help_text="Por exemplo, 2026/2.")
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="professor responsável",
        on_delete=models.PROTECT,
        related_name="disciplinas_lecionadas",
    )

    class Meta:
        verbose_name = "disciplina"
        verbose_name_plural = "disciplinas"
        constraints = [
            models.UniqueConstraint(
                fields=["codigo", "turma", "semestre"], name="disciplina_unica_por_oferta"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} {self.nome} ({self.turma}, {self.semestre})"


class Matricula(models.Model):
    """Liga um aluno a uma disciplina. Encerrada, tira o acesso sem apagar o histórico."""

    class Situacao(models.TextChoices):
        ATIVA = "ativa", "Ativa"
        ENCERRADA = "encerrada", "Encerrada"

    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="aluno",
        on_delete=models.CASCADE,
        related_name="matriculas",
    )
    disciplina = models.ForeignKey(
        Disciplina,
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="matriculas",
    )
    situacao = models.CharField(
        "situação", max_length=10, choices=Situacao.choices, default=Situacao.ATIVA
    )
    atualizada_em = models.DateTimeField("atualizada em", auto_now=True)

    class Meta:
        verbose_name = "matrícula"
        verbose_name_plural = "matrículas"
        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "disciplina"], name="matricula_unica_por_aluno_e_disciplina"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.aluno_id} em {self.disciplina_id} ({self.situacao})"


class Favorito(models.Model):
    """Disciplina que a pessoa marcou como favorita. É da pessoa, e não do perfil em uso."""

    pessoa = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="pessoa",
        on_delete=models.CASCADE,
        related_name="favoritos",
    )
    disciplina = models.ForeignKey(
        Disciplina,
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="favoritos",
    )

    class Meta:
        verbose_name = "favorito"
        verbose_name_plural = "favoritos"
        constraints = [
            models.UniqueConstraint(
                fields=["pessoa", "disciplina"], name="favorito_unico_por_pessoa_e_disciplina"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.pessoa_id} favoritou {self.disciplina_id}"
