from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from demonstracao import servicos


class Command(BaseCommand):
    help = (
        "Cria as pessoas, as disciplinas e as matrículas fictícias do protótipo "
        "(a aluna Ana Souza, o professor Carlos Mendes e as seis disciplinas do 2º período). "
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
                f"Dados de demonstração prontos: {relatorio.criados} criados, "
                f"{relatorio.existentes} já existiam."
            )
        )
