from rest_framework import serializers

from questoes.models import QUANTIDADE_MAXIMA, QUANTIDADE_MINIMA


class PedidoDeGeracaoSerializer(serializers.Serializer):
    quantidade = serializers.IntegerField(
        min_value=QUANTIDADE_MINIMA,
        max_value=QUANTIDADE_MAXIMA,
        error_messages={
            "min_value": "Peça pelo menos 5 questões.",
            "max_value": "Peça no máximo 20 questões por vez.",
        },
    )


class GeracaoSerializer(serializers.Serializer):
    """O andamento de um pedido de rascunhos."""

    id = serializers.IntegerField()
    material = serializers.IntegerField(source="material_id")
    quantidade = serializers.IntegerField()
    status = serializers.ChoiceField(choices=["processando", "pronto", "erro"])
    geradas = serializers.IntegerField()
    descartadas = serializers.IntegerField()
    criado_em = serializers.DateTimeField()
    terminado_em = serializers.DateTimeField(allow_null=True)
