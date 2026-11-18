import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


class AvaliacaoDoCartao(models.TextChoices):
    DIFICIL = "dificil", "Difícil"
    BOM = "bom", "Bom"
    FACIL = "facil", "Fácil"


class Cartao(models.Model):
    """Uma questão publicada na agenda de revisão de um aluno (REV-RF-01), agendada pelo SM-2."""

    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="aluno",
        on_delete=models.CASCADE,
        related_name="cartoes_de_revisao",
    )
    questao = models.ForeignKey(
        "questoes.Questao",
        verbose_name="questão",
        on_delete=models.CASCADE,
        related_name="cartoes_de_revisao",
    )
    facilidade = models.FloatField("facilidade", default=2.5)
    intervalo_dias = models.PositiveIntegerField("intervalo atual (dias)", default=0)
    repeticoes = models.PositiveIntegerField("acertos seguidos", default=0)
    proxima_data = models.DateField("próxima revisão", default=timezone.localdate)
    ultima_avaliacao = models.CharField("última avaliação", max_length=7, blank=True)

    class Meta:
        verbose_name = "cartão de revisão"
        verbose_name_plural = "cartões de revisão"
        constraints = [
            models.UniqueConstraint(fields=["aluno", "questao"], name="cartao_aluno_questao")
        ]
        indexes = [models.Index(fields=["aluno", "proxima_data"], name="cartao_aluno_data")]

    def __str__(self) -> str:
        return f"Cartão da questão {self.questao_id} de {self.aluno_id}"


class SessaoRevisao(models.Model):
    """A revisão de um dia: até 10 cartões, na ordem, e as respostas e avaliações (REV-RF-02)."""

    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="aluno",
        on_delete=models.CASCADE,
        related_name="sessoes_de_revisao",
    )
    data = models.DateField("dia")
    cartoes = models.JSONField("cartões, na ordem", default=list)
    # Uma entrada por cartão respondido: {"cartao", "alternativa", "acerto", "avaliacao"}.
    respostas = models.JSONField("respostas", default=list, blank=True)
    concluida = models.BooleanField("concluída", default=False)

    class Meta:
        verbose_name = "sessão de revisão"
        verbose_name_plural = "sessões de revisão"
        constraints = [models.UniqueConstraint(fields=["aluno", "data"], name="sessao_aluno_dia")]

    def __str__(self) -> str:
        return f"Revisão de {self.aluno_id} em {self.data}"


class PreferenciaLembrete(models.Model):
    """O lembrete diário da revisão, desligado por padrão (REV-RF-09). Nesta versão, por e-mail."""

    aluno = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="aluno",
        on_delete=models.CASCADE,
        related_name="lembrete_de_revisao",
    )
    ligado = models.BooleanField("ligado", default=False)
    horario = models.TimeField("horário", default=datetime.time(19, 0))
    ultimo_envio = models.DateField("último envio", null=True, blank=True)

    class Meta:
        verbose_name = "preferência de lembrete"
        verbose_name_plural = "preferências de lembrete"

    def __str__(self) -> str:
        return f"Lembrete de {self.aluno_id}"
