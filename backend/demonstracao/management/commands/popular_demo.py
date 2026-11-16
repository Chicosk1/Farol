from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from demonstracao import servicos


class Command(BaseCommand):
    help = (
        "Cria as pessoas fictícias do protótipo (Ana Souza e Carlos Mendes). "
        "Pode ser rodado várias vezes. Só funciona em desenvolvimento e em teste."
    )

    def handle(self, *args, **opcoes):
        if not settings.FAROL_LOGIN_DESENVOLVIMENTO:
            raise CommandError(
                "popular_demo só roda nas configurações de desenvolvimento e de teste: "
                "dados fictícios não entram em produção."
            )
        relatorio = servicos.popular()
        self.stdout.write(
            self.style.SUCCESS(
                f"Dados de demonstração prontos: {relatorio.criadas} criadas, "
                f"{relatorio.existentes} já existiam."
            )
        )
