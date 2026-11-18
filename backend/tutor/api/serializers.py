from rest_framework import serializers

from tutor.models import Citacao, ConfiguracaoTutor, JanelaProva, Mensagem
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


class ConfiguracaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoTutor
        fields = ["modo_pistas", "limite_diario", "politica", "resumo_semanal"]


class CitacaoSerializer(serializers.ModelSerializer):
    """A citação como o evento citacao da resposta em streaming."""

    rotulo = serializers.CharField(read_only=True)
    trecho_id = serializers.IntegerField(read_only=True)
    material_id = serializers.IntegerField(source="trecho.material_id", read_only=True)
    pagina = serializers.IntegerField(source="trecho.pagina", read_only=True)

    class Meta:
        model = Citacao
        fields = ["ordem", "rotulo", "trecho_id", "material_id", "pagina"]


class MensagemSerializer(serializers.ModelSerializer):
    citacoes = CitacaoSerializer(many=True, read_only=True)

    class Meta:
        model = Mensagem
        fields = ["id", "autor", "texto", "tipo", "avaliacao", "criada_em", "citacoes"]


class UsoDoDiaSerializer(serializers.Serializer):
    usadas = serializers.IntegerField()
    limite = serializers.IntegerField()


class EstadoDoTutorSerializer(serializers.Serializer):
    modo_pistas = serializers.BooleanField()
    politica = serializers.CharField(allow_blank=True)
    pausado = serializers.BooleanField()
    uso = UsoDoDiaSerializer(source="*")
    conversa_id = serializers.IntegerField(allow_null=True)
    mensagens = MensagemSerializer(many=True)
    sugestoes = serializers.ListField(child=serializers.CharField())


class AvaliacaoSerializer(serializers.Serializer):
    """util, nao_util ou incorreta; vazio desfaz a marcação."""

    avaliacao = serializers.ChoiceField(choices=Mensagem.Avaliacao.choices, allow_blank=True)


class ConversaDoHistoricoSerializer(serializers.Serializer):
    disciplina_id = serializers.IntegerField()
    disciplina_nome = serializers.CharField()
    mensagens = serializers.IntegerField()
    ultima_em = serializers.DateTimeField()
