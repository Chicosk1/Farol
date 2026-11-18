from rest_framework import serializers

from questoes.models import (
    QUANTIDADE_MAXIMA,
    QUANTIDADE_MINIMA,
    StatusDaGeracao,
    StatusDaQuestao,
)


class PedidoDeGeracaoSerializer(serializers.Serializer):
    quantidade = serializers.IntegerField(
        min_value=QUANTIDADE_MINIMA,
        max_value=QUANTIDADE_MAXIMA,
        error_messages={
            "min_value": "Peça pelo menos 5 questões.",
            "max_value": "Peça no máximo 20 questões por vez.",
        },
    )


class TrechoDaQuestaoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    pagina = serializers.IntegerField()


class QuestaoDoProfessorSerializer(serializers.Serializer):
    """A questão completa, com o gabarito: só o professor da disciplina a vê."""

    id = serializers.IntegerField()
    material = serializers.IntegerField(source="material_id")
    aula_numero = serializers.IntegerField(source="material.aula_numero")
    aula_titulo = serializers.CharField(source="material.aula_titulo")
    enunciado = serializers.CharField()
    alternativas = serializers.ListField(child=serializers.CharField())
    correta = serializers.IntegerField()
    justificativa = serializers.CharField()
    topico = serializers.CharField()
    trecho = TrechoDaQuestaoSerializer()
    status = serializers.ChoiceField(choices=StatusDaQuestao.choices)
    nova = serializers.BooleanField()
    editada = serializers.BooleanField()
    origem_retirada = serializers.SerializerMethodField()

    def get_origem_retirada(self, questao) -> bool:
        return questao.material.status == "retirado"


class ContagensSerializer(serializers.Serializer):
    pendente = serializers.IntegerField()
    publicada = serializers.IntegerField()
    descartada = serializers.IntegerField()


class QuestoesDaDisciplinaSerializer(serializers.Serializer):
    contagens = ContagensSerializer()
    questoes = QuestaoDoProfessorSerializer(many=True)


class FiltroDeQuestoesSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=StatusDaQuestao.choices, default="pendente")
    material = serializers.IntegerField(required=False)


class MudancaDeQuestaoSerializer(serializers.Serializer):
    """Campos a editar (só em pendentes) e, ou, o novo status."""

    enunciado = serializers.CharField(required=False, allow_blank=True, trim_whitespace=False)
    alternativas = serializers.ListField(
        child=serializers.CharField(allow_blank=True, trim_whitespace=False), required=False
    )
    correta = serializers.IntegerField(required=False)
    justificativa = serializers.CharField(required=False, allow_blank=True)
    topico = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=StatusDaQuestao.choices, required=False)


class GeracaoSerializer(serializers.Serializer):
    """O andamento de um pedido de rascunhos."""

    id = serializers.IntegerField()
    material = serializers.IntegerField(source="material_id")
    quantidade = serializers.IntegerField()
    status = serializers.ChoiceField(choices=StatusDaGeracao.choices)
    geradas = serializers.IntegerField()
    descartadas = serializers.IntegerField()
    criado_em = serializers.DateTimeField()
    terminado_em = serializers.DateTimeField(allow_null=True)


class TrechoCitadoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rotulo = serializers.CharField()


class RetornoDaQuestaoSerializer(serializers.Serializer):
    """O retorno depois de responder: só aqui o aluno recebe o gabarito (QUE-RF-08)."""

    questao = serializers.IntegerField()
    alternativa = serializers.IntegerField()
    acerto = serializers.BooleanField()
    correta = serializers.IntegerField()
    justificativa = serializers.CharField()
    topico = serializers.CharField()
    trecho = TrechoCitadoSerializer()


class QuestaoDoQuizSerializer(serializers.Serializer):
    """A questão como o aluno a vê antes de responder: sem o gabarito nem a justificativa."""

    id = serializers.IntegerField()
    enunciado = serializers.CharField()
    alternativas = serializers.ListField(child=serializers.CharField())
    topico = serializers.CharField()


class QuizSerializer(serializers.Serializer):
    material = serializers.IntegerField()
    disciplina = serializers.IntegerField()
    aula_numero = serializers.IntegerField()
    aula_titulo = serializers.CharField()
    pausado = serializers.BooleanField()
    questoes = QuestaoDoQuizSerializer(many=True)
    respostas = RetornoDaQuestaoSerializer(many=True)
    concluido = serializers.BooleanField()


class RespostaDoAlunoSerializer(serializers.Serializer):
    alternativa = serializers.IntegerField(min_value=0, max_value=3)


class QuizDaAulaSerializer(serializers.Serializer):
    material = serializers.IntegerField()
    aula_numero = serializers.IntegerField()
    aula_titulo = serializers.CharField()
    questoes = serializers.IntegerField()
    respondidas = serializers.IntegerField()
    acertos = serializers.IntegerField()
