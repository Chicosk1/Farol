from rest_framework import serializers


class SaudeSerializer(serializers.Serializer):
    status = serializers.CharField(help_text='Sempre "ok" quando a API está no ar.')
