"""Identificador pseudônimo do aluno por disciplina (TUT-RF-12, princípio IV da constituição).

Os registros usados no radar e na análise de qualidade guardam só este identificador, e nunca o
aluno. É um HMAC do id do aluno, com um segredo do servidor somado ao id da disciplina:
- o mesmo aluno tem o mesmo identificador numa disciplina, então dá para contar alunos distintos;
- em outra disciplina, o mesmo aluno tem outro identificador, então não dá para cruzar disciplinas;
- sem o segredo, que fica fora do banco, não há como descobrir o aluno a partir do identificador.
"""

import hashlib
import hmac

from django.conf import settings


def pseudonimo_do_aluno(aluno_id: int, disciplina_id: int) -> str:
    chave = f"{settings.FAROL_SEGREDO_DO_PSEUDONIMO}:{disciplina_id}".encode()
    return hmac.new(chave, str(aluno_id).encode(), hashlib.sha256).hexdigest()
