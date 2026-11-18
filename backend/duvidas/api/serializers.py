from rest_framework import serializers


class PreviaSerializer(serializers.Serializer):
    texto_filtrado = serializers.CharField()


class DuvidaEnviadaSerializer(serializers.Serializer):
    duvida_id = serializers.IntegerField()
    status = serializers.CharField()


class DuvidaDoProfessorSerializer(serializers.Serializer):
    """O que o professor vê: nunca o aluno, nem a hora do envio (DUV-RF-03)."""

    id = serializers.IntegerField()
    texto = serializers.CharField()
    data = serializers.DateField()
    status = serializers.CharField()
    nova = serializers.BooleanField()


class MudancaDeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["respondida", "oculta"])


class MinhaDuvidaSerializer(serializers.Serializer):
    mensagem_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=["aberta", "respondida"])
