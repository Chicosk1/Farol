from django.conf import settings
from django.db import models
from django.utils import timezone


class Duvida(models.Model):
    """A dúvida que o material não respondeu, como o professor a vê (DUV-RF-03).

    Não tem ligação com o aluno: só a disciplina, o texto já filtrado e o dia, sem a hora.
    """

    class Status(models.TextChoices):
        ABERTA = "aberta", "Aberta"
        RESPONDIDA = "respondida", "Respondida em aula"
        OCULTA = "oculta", "Oculta"

    disciplina = models.ForeignKey(
        "disciplinas.Disciplina",
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="duvidas",
    )
    texto = models.TextField("texto sem dados pessoais")
    data = models.DateField("dia do envio", default=timezone.localdate)
    status = models.CharField(
        "status", max_length=10, choices=Status.choices, default=Status.ABERTA
    )
    vista = models.BooleanField("vista pelo professor", default=False)
    ocultada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="ocultada por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    ocultada_em = models.DateTimeField("ocultada em", null=True, blank=True)

    class Meta:
        verbose_name = "dúvida"
        verbose_name_plural = "dúvidas"
        ordering = ["-data", "-id"]

    def __str__(self) -> str:
        return self.texto[:60]


StatusDaDuvida = Duvida.Status


class EnvioDuvida(models.Model):
    """De que resposta "não encontrei" a dúvida saiu. Só o lado do aluno consulta (DUV-RNF-01)."""

    mensagem = models.OneToOneField(
        "tutor.Mensagem",
        verbose_name="resposta não encontrei",
        on_delete=models.CASCADE,
        related_name="envio_de_duvida",
    )
    duvida = models.ForeignKey(
        Duvida, verbose_name="dúvida", on_delete=models.CASCADE, related_name="envios"
    )
    enviada_em = models.DateTimeField("enviada em", default=timezone.now)

    class Meta:
        verbose_name = "envio de dúvida"
        verbose_name_plural = "envios de dúvida"

    def __str__(self) -> str:
        return f"Envio da dúvida {self.duvida_id}"
