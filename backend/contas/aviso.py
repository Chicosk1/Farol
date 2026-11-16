"""Texto e versão do aviso de privacidade (ACE-RF-08, princípio IV da constituição).

Ao mudar o texto, mude também VERSAO_ATUAL: cada aluno vê o aviso novo uma vez e a ciência dele
é guardada por versão.
"""

VERSAO_ATUAL = "1"

TITULO = "Como o Farol cuida dos seus dados"

ITENS = [
    {
        "titulo": "O que é registrado",
        "texto": (
            "O seu nome, o seu e-mail institucional e as disciplinas em que você está matriculado. "
            "Quando você usa o tutor, as suas perguntas e as respostas ficam guardadas no seu "
            "histórico. Nada além disso é coletado."
        ),
    },
    {
        "titulo": "Para quê",
        "texto": (
            "Para mostrar a você só as suas disciplinas e permitir que o tutor responda com o "
            "material do professor. O professor vê os assuntos que mais geram dúvida na turma, "
            "mas não vê quem perguntou: os assuntos aparecem sem nome e só quando vêm de pelo "
            "menos 5 alunos diferentes."
        ),
    },
    {
        "titulo": "Por quanto tempo",
        "texto": (
            "As suas perguntas são guardadas por 12 meses e depois apagadas ou mantidas só de "
            "forma agregada, sem ligação com você."
        ),
    },
    {
        "titulo": "Os seus direitos",
        "texto": (
            "Você pode ver o seu histórico e apagar tudo quando quiser, na tela Meus dados. "
            "Dados pessoais, como nome, e-mail, CPF e telefone, são removidos das perguntas "
            "antes de qualquer envio ao provedor de IA."
        ),
    },
]
