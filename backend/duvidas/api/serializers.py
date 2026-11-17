from rest_framework import serializers


class PreviaSerializer(serializers.Serializer):
    texto_filtrado = serializers.CharField()


class DuvidaEnviadaSerializer(serializers.Serializer):
    duvida_id = serializers.IntegerField()
    status = serializers.CharField()
