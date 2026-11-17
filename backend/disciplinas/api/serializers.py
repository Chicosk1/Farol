from rest_framework import serializers

from disciplinas.leitura_csv import LIMITE_DE_BYTES
from disciplinas.models import Importacao
from disciplinas.servicos import FILTROS


class DisciplinaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo = serializers.CharField()
    nome = serializers.CharField()
    turma = serializers.CharField()
    semestre = serializers.CharField()
    professor_nome = serializers.CharField(source="professor.nome")
    favorita = serializers.BooleanField(help_text="Se a pessoa marcou a disciplina como favorita.")


class ConsultaDeDisciplinasSerializer(serializers.Serializer):
    busca = serializers.CharField(required=False, allow_blank=True, default="", max_length=100)
    filtro = serializers.ChoiceField(choices=FILTROS, required=False, default="todas")


class EnvioDeImportacaoSerializer(serializers.Serializer):
    arquivo = serializers.FileField(help_text="CSV em UTF-8, separado por vírgula, de até 5 MB.")

    def validate_arquivo(self, arquivo):
        if not arquivo.name.lower().endswith(".csv"):
            raise serializers.ValidationError("Envie um arquivo CSV (.csv).")
        if arquivo.size > LIMITE_DE_BYTES:
            raise serializers.ValidationError("O arquivo passa de 5 MB.")
        return arquivo


class ImportacaoCriadaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=Importacao.Status.choices)


class LinhaRejeitadaSerializer(serializers.Serializer):
    linha = serializers.IntegerField(
        help_text="Número da linha no arquivo; o cabeçalho é a linha 1."
    )
    motivo = serializers.CharField()


class ImportacaoSerializer(serializers.ModelSerializer):
    rejeitadas = LinhaRejeitadaSerializer(many=True)

    class Meta:
        model = Importacao
        fields = [
            "id",
            "status",
            "aceitas",
            "rejeitadas",
            "matriculas_encerradas",
            "erro",
            "aviso",
            "enviada_em",
        ]
        read_only_fields = fields
