"""Painel administrativo: fila de revisão das respostas marcadas como incorretas (TUT-RF-09).

Só o administrador (equipe do Farol) entra. A tela mostra a pergunta, já sem dados pessoais, a
resposta e as citações, sem nada que identifique o aluno.
"""

from django.contrib import admin
from django.utils.html import format_html, format_html_join

from contas.servicos import Perfil

from . import servicos
from .models import RegistroUso, RevisaoResposta


def _e_administrador(request) -> bool:
    return Perfil.ADMIN in getattr(request.user, "perfis", [])


@admin.register(RevisaoResposta)
class RevisaoRespostaAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "disciplina", "resumo_da_resposta", "respondida_em")
    list_filter = ("status",)
    fields = ("disciplina", "pergunta", "resposta", "citacoes", "status", "nota_da_equipe")
    readonly_fields = ("disciplina", "pergunta", "resposta", "citacoes")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("mensagem__conversa__disciplina")
            .order_by("status", "-mensagem__criada_em")
        )

    @admin.display(description="Disciplina")
    def disciplina(self, revisao: RevisaoResposta):
        return revisao.mensagem.conversa.disciplina

    @admin.display(description="Resposta")
    def resumo_da_resposta(self, revisao: RevisaoResposta) -> str:
        texto = revisao.mensagem.texto
        return texto if len(texto) <= 80 else texto[:79] + "…"

    @admin.display(description="Respondida em")
    def respondida_em(self, revisao: RevisaoResposta):
        return revisao.mensagem.criada_em

    @admin.display(description="Pergunta do aluno")
    def pergunta(self, revisao: RevisaoResposta) -> str:
        pergunta = servicos.pergunta_respondida(revisao.mensagem)
        return pergunta.texto if pergunta else "—"

    @admin.display(description="Resposta do tutor")
    def resposta(self, revisao: RevisaoResposta) -> str:
        return revisao.mensagem.texto

    @admin.display(description="Citações")
    def citacoes(self, revisao: RevisaoResposta):
        citacoes = list(revisao.mensagem.citacoes.select_related("trecho__material"))
        if not citacoes:
            return "Nenhuma."
        itens = format_html_join(
            "",
            "<li><strong>[{}] {}:</strong> {}</li>",
            ((c.ordem, c.rotulo, c.trecho.texto) for c in citacoes),
        )
        return format_html("<ul>{}</ul>", itens)

    # Permissões: só o administrador revisa; quem põe na fila são os alunos, não a equipe.
    def has_module_permission(self, request) -> bool:
        return _e_administrador(request)

    def has_view_permission(self, request, obj=None) -> bool:
        return _e_administrador(request)

    def has_change_permission(self, request, obj=None) -> bool:
        return _e_administrador(request)

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(RegistroUso)
class RegistroUsoAdmin(admin.ModelAdmin):
    """O uso do tutor, sem identificar alunos, e a tela de custo por aluno (TUT-RNF-05)."""

    list_display = ("criado_em", "disciplina", "tipo", "tokens_entrada", "tokens_saida", "custo")
    list_filter = ("tipo",)

    def get_urls(self):
        from django.urls import path

        return [
            path(
                "custos/",
                self.admin_site.admin_view(self.custos_view),
                name="tutor_registrouso_custos",
            ),
            *super().get_urls(),
        ]

    def custos_view(self, request):
        from datetime import date

        from django.conf import settings
        from django.core.exceptions import PermissionDenied
        from django.template.response import TemplateResponse
        from django.utils import timezone

        if not _e_administrador(request):
            raise PermissionDenied
        hoje = timezone.localdate()
        try:
            ano, mes = (int(parte) for parte in request.GET.get("mes", "").split("-"))
            referencia = date(ano, mes, 1)
        except ValueError:
            referencia = hoje.replace(day=1)
        contexto = {
            **self.admin_site.each_context(request),
            "title": f"Custo do tutor em {referencia:%m/%Y}",
            "custos": servicos.custos_do_mes(referencia.year, referencia.month),
            "orcamento": settings.FAROL_IA_ORCAMENTO_POR_ALUNO_MES,
            "mes": f"{referencia:%Y-%m}",
        }
        return TemplateResponse(request, "admin/tutor/custos.html", contexto)

    def has_module_permission(self, request) -> bool:
        return _e_administrador(request)

    def has_view_permission(self, request, obj=None) -> bool:
        return _e_administrador(request)

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
