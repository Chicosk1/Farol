from rest_framework import serializers


class IndicadoresSerializer(serializers.Serializer):
    alunos_ativos = serializers.IntegerField()
    matriculados = serializers.IntegerField()
    perguntas = serializers.IntegerField()
    acerto_medio = serializers.IntegerField(allow_null=True)
    duvidas_sem_resposta = serializers.IntegerField()


class TopicoSerializer(serializers.Serializer):
    nome = serializers.CharField()
    alunos = serializers.IntegerField()
    exemplos = serializers.ListField(child=serializers.CharField())
    material = serializers.IntegerField()


class AcertoSerializer(serializers.Serializer):
    topico = serializers.CharField()
    taxa = serializers.IntegerField()
    alunos = serializers.IntegerField()
    material = serializers.IntegerField()


class QuestaoComAcertoSerializer(serializers.Serializer):
    enunciado = serializers.CharField()
    taxa = serializers.IntegerField()


class SugestaoSerializer(serializers.Serializer):
    nome = serializers.CharField()
    material = serializers.IntegerField()


class RadarSerializer(serializers.Serializer):
    """Só dados agregados: nenhum nome, e-mail, horário ou contagem por aluno (RAD-RF-06)."""

    semana = serializers.DateField()
    rotulo = serializers.CharField()
    indicadores = IndicadoresSerializer()
    pouco_uso = serializers.BooleanField()
    topicos = TopicoSerializer(many=True)
    acertos = AcertoSerializer(many=True)
    questoes_com_menor_acerto = QuestaoComAcertoSerializer(many=True)
    sugestao = SugestaoSerializer(many=True)


class SemanaSerializer(serializers.Serializer):
    semana = serializers.DateField()
    rotulo = serializers.CharField()
    atual = serializers.BooleanField()


class FiltroDaSemanaSerializer(serializers.Serializer):
    semana = serializers.DateField(required=False)


class ExemploSerializer(serializers.Serializer):
    texto = serializers.CharField(max_length=2000)
