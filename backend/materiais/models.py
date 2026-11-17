"""Modelos do módulo materiais (spec 002)."""

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from pgvector.django import HnswIndex, VectorField


class Material(models.Model):
    """O PDF de uma aula de uma disciplina, enviado pelo professor."""

    class Status(models.TextChoices):
        PROCESSANDO = "processando", "Processando"
        PRONTO = "pronto", "Pronto para o tutor"
        ATENCAO = "atencao", "Precisa de atenção"
        ERRO = "erro", "Erro, tente de novo"
        RETIRADO = "retirado", "Retirado"
        SUBSTITUIDO = "substituido", "Substituído pela versão nova"

    class Etapa(models.TextChoices):
        ENVIANDO = "enviando", "Enviando arquivo"
        LENDO = "lendo", "Lendo as páginas"
        DIVIDINDO = "dividindo", "Dividindo em trechos"
        VETORIZANDO = "vetorizando", "Gerando a busca semântica"
        PRONTO = "pronto", "Pronto para o tutor"

    disciplina = models.ForeignKey(
        "disciplinas.Disciplina",
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="materiais",
    )
    aula_numero = models.PositiveSmallIntegerField("número da aula")
    aula_titulo = models.CharField("título da aula", max_length=200)
    arquivo = models.FileField("arquivo", upload_to="materiais/")
    paginas = models.PositiveIntegerField("páginas", default=0)
    status = models.CharField(
        "status", max_length=12, choices=Status.choices, default=Status.PROCESSANDO
    )
    etapa = models.CharField(
        "etapa do processamento", max_length=12, choices=Etapa.choices, default=Etapa.ENVIANDO
    )
    versao = models.PositiveIntegerField("versão", default=1)
    substitui = models.ForeignKey(
        "self",
        verbose_name="substitui",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="substituido_por",
    )
    paginas_sem_texto = ArrayField(
        models.PositiveIntegerField(), verbose_name="páginas sem texto", default=list, blank=True
    )
    erro = models.TextField("mensagem de erro", blank=True)
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="enviado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="materiais_enviados",
    )
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "material"
        verbose_name_plural = "materiais"
        ordering = ["aula_numero", "id"]
        indexes = [models.Index(fields=["disciplina", "status"], name="material_disciplina_status")]

    def __str__(self) -> str:
        return f"Aula {self.aula_numero}: {self.aula_titulo} ({self.disciplina.nome})"


class Trecho(models.Model):
    """Um pedaço do texto de uma página, com o vetor que permite achá-lo pelo sentido."""

    material = models.ForeignKey(
        Material, verbose_name="material", on_delete=models.CASCADE, related_name="trechos"
    )
    pagina = models.PositiveIntegerField("página")
    ordem = models.PositiveIntegerField("ordem na página")
    texto = models.TextField("texto")
    inicio = models.PositiveIntegerField(
        "início na página", help_text="Posição do primeiro caractere."
    )
    fim = models.PositiveIntegerField(
        "fim na página", help_text="Posição depois do último caractere."
    )
    vetor = VectorField(dimensions=settings.FAROL_DIMENSAO_DO_VETOR)

    class Meta:
        verbose_name = "trecho"
        verbose_name_plural = "trechos"
        ordering = ["material_id", "pagina", "ordem"]
        constraints = [
            models.UniqueConstraint(
                fields=["material", "pagina", "ordem"], name="trecho_unico_por_material_e_ordem"
            ),
        ]
        indexes = [
            HnswIndex(
                name="trecho_vetor_hnsw",
                fields=["vetor"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self) -> str:
        return f"{self.material_id} p. {self.pagina} #{self.ordem}"


# Nome direto para o contrato OpenAPI (ENUM_NAME_OVERRIDES não importa classes aninhadas).
StatusDoMaterial = Material.Status
