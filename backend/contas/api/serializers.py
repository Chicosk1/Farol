from rest_framework import serializers

from contas.models import Perfil


class EuSerializer(serializers.Serializer):
    """A pessoa que está usando o Farol, com os perfis dela e o perfil em uso."""

    id = serializers.IntegerField()
    email = serializers.EmailField()
    nome = serializers.CharField()
    perfis = serializers.ListField(child=serializers.ChoiceField(choices=Perfil.choices))
    perfil_ativo = serializers.ChoiceField(choices=Perfil.choices, allow_null=True)


class TrocaDePerfilSerializer(serializers.Serializer):
    perfil = serializers.ChoiceField(choices=Perfil.choices)
