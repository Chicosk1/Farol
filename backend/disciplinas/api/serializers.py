from rest_framework import serializers

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
