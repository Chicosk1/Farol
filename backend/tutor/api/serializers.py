from rest_framework import serializers

from tutor.models import JanelaProva
from tutor.servicos import LIMITE_DE_CARACTERES


class PerguntaSerializer(serializers.Serializer):
    texto = serializers.CharField(max_length=LIMITE_DE_CARACTERES)


class NovaJanelaSerializer(serializers.Serializer):
    """Sem início, a janela começa agora (modo prova imediato); sem fim, fica aberta."""

    inicio = serializers.DateTimeField(required=False)
    fim = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, dados):
        inicio, fim = dados.get("inicio"), dados.get("fim")
        if fim is not None and inicio is not None and fim <= inicio:
            raise serializers.ValidationError({"fim": ["O fim precisa ser depois do início."]})
        return dados


class JanelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JanelaProva
        fields = ["id", "inicio", "fim"]
