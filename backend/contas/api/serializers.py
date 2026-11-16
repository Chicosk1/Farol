from rest_framework import serializers

from contas.models import Perfil


class EuSerializer(serializers.Serializer):
    """A pessoa que está usando o Farol, com os perfis dela e o perfil em uso."""

    id = serializers.IntegerField()
    email = serializers.EmailField()
    nome = serializers.CharField()
    perfis = serializers.ListField(child=serializers.ChoiceField(choices=Perfil.choices))
    perfil_ativo = serializers.ChoiceField(choices=Perfil.choices, allow_null=True)
    precisa_ver_aviso = serializers.BooleanField(
        help_text="Se o aluno ainda precisa ler a versão atual do aviso de privacidade."
    )


class EntradaDeDesenvolvimentoSerializer(serializers.Serializer):
    email = serializers.EmailField()


class TrocaDePerfilSerializer(serializers.Serializer):
    perfil = serializers.ChoiceField(choices=Perfil.choices)


class ItemDoAvisoSerializer(serializers.Serializer):
    titulo = serializers.CharField()
    texto = serializers.CharField()


class AvisoDePrivacidadeSerializer(serializers.Serializer):
    versao = serializers.CharField()
    titulo = serializers.CharField()
    itens = ItemDoAvisoSerializer(many=True)


class CienciaDoAvisoSerializer(serializers.Serializer):
    versao = serializers.CharField(help_text="A versão do aviso que a pessoa leu.")
