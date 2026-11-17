"""Painel administrativo: fila de revisão das respostas marcadas como incorretas (TUT-RF-09).

Só o administrador (equipe do Farol) entra. A tela mostra a pergunta, já sem dados pessoais, a
resposta e as citações, sem nada que identifique o aluno.
"""

from django.contrib import admin
from django.utils.html import format_html, format_html_join

from contas.servicos import Perfil

from . import servicos
from .models import RevisaoResposta


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
