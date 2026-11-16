from rest_framework import serializers

from materiais.models import Material


class EnvioDeMaterialSerializer(serializers.Serializer):
    arquivo = serializers.FileField(help_text="O PDF da aula.")
    aula_numero = serializers.IntegerField(min_value=1, max_value=999)
    aula_titulo = serializers.CharField(max_length=200)


class MaterialEnviadoSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=Material.Status.choices)
