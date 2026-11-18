"""Mede quanto tempo um PDF de 40 páginas leva para ficar pronto (MAT-T90, MAT-RNF-01).

Uso: python manage.py medir_processamento [--paginas 40]
Roda com o provedor de IA configurado: em desenvolvimento, o falso; no servidor, o real. Cria uma
disciplina e um material fictícios e apaga tudo no fim.
"""

import time

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from contas import servicos as contas
from disciplinas import servicos as disciplinas
from materiais import servicos
from materiais.models import Material
from materiais.testes import pdfs

META_EM_SEGUNDOS = 120

PARAGRAFO = (
    "Uma lista encadeada guarda cada elemento num nó, com um ponteiro para o próximo nó. "
    "Inserir no início custa O(1), e buscar um elemento custa O(n) no pior caso. "
)


class _Desfazer(Exception):
    """Desfaz tudo o que a medição criou no banco."""


class Command(BaseCommand):
    help = "Mede o tempo de processamento de um PDF com texto (meta: 2 minutos para 40 páginas)."

    def add_arguments(self, parser):
        parser.add_argument("--paginas", type=int, default=40)

    def handle(self, *args, paginas: int, **opcoes):
        conteudo = pdfs.pdf_com_texto([PARAGRAFO * 6 for _ in range(paginas)])
        try:
            with transaction.atomic():
                professor, _ = contas.garantir_pessoa_com_perfil(
                    "medicao@exemplo.edu.br", contas.Perfil.PROFESSOR, nome="Medição"
                )
                disciplina, _ = disciplinas.garantir_disciplina(
                    "MEDICAO", "Medição", "MEDICAO", "0000/0", professor
                )
                material = Material(disciplina=disciplina, aula_numero=1, aula_titulo="Medição")
                material.arquivo.save("medicao.pdf", ContentFile(conteudo), save=False)
                material.save()
                inicio = time.perf_counter()
                material = servicos.processar_material(material.id)
                segundos = time.perf_counter() - inicio
                material.arquivo.delete(save=False)
                raise _Desfazer
        except _Desfazer:
            pass
        dentro = segundos <= META_EM_SEGUNDOS * paginas / 40
        self.stdout.write(
            f"{paginas} páginas: {segundos:.1f} s, status {material.status} "
            f"(meta: {META_EM_SEGUNDOS} s para 40 páginas) -> "
            + ("dentro da meta" if dentro else "ACIMA DA META")
        )
