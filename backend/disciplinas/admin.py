"""Painel administrativo: tela de importação de turmas por CSV (ACE-RF-06).

Só entra quem é da equipe do Farol e está com o perfil de administrador. A importação é enviada
pelo formulário, processada em segundo plano (Celery) e o relatório aparece na própria página.
"""

from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from contas.servicos import Perfil

from . import servicos
from .leitura_csv import COLUNAS, LIMITE_DE_BYTES
from .models import Importacao


class EnvioDeImportacaoForm(forms.ModelForm):
    class Meta:
        model = Importacao
        fields = ["arquivo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "arquivo" in self.fields:  # na página do relatório, o arquivo é só leitura
            self.fields["arquivo"].help_text = (
                "CSV em UTF-8, separado por vírgula, de até 5 MB, com uma linha por aluno e "
                f"disciplina. Colunas: {','.join(COLUNAS)}"
            )

    def clean_arquivo(self):
        arquivo = self.cleaned_data["arquivo"]
        if not arquivo.name.lower().endswith(".csv"):
            raise forms.ValidationError("Envie um arquivo CSV (.csv).")
        if arquivo.size > LIMITE_DE_BYTES:
            raise forms.ValidationError("O arquivo passa de 5 MB.")
        return arquivo


def _e_administrador(request) -> bool:
    return Perfil.ADMIN in getattr(request.user, "perfis", [])


@admin.register(Importacao)
class ImportacaoAdmin(admin.ModelAdmin):
    form = EnvioDeImportacaoForm
    list_display = (
        "id",
        "enviada_em",
        "enviada_por",
        "status",
        "aceitas",
        "total_rejeitadas",
        "matriculas_encerradas",
    )
    list_filter = ("status",)
    readonly_fields = (
        "enviada_por",
        "enviada_em",
        "status",
        "aceitas",
        "matriculas_encerradas",
        "aviso",
        "erro",
        "linhas_rejeitadas",
    )

    @admin.display(description="Linhas rejeitadas")
    def total_rejeitadas(self, importacao: Importacao) -> int:
        return len(importacao.rejeitadas)

    @admin.display(description="Linhas rejeitadas")
    def linhas_rejeitadas(self, importacao: Importacao):
        if not importacao.rejeitadas:
            return "Nenhuma."
        itens = format_html_join(
            "",
            "<li><strong>Linha {}:</strong> {}</li>",
            ((r["linha"], r["motivo"]) for r in importacao.rejeitadas),
        )
        return format_html("<ul>{}</ul>", itens)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ["arquivo"]
        return [
            "status",
            "aceitas",
            "linhas_rejeitadas",
            "matriculas_encerradas",
            "aviso",
            "erro",
            "enviada_por",
            "enviada_em",
            "arquivo",
        ]

    # Permissões: só o administrador envia e consulta; o histórico não se edita nem se apaga.
    def has_module_permission(self, request) -> bool:
        return _e_administrador(request)

    def has_view_permission(self, request, obj=None) -> bool:
        return _e_administrador(request)

    def has_add_permission(self, request) -> bool:
        return _e_administrador(request)

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def save_model(self, request, obj, form, change) -> None:
        obj.enviada_por = request.user
        super().save_model(request, obj, form, change)
        servicos.enfileirar_importacao(obj.pk)

    def response_add(self, request, obj, post_url_continue=None):
        self.message_user(
            request,
            "Arquivo recebido. O relatório aparece abaixo quando o processamento termina; "
            "recarregue a página se ele ainda estiver pendente.",
        )
        return HttpResponseRedirect(reverse("admin:disciplinas_importacao_change", args=[obj.pk]))
