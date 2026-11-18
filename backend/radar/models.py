from django.conf import settings
from django.db import models
from django.utils import timezone


class RadarSemanal(models.Model):
    """O radar calculado de uma semana (de segunda a domingo), pronto para a tela (RAD-RNF-01)."""

    disciplina = models.ForeignKey(
        "disciplinas.Disciplina",
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="radares",
    )
    semana = models.DateField("segunda-feira da semana")
    dados = models.JSONField("indicadores, tópicos, acertos e sugestão", default=dict)
    calculado_em = models.DateTimeField("calculado em", default=timezone.now)

    class Meta:
        verbose_name = "radar semanal"
        verbose_name_plural = "radares semanais"
        constraints = [
            models.UniqueConstraint(fields=["disciplina", "semana"], name="radar_disciplina_semana")
        ]

    def __str__(self) -> str:
        return f"Radar de {self.disciplina_id} na semana de {self.semana}"


class ExemploOculto(models.Model):
    """Uma pergunta de exemplo que o professor escondeu: não volta ao radar (RAD-RF-05)."""

    disciplina = models.ForeignKey(
        "disciplinas.Disciplina",
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="exemplos_ocultos",
    )
    hash_texto = models.CharField("hash do texto", max_length=64)
    ocultado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="ocultado por",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    data = models.DateTimeField("ocultado em", default=timezone.now)

    class Meta:
        verbose_name = "exemplo oculto"
        verbose_name_plural = "exemplos ocultos"
        constraints = [
            models.UniqueConstraint(
                fields=["disciplina", "hash_texto"], name="exemplo_oculto_unico"
            )
        ]

    def __str__(self) -> str:
        return f"Exemplo oculto em {self.disciplina_id}"
