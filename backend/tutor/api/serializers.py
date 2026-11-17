from rest_framework import serializers

from tutor.servicos import LIMITE_DE_CARACTERES


class PerguntaSerializer(serializers.Serializer):
    texto = serializers.CharField(max_length=LIMITE_DE_CARACTERES)
