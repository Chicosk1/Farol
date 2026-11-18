"""Renderizador que deixa a rota de perguntas aceitar o pedido de eventos do navegador (TUT-T29)."""

import json

from rest_framework.renderers import BaseRenderer


class EventosDoTutor(BaseRenderer):
    """Aceita `Accept: text/event-stream` na negociação de conteúdo do DRF.

    A resposta boa é um StreamingHttpResponse, que não passa por renderizador. As recusas (400,
    403, 423, 429, 503) passam: o corpo vai em JSON, que o cliente lê do mesmo jeito.
    """

    media_type = "text/event-stream"
    format = "eventos"
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None) -> bytes:
        if data is None:
            return b""
        return json.dumps(data, ensure_ascii=False).encode("utf-8")
