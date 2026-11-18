from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from django.utils import timezone

QUANTIDADE_MINIMA = 5
QUANTIDADE_MAXIMA = 20
ALTERNATIVAS = 4


class PedidoGeracao(models.Model):
    """O pedido do professor de N rascunhos de uma aula, gerados em segundo plano (QUE-RF-01)."""

    class Status(models.TextChoices):
        PROCESSANDO = "processando", "Gerando"
        PRONTO = "pronto", "Pronto"
        ERRO = "erro", "Erro"

    material = models.ForeignKey(
        "materiais.Material",
        verbose_name="aula",
        on_delete=models.CASCADE,
        related_name="pedidos_de_questoes",
    )
    quantidade = models.PositiveSmallIntegerField("quantidade pedida")
    status = models.CharField(
        "status", max_length=11, choices=Status.choices, default=Status.PROCESSANDO
    )
    geradas = models.PositiveSmallIntegerField("rascunhos aceitos", default=0)
    descartadas = models.PositiveSmallIntegerField("descartadas na validação", default=0)
    pedido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="pedido por",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    terminado_em = models.DateTimeField("terminado em", null=True, blank=True)

    class Meta:
        verbose_name = "pedido de geração"
        verbose_name_plural = "pedidos de geração"
        constraints = [
            models.CheckConstraint(
                condition=Q(quantidade__gte=QUANTIDADE_MINIMA, quantidade__lte=QUANTIDADE_MAXIMA),
                name="pedido_quantidade_de_5_a_20",
            )
        ]

    def __str__(self) -> str:
        return f"{self.quantidade} questões da aula {self.material_id}"


StatusDaGeracao = PedidoGeracao.Status


class Questao(models.Model):
    """Uma questão de múltipla escolha de uma aula. Só a publicada chega ao aluno (QUE-RF-04)."""

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        PUBLICADA = "publicada", "Publicada"
        DESCARTADA = "descartada", "Descartada"

    material = models.ForeignKey(
        "materiais.Material",
        verbose_name="aula",
        on_delete=models.CASCADE,
        related_name="questoes",
    )
    pedido = models.ForeignKey(
        PedidoGeracao,
        verbose_name="pedido de geração",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questoes",
    )
    enunciado = models.TextField("enunciado")
    alternativas = ArrayField(models.TextField(), verbose_name="alternativas", size=ALTERNATIVAS)
    correta = models.PositiveSmallIntegerField("alternativa correta (0 a 3)")
    justificativa = models.TextField("justificativa")
    topico = models.CharField("tópico", max_length=120)
    trecho = models.ForeignKey(
        "materiais.Trecho",
        verbose_name="trecho de origem",
        on_delete=models.CASCADE,
        related_name="questoes",
    )
    status = models.CharField(
        "status", max_length=10, choices=Status.choices, default=Status.PENDENTE
    )
    nova = models.BooleanField("novo rascunho, ainda não visto", default=True)
    editada = models.BooleanField("editada pelo professor", default=False)
    criada_em = models.DateTimeField("criada em", auto_now_add=True)
    atualizada_em = models.DateTimeField("atualizada em", auto_now=True)

    class Meta:
        verbose_name = "questão"
        verbose_name_plural = "questões"
        ordering = ["id"]
        indexes = [models.Index(fields=["material", "status"], name="questao_material_status")]
        constraints = [
            models.CheckConstraint(
                condition=Q(correta__lte=ALTERNATIVAS - 1), name="questao_correta_de_0_a_3"
            ),
            models.CheckConstraint(
                condition=Q(alternativas__len=ALTERNATIVAS), name="questao_quatro_alternativas"
            ),
        ]

    def __str__(self) -> str:
        return self.enunciado[:60]


StatusDaQuestao = Questao.Status


class RespostaQuiz(models.Model):
    """Uma resposta a uma questão, sem identificação do aluno (QUE-RF-11).

    Guarda só o pseudônimo por disciplina e o dia, sem a hora: basta para a taxa de acerto da
    semana no radar (RAD-RNF-02) e não permite ligar a resposta ao progresso do aluno.
    """

    class Contexto(models.TextChoices):
        QUIZ = "quiz", "Quiz da aula"
        REVISAO = "revisao", "Revisão do dia"

    questao = models.ForeignKey(
        Questao, verbose_name="questão", on_delete=models.CASCADE, related_name="respostas"
    )
    aluno_pseudonimo = models.CharField("aluno (pseudônimo)", max_length=64)
    alternativa = models.PositiveSmallIntegerField("alternativa escolhida")
    acerto = models.BooleanField("acertou")
    respondida_em = models.DateField("dia da resposta", default=timezone.localdate)
    contexto = models.CharField(
        "onde respondeu", max_length=7, choices=Contexto.choices, default=Contexto.QUIZ
    )

    class Meta:
        verbose_name = "resposta de quiz"
        verbose_name_plural = "respostas de quiz"
        indexes = [models.Index(fields=["questao", "respondida_em"], name="resposta_questao_dia")]

    def __str__(self) -> str:
        return f"Resposta à questão {self.questao_id}"


class ProgressoQuiz(models.Model):
    """Onde o aluno parou no quiz de uma aula, para continuar dali (caso de borda da spec 005)."""

    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="aluno",
        on_delete=models.CASCADE,
        related_name="progressos_de_quiz",
    )
    material = models.ForeignKey(
        "materiais.Material",
        verbose_name="aula",
        on_delete=models.CASCADE,
        related_name="progressos_de_quiz",
    )
    indice_atual = models.PositiveSmallIntegerField("questão atual", default=0)
    # Uma entrada por questão respondida: {"questao": id, "alternativa": n, "acerto": bool}.
    respostas = models.JSONField("respostas desta tentativa", default=list, blank=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "progresso no quiz"
        verbose_name_plural = "progressos no quiz"
        constraints = [
            models.UniqueConstraint(fields=["aluno", "material"], name="progresso_aluno_material")
        ]

    def __str__(self) -> str:
        return f"Quiz da aula {self.material_id} de {self.aluno_id}"
