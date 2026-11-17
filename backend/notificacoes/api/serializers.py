from rest_framework import serializers

from notificacoes.models import Notificacao


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = ["id", "tipo", "texto", "link", "lida", "criada_em"]


class NotificacoesSerializer(serializers.Serializer):
    notificacoes = NotificacaoSerializer(many=True)
    nao_lidas = serializers.IntegerField()
