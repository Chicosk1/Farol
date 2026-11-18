"""Modelos do módulo tutor (spec 003)."""

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class ConfiguracaoTutor(models.Model):
    """O que o professor controla no tutor da sua disciplina (TUT-RF-06, 08 e 10)."""

    LIMITES = [
        (20, "20 perguntas por dia"),
        (40, "40 perguntas por dia"),
        (60, "60 perguntas por dia"),
    ]

    disciplina = models.OneToOneField(
        "disciplinas.Disciplina",
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="configuracao_do_tutor",
    )
    modo_pistas = models.BooleanField("modo pistas", default=True)
    limite_diario = models.PositiveSmallIntegerField("limite diário", choices=LIMITES, default=40)
    politica = models.TextField("política de uso de IA", blank=True)

    class Meta:
        verbose_name = "configuração do tutor"
        verbose_name_plural = "configurações do tutor"

    def __str__(self) -> str:
        return f"Tutor de {self.disciplina_id}"


class JanelaProva(models.Model):
    """Período em que o tutor da disciplina fica pausado. Modo prova imediato: fim em aberto."""

    disciplina = models.ForeignKey(
        "disciplinas.Disciplina",
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="janelas_de_prova",
    )
    inicio = models.DateTimeField("início")
    fim = models.DateTimeField("fim", null=True, blank=True)
    criada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criada por",
        on_delete=models.SET_NULL,
        null=True,
        related_name="janelas_de_prova_criadas",
    )

    class Meta:
        verbose_name = "janela de prova"
        verbose_name_plural = "janelas de prova"
        ordering = ["-inicio"]

    def __str__(self) -> str:
        return f"Prova de {self.disciplina_id} a partir de {self.inicio:%d/%m %H:%M}"


class Conversa(models.Model):
    """As perguntas e respostas de um aluno numa disciplina. Só o próprio aluno a vê."""

    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="aluno",
        on_delete=models.CASCADE,
        related_name="conversas_com_o_tutor",
    )
    disciplina = models.ForeignKey(
        "disciplinas.Disciplina",
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="conversas",
    )
    criada_em = models.DateTimeField("criada em", default=timezone.now)

    class Meta:
        verbose_name = "conversa"
        verbose_name_plural = "conversas"
        ordering = ["-criada_em", "-id"]

    def __str__(self) -> str:
        return f"Conversa {self.pk}"


class Mensagem(models.Model):
    class Autor(models.TextChoices):
        ALUNO = "aluno", "Aluno"
        TUTOR = "tutor", "Tutor"

    class Tipo(models.TextChoices):
        RESPOSTA = "resposta", "Resposta"
        PISTAS = "pistas", "Modo pistas"
        NAO_ENCONTRADO = "nao_encontrado", "Não encontrei no material"
        SAUDACAO = "saudacao", "Saudação"
        ERRO = "erro", "Erro"

    class Avaliacao(models.TextChoices):
        NENHUMA = "", "Sem avaliação"
        UTIL = "util", "Útil"
        NAO_UTIL = "nao_util", "Não útil"
        INCORRETA = "incorreta", "Incorreta"

    conversa = models.ForeignKey(
        Conversa, verbose_name="conversa", on_delete=models.CASCADE, related_name="mensagens"
    )
    autor = models.CharField("autor", max_length=5, choices=Autor.choices)
    texto = models.TextField("texto")
    tipo = models.CharField("tipo", max_length=14, choices=Tipo.choices, default=Tipo.RESPOSTA)
    avaliacao = models.CharField(
        "avaliação", max_length=10, choices=Avaliacao.choices, default=Avaliacao.NENHUMA, blank=True
    )
    criada_em = models.DateTimeField("criada em", default=timezone.now)

    class Meta:
        verbose_name = "mensagem"
        verbose_name_plural = "mensagens"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.autor}: {self.texto[:40]}"


class Citacao(models.Model):
    """O trecho do material que sustenta uma resposta (TUT-RF-02)."""

    mensagem = models.ForeignKey(
        Mensagem, verbose_name="mensagem", on_delete=models.CASCADE, related_name="citacoes"
    )
    trecho = models.ForeignKey(
        "materiais.Trecho", verbose_name="trecho", on_delete=models.CASCADE, related_name="citacoes"
    )
    ordem = models.PositiveSmallIntegerField("ordem")

    class Meta:
        verbose_name = "citação"
        verbose_name_plural = "citações"
        ordering = ["mensagem_id", "ordem"]
        constraints = [
            models.UniqueConstraint(
                fields=["mensagem", "ordem"], name="citacao_unica_por_mensagem_e_ordem"
            ),
        ]

    def __str__(self) -> str:
        return self.rotulo

    @property
    def rotulo(self) -> str:
        """O texto da citação, como o aluno a vê: "Aula 4, p. 5"."""
        return f"Aula {self.trecho.material.aula_numero}, p. {self.trecho.pagina}"


AvaliacaoDaMensagem = Mensagem.Avaliacao  # nome do enum no contrato (ENUM_NAME_OVERRIDES)


class RegistroUso(models.Model):
    """Uma pergunta ao tutor, sem identificação do aluno (TUT-RF-12).

    Só guarda um identificador pseudônimo por disciplina, que permite contar alunos distintos
    (regra dos 5 alunos do radar) sem revelar quem são. Não há ligação com Conversa nem Mensagem,
    por isso a avaliação do aluno fica só na mensagem: ligar os dois revelaria o pseudônimo.
    """

    aluno_pseudonimo = models.CharField("aluno (pseudônimo)", max_length=64)
    disciplina = models.ForeignKey(
        "disciplinas.Disciplina",
        verbose_name="disciplina",
        on_delete=models.CASCADE,
        related_name="registros_de_uso",
    )
    pergunta_filtrada = models.TextField("pergunta sem dados pessoais")
    trechos = ArrayField(models.PositiveIntegerField(), verbose_name="trechos usados", default=list)
    tipo = models.CharField("tipo da resposta", max_length=14)
    tokens_entrada = models.PositiveIntegerField("tokens de entrada", default=0)
    tokens_saida = models.PositiveIntegerField("tokens de saída", default=0)
    custo = models.DecimalField("custo (R$)", max_digits=10, decimal_places=6, default=0)
    criado_em = models.DateTimeField("criado em", default=timezone.now)

    class Meta:
        verbose_name = "registro de uso"
        verbose_name_plural = "registros de uso"
        indexes = [models.Index(fields=["disciplina", "criado_em"], name="uso_disciplina_data")]

    def __str__(self) -> str:
        return f"Uso {self.pk} em {self.disciplina_id}"


class RevisaoResposta(models.Model):
    """Fila da equipe com as respostas que os alunos marcaram como incorretas (TUT-RF-09)."""

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        REVISADA = "revisada", "Revisada"

    mensagem = models.OneToOneField(
        Mensagem, verbose_name="mensagem", on_delete=models.CASCADE, related_name="revisao"
    )
    status = models.CharField(
        "status", max_length=10, choices=Status.choices, default=Status.PENDENTE
    )
    nota_da_equipe = models.TextField("nota da equipe", blank=True)

    class Meta:
        verbose_name = "revisão de resposta"
        verbose_name_plural = "revisões de resposta"

    def __str__(self) -> str:
        return f"Revisão da mensagem {self.mensagem_id} ({self.status})"
