# Especificação: Dúvidas ao professor

| Campo | Valor |
| --- | --- |
| Código | `DUV` |
| Branch | `004-duvidas-ao-professor` |
| Status | Em revisão |
| Criada em | 2026-11-13 |
| Origem | Documento de idealização, funcionalidades F1 e F3 |

## Contexto

Quando o material não responde uma pergunta, o tutor não inventa (spec [003](../003-tutor-da-disciplina/spec.md)). Para a dúvida não morrer ali, o aluno pode enviá-la ao professor, sem se identificar. Isso ataca diretamente a vergonha de perguntar em sala e dá ao professor um sinal concreto do que o material não cobre.

## Histórias de usuário e testes de aceite

### História 1: Enviar ao professor a dúvida que o tutor não respondeu (Prioridade: P1)

Como aluno, quero enviar ao professor, sem o meu nome, a dúvida que o tutor não encontrou no material.

**Por que esta prioridade:** fecha o ciclo da resposta "não encontrei" e é o que diferencia o Farol de um chatbot.

**Teste independente:** perguntar "Isso cai na prova?", enviar a dúvida e vê-la no radar do professor, sem nome.

**Cenários de aceite:**

1. **Dado** uma resposta "Não encontrei isso no material da disciplina.", **quando** o aluno toca em "Enviar dúvida ao professor", **então** vê o texto exato que será enviado, com os dados pessoais já removidos, e o aviso de que o professor não verá o nome dele.
2. **Dado** a pré-visualização, **quando** o aluno confirma, **então** vê "Dúvida enviada ao professor, sem o seu nome." e o botão da mensagem é trocado por essa mesma nota.
3. **Dado** uma dúvida já enviada a partir de uma mensagem, **quando** o aluno volta à conversa, **então** não consegue enviar a mesma dúvida de novo.

### História 2: Ver as dúvidas da turma (Prioridade: P1)

Como professor, quero ver as dúvidas que o material não respondeu, para tratar delas em aula.

**Por que esta prioridade:** sem esta tela, a dúvida enviada não chega a ninguém.

**Teste independente:** com 3 dúvidas enviadas, o professor vê as 3 no radar e o aviso no sino.

**Cenários de aceite:**

1. **Dado** dúvidas enviadas na disciplina, **quando** o professor abre o radar, **então** vê a seção "Dúvidas que o material não respondeu", da mais recente para a mais antiga, com o texto e há quanto tempo foi enviada.
2. **Dado** uma dúvida que o professor ainda não viu, **quando** ele abre o radar, **então** ela aparece com a marca "Nova".
3. **Dado** uma dúvida nova, **quando** o professor está em qualquer tela, **então** o sino de notificações mostra um ponto e lista a dúvida.
4. **Dado** qualquer dúvida, **quando** o professor a vê, **então** não há nome, RA, e-mail, turma ou horário exato que identifique o aluno.

### História 3: Marcar a dúvida como respondida em aula (Prioridade: P2)

Como professor, quero marcar uma dúvida como respondida em aula, para a lista mostrar só o que falta.

**Cenários de aceite:**

1. **Dado** uma dúvida aberta, **quando** o professor toca em "Respondida em aula", **então** ela sai da lista de abertas e aparece entre as respondidas, sem a marca "Nova".

### História 4: Saber que a minha dúvida foi respondida (Prioridade: P3)

Como aluno, quero saber quando o professor marcou a minha dúvida como respondida, para prestar atenção na aula ou rever a gravação.

**Cenários de aceite:**

1. **Dado** uma dúvida que o aluno enviou, **quando** o professor a marca como respondida em aula, **então** o aluno vê o novo status na conversa em que a dúvida nasceu, e o professor continua sem saber quem enviou.

### Casos de borda

- Turma muito pequena: mesmo sem nome, o estilo do texto pode identificar o aluno. O aviso da pré-visualização deixa isso claro.
- O aluno apaga o histórico (ACE-RF-09) depois de enviar: a dúvida continua para o professor, porque já não tem ligação com o aluno.
- Envio em massa: [PRECISA ESCLARECER: limitar o número de dúvidas por aluno por dia? Sugestão: 5]
- Texto ofensivo: o professor pode ocultar a dúvida; a ocultação fica registrada.

## Requisitos

### Requisitos funcionais

- **DUV-RF-01**: O sistema DEVE oferecer "Enviar dúvida ao professor" em toda resposta do tipo "não encontrei" do tutor.
- **DUV-RF-02**: Antes do envio, o sistema DEVE mostrar ao aluno o texto que será enviado, já sem dados pessoais, e pedir confirmação.
- **DUV-RF-03**: A dúvida DEVE chegar ao professor sem nome, RA, e-mail, turma ou horário exato do aluno.
- **DUV-RF-04**: O sistema DEVE impedir o envio repetido da mesma dúvida a partir da mesma mensagem.
- **DUV-RF-05**: O professor DEVE ver as dúvidas da disciplina no radar, da mais recente para a mais antiga, com a marca "Nova" nas que ainda não viu.
- **DUV-RF-06**: O sistema DEVE avisar o professor de novas dúvidas pelo sino de notificações.
- **DUV-RF-07**: O professor DEVE poder marcar uma dúvida como respondida em aula e ocultar dúvidas ofensivas.
- **DUV-RF-08**: O aluno DEVE ver o status da dúvida que enviou (aberta ou respondida em aula).
- **DUV-RF-09**: As dúvidas abertas da semana DEVEM entrar no resumo semanal por e-mail do professor (spec [007](../007-radar-da-turma/spec.md)).

### Requisitos não funcionais

- **DUV-RNF-01**: A ligação entre a dúvida e o aluno fica guardada só do lado do aluno (para DUV-RF-08) e nunca é exposta em rotas do professor.

### Entidades principais

- **Dúvida**: disciplina, texto filtrado, data (arredondada para o dia), status (aberta, respondida, oculta), vista pelo professor (sim ou não).
- **Envio de dúvida**: liga a mensagem do aluno à dúvida, visível só para o aluno.

## Critérios de sucesso

- **DUV-CS-01**: Em teste com os professores do piloto, nenhum consegue identificar o autor de uma dúvida pela tela do radar.
- **DUV-CS-02**: 80% das dúvidas enviadas no piloto são marcadas como respondidas em até 14 dias.

## Fora do escopo

- Resposta escrita do professor dentro do Farol (a resposta acontece em aula).
- Conversa privada entre aluno e professor.

## Questões em aberto

| Questão | Dono | Prazo |
| --- | --- | --- |
| Limite de dúvidas por aluno por dia | Dono do produto | Antes do plano final |
| O professor deve poder responder por escrito, além de "respondida em aula" | Professores do piloto | Fase 0 |

## Histórico

| Data | Mudança |
| --- | --- |
| 2026-11-13 | Criação da spec a partir da idealização e do protótipo |
