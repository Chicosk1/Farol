from rest_framework import serializers

from materiais.models import Material


class EnvioDeMaterialSerializer(serializers.Serializer):
    arquivo = serializers.FileField(help_text="O PDF da aula.")
    aula_numero = serializers.IntegerField(min_value=1, max_value=999)
    aula_titulo = serializers.CharField(max_length=200)


class MaterialEnviadoSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=Material.Status.choices)


class MaterialDoAlunoSerializer(serializers.ModelSerializer):
    """O que o aluno vê: só materiais prontos, sem status, etapa, erro nem o caminho do arquivo."""

    class Meta:
        model = Material
        fields = ["id", "aula_numero", "aula_titulo", "paginas"]
        read_only_fields = fields


class MaterialDoProfessorSerializer(serializers.ModelSerializer):
    """O que o professor e a administração veem: todos os materiais, com o andamento."""

    status_rotulo = serializers.CharField(source="get_status_display", read_only=True)
    etapa_rotulo = serializers.CharField(source="get_etapa_display", read_only=True)

    class Meta:
        model = Material
        fields = [
            "id",
            "aula_numero",
            "aula_titulo",
            "paginas",
            "status",
            "status_rotulo",
            "etapa",
            "etapa_rotulo",
            "erro",
            "paginas_sem_texto",
            "versao",
            "criado_em",
        ]
        read_only_fields = fields


class PaginaDoPdfSerializer(serializers.Serializer):
    pagina = serializers.IntegerField(
        min_value=1, required=False, help_text="Página em que o visualizador deve abrir."
    )
