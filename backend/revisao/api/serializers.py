from rest_framework import serializers

from revisao.models import AvaliacaoDoCartao


class TrechoDaRevisaoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rotulo = serializers.CharField()


class RetornoNaRevisaoSerializer(serializers.Serializer):
    questao = serializers.IntegerField()
    alternativa = serializers.IntegerField()
    acerto = serializers.BooleanField()
    correta = serializers.IntegerField()
    justificativa = serializers.CharField()
    topico = serializers.CharField()
    trecho = TrechoDaRevisaoSerializer()


class CartaoDaSessaoSerializer(serializers.Serializer):
    """O cartão antes da resposta: sem o gabarito (como no quiz)."""

    id = serializers.IntegerField()
    disciplina = serializers.IntegerField()
    disciplina_nome = serializers.CharField()
    enunciado = serializers.CharField()
    alternativas = serializers.ListField(child=serializers.CharField())
    topico = serializers.CharField()


class RetornoDoCartaoSerializer(RetornoNaRevisaoSerializer):
    cartao = serializers.IntegerField()


class RespostaDaSessaoSerializer(RetornoDoCartaoSerializer):
    avaliacao = serializers.CharField(allow_blank=True)
    volta = serializers.CharField(allow_blank=True)


class DiaDaSequenciaSerializer(serializers.Serializer):
    data = serializers.DateField()
    feita = serializers.BooleanField()


class RevisaoDeHojeSerializer(serializers.Serializer):
    data = serializers.DateField()
    cartoes = CartaoDaSessaoSerializer(many=True)
    respostas = RespostaDaSessaoSerializer(many=True)
    concluida = serializers.BooleanField()
    disciplinas = serializers.ListField(child=serializers.CharField())
    minutos = serializers.IntegerField()
    tem_questoes = serializers.BooleanField()
    sequencia = DiaDaSequenciaSerializer(many=True)
    dias_seguidos = serializers.IntegerField()


class RespostaAoCartaoSerializer(serializers.Serializer):
    alternativa = serializers.IntegerField(min_value=0, max_value=3)


class AvaliacaoDoCartaoSerializer(serializers.Serializer):
    avaliacao = serializers.ChoiceField(choices=AvaliacaoDoCartao.choices)


class AgendaDoCartaoSerializer(serializers.Serializer):
    proxima_data = serializers.DateField()
    texto = serializers.CharField()


class LembreteSerializer(serializers.Serializer):
    ligado = serializers.BooleanField()
    horario = serializers.TimeField(format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])
