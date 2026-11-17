from django.conf import settings
from django.db import models
from django.utils import timezone


class Notificacao(models.Model):
    """Um aviso para uma pessoa, mostrado no sino do cabeçalho (MAT-RF-06, DUV-RF-06)."""

    class Tipo(models.TextChoices):
        MATERIAL_PRONTO = "material_pronto", "Material pronto"
        MATERIAL_ATENCAO = "material_atencao", "Material precisa de atenção"
        MATERIAL_ERRO = "material_erro", "Material com erro"
        DUVIDA_NOVA = "duvida_nova", "Dúvida nova"

    pessoa = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="pessoa",
        on_delete=models.CASCADE,
        related_name="notificacoes",
    )
    tipo = models.CharField("tipo", max_length=30, choices=Tipo.choices)
    texto = models.CharField("texto", max_length=300)
    link = models.CharField("link", max_length=200, blank=True)
    lida = models.BooleanField("lida", default=False)
    criada_em = models.DateTimeField("criada em", default=timezone.now)

    class Meta:
        verbose_name = "notificação"
        verbose_name_plural = "notificações"
        ordering = ["-criada_em", "-id"]
        indexes = [models.Index(fields=["pessoa", "lida"], name="notificacao_pessoa_lida")]

    def __str__(self) -> str:
        return self.texto
