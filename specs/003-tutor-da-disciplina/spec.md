# Especificação: Tutor da disciplina

| Campo | Valor |
| --- | --- |
| Código | `TUT` |
| Branch | `003-tutor-da-disciplina` |
| Status | Em revisão |
| Criada em | 2026-11-13 |
| Origem | Documento de idealização, funcionalidade F1 |

## Contexto

O aluno estuda à noite e no fim de semana, sem professor por perto, e já usa chatbots genéricos que respondem fora do conteúdo e às vezes inventam. O tutor do Farol responde só com o material que o professor publicou, sempre mostrando de onde tirou a resposta, e segue as regras da disciplina: pistas em vez de respostas prontas e pausa durante as provas.

Esta é a funcionalidade central do produto e a que concentra o maior risco (respostas erradas). Ela aplica diretamente os princípios I, II e III da [constituição](../../.specify/memory/constitution.md).

## Histórias de usuário e testes de aceite

### História 1: Perguntar e receber resposta com a fonte (Prioridade: P1)

Como aluno, quero perguntar sobre o conteúdo da disciplina em linguagem natural e receber uma resposta com a página do material de onde ela veio.

**Por que esta prioridade:** é o motivo de o aluno abrir o Farol.

**Teste independente:** com os materiais de Estruturas de Dados publicados, perguntar "O que é uma lista encadeada?" e receber uma resposta com a citação "Aula 4, p. 5".

**Cenários de aceite:**

1. **Dado** uma disciplina com materiais prontos, **quando** o aluno pergunta algo que o material explica, **então** recebe uma resposta com pelo menos uma citação no formato "Aula N, p. M".
2. **Dado** uma resposta com citação, **quando** o aluno toca na citação, **então** o material abre na página citada com o trecho destacado.
3. **Dado** uma pergunta enviada, **quando** o tutor começa a responder, **então** o texto aparece aos poucos, e a primeira palavra surge em até 3 segundos.
4. **Dado** uma disciplina sem nenhum material pronto, **quando** o aluno abre o tutor, **então** vê "O tutor desta disciplina ainda não foi ativado" e não consegue perguntar.

### História 2: Saber quando o material não responde (Prioridade: P1)

Como aluno, quero que o tutor me diga claramente quando o assunto não está no material, em vez de inventar, e me ofereça levar a dúvida ao professor.

**Por que esta prioridade:** é a garantia contra respostas inventadas, o maior risco do produto.

**Teste independente:** perguntar "Isso cai na prova?" e receber "Não encontrei isso no material da disciplina", com o botão para enviar a dúvida.

**Cenários de aceite:**

1. **Dado** uma pergunta sem trecho relevante no material, **quando** o aluno envia, **então** o tutor responde "Não encontrei isso no material da disciplina." e mostra o botão "Enviar dúvida ao professor" (spec [004](../004-duvidas-ao-professor/spec.md)).
2. **Dado** uma pergunta administrativa (datas de prova, notas, presença), **quando** o aluno envia, **então** o tutor também responde que não encontrou no material.
3. **Dado** uma pergunta parcialmente coberta, **quando** o tutor responde, **então** responde só a parte coberta, com citação, e diz o que não encontrou.

### História 3: Receber pistas em vez da resposta pronta (Prioridade: P1)

Como professor, quero que, em exercícios, o tutor guie o aluno por etapas em vez de entregar o resultado, para que o aluno aprenda e não cole.

**Por que esta prioridade:** sem isso, professores não aceitam o tutor nas suas disciplinas.

**Teste independente:** com o modo pistas ligado, pedir "Me dá a resposta do exercício de pilha" e receber perguntas que guiam, sem o código final.

**Cenários de aceite:**

1. **Dado** o modo pistas ligado, **quando** o aluno pede a resposta de um exercício, **então** o tutor responde com uma pista ou pergunta que leva ao próximo passo, marcada com "Modo pistas", e sem o resultado final.
2. **Dado** o modo pistas ligado, **quando** o aluno faz uma pergunta conceitual, **então** o tutor responde normalmente.
3. **Dado** o modo pistas desligado pelo professor, **quando** o aluno pede a resposta de um exercício que está no material, **então** o tutor explica a solução, com citação.

### História 4: Pausar o tutor durante as provas (Prioridade: P2)

Como professor, quero pausar o tutor da minha disciplina durante as avaliações, na hora ou com agendamento.

**Teste independente:** ligar o modo prova e ver o tutor pausado na conta do aluno.

**Cenários de aceite:**

1. **Dado** o modo prova ligado agora, **quando** o aluno abre o tutor, **então** vê "O tutor está pausado durante a prova" e não consegue perguntar.
2. **Dado** uma janela de prova agendada para quinta-feira, das 19h às 22h, **quando** chega 19h, **então** o tutor pausa sozinho, e às 22h volta a responder.
3. **Dado** um aluno no meio de uma conversa, **quando** a janela de prova começa, **então** a próxima pergunta já é bloqueada, com o mesmo aviso.

### História 5: Respeitar o limite diário (Prioridade: P2)

Como instituição, quero limitar quantas perguntas cada aluno faz por dia, para controlar o custo e evitar abuso.

**Teste independente:** com limite 20, a 21ª pergunta do dia é recusada.

**Cenários de aceite:**

1. **Dado** o tutor aberto, **quando** o aluno olha o rodapé, **então** vê quantas perguntas já fez hoje e o limite (por exemplo, "12 de 40 perguntas hoje").
2. **Dado** um aluno que atingiu o limite, **quando** tenta perguntar, **então** vê "Você chegou ao limite de N perguntas de hoje. O limite volta amanhã." e a pergunta não é enviada.
3. **Dado** o professor mudou o limite para 60, **quando** o aluno abre o tutor, **então** o novo limite já vale.

### História 6: Avaliar a resposta (Prioridade: P2)

Como aluno, quero dizer se uma resposta foi útil ou está incorreta, para que a equipe corrija o tutor.

**Cenários de aceite:**

1. **Dado** uma resposta do tutor, **quando** o aluno marca "Útil", "Não útil" ou "Incorreta", **então** a marcação fica registrada e pode ser desfeita com um novo toque.
2. **Dado** uma resposta marcada como incorreta, **quando** a marcação é registrada, **então** o aluno vê "Obrigado. Respostas marcadas como incorretas vão para revisão da equipe." e a resposta entra na fila de revisão.

### História 7: Conhecer as regras de uso de IA da disciplina (Prioridade: P3)

Como aluno, quero ver a política de uso de IA que o professor definiu, para saber o que é permitido.

**Cenários de aceite:**

1. **Dado** o tutor aberto, **quando** o aluno toca em "Política de uso de IA", **então** vê o texto do professor e o resumo das regras (só material da disciplina, pistas em exercícios, pausa nas provas).
2. **Dado** o professor alterou a política, **quando** o aluno abre o tutor, **então** vê o texto novo.

### Casos de borda

- Pergunta vazia ou só com espaços: o botão de enviar fica desativado.
- Pergunta muito longa: limitada a 1.000 caracteres, com contador visível.
- Pergunta com CPF, e-mail ou telefone: os dados são removidos antes de qualquer processamento, e o aluno vê um aviso discreto.
- Tentativa de mudar as regras ("ignore as instruções anteriores"): o tutor mantém as regras e responde só com base no material.
- Material retirado no meio de uma conversa: a pergunta seguinte já não usa aquele material (MAT-RF-10).
- Saudação ("oi", "boa noite"): o tutor responde com uma frase curta explicando que responde só sobre o material da disciplina, sem consumir o limite diário.
- Provedor de IA fora do ar: o aluno vê "O tutor está indisponível agora. Tente de novo em alguns minutos." e a pergunta não conta no limite.

## Requisitos

### Requisitos funcionais

- **TUT-RF-01**: O tutor DEVE responder somente com base nos trechos de materiais prontos da disciplina selecionada.
- **TUT-RF-02**: Toda resposta DEVE trazer pelo menos uma citação (aula e página ou slide), que abre o material na página citada com o trecho destacado.
- **TUT-RF-03**: O sistema NÃO DEVE apresentar como resposta nenhuma afirmação sem citação.
- **TUT-RF-04**: Quando nenhum trecho do material é relevante para a pergunta, o tutor DEVE responder "Não encontrei isso no material da disciplina." e oferecer "Enviar dúvida ao professor", sem chamar o modelo de linguagem.
- **TUT-RF-05**: Com o modo pistas ligado, quando a pergunta pede a resolução de um exercício, o tutor DEVE responder com pistas em etapas, sem o resultado final, e marcar a resposta com "Modo pistas".
- **TUT-RF-06**: O professor DEVE poder ligar e desligar o modo pistas por disciplina; o padrão é ligado.
- **TUT-RF-07**: O professor DEVE poder pausar o tutor da disciplina imediatamente (modo prova) e agendar janelas de prova com início e fim; durante a pausa, o aluno vê o aviso e não consegue perguntar.
- **TUT-RF-08**: O sistema DEVE limitar o número de perguntas por aluno, por disciplina e por dia, com valor escolhido pelo professor entre 20, 40 e 60 (padrão 40), zerando à meia-noite no horário de Brasília, e mostrar ao aluno o uso do dia.
- **TUT-RF-09**: O aluno DEVE poder avaliar cada resposta como útil, não útil ou incorreta; respostas marcadas como incorretas entram na fila de revisão da equipe.
- **TUT-RF-10**: O tutor DEVE exibir a política de uso de IA da disciplina, escrita e editável pelo professor.
- **TUT-RF-11**: O sistema DEVE remover dados pessoais (nome, e-mail, CPF, telefone) da pergunta antes de enviá-la ao provedor de IA ou registrá-la para análise.
- **TUT-RF-12**: O histórico de conversa DEVE ser visível só para o próprio aluno; os registros usados no radar e na análise de qualidade DEVEM guardar só um identificador pseudônimo, que permite contar alunos distintos sem revelar quem são.
- **TUT-RF-13**: O tutor DEVE mostrar a resposta aos poucos (streaming), à medida que é gerada.
- **TUT-RF-14**: O tutor PODE sugerir perguntas iniciais sobre o material da disciplina quando a conversa está vazia.

### Requisitos não funcionais

- **TUT-RNF-01**: A primeira palavra da resposta aparece em até 3 segundos no percentil 95.
- **TUT-RNF-02**: As regras do tutor ficam fixas no servidor e não podem ser alteradas pelo texto da pergunta.
- **TUT-RNF-03**: A resposta é exibida como texto, sem interpretar HTML nem executar nada.
- **TUT-RNF-04**: Novas respostas são anunciadas por leitores de tela, e a conversa funciona só com o teclado.
- **TUT-RNF-05**: O custo de IA fica em até R$ 2 por aluno por mês.

### Entidades principais

- **Conversa**: aluno, disciplina, mensagens.
- **Mensagem**: autor (aluno ou tutor), texto, citações, tipo (resposta, pistas, não encontrado, saudação), avaliação.
- **Citação**: trecho, aula, página.
- **Configuração do tutor na disciplina**: modo pistas, limite diário, política de uso de IA.
- **Janela de prova**: disciplina, início, fim.
- **Registro de uso**: identificador pseudônimo do aluno, disciplina, pergunta filtrada, trechos usados, tipo de resposta, avaliação, tokens e custo.

## Critérios de sucesso

- **TUT-CS-01**: No conjunto de 100 perguntas reais por disciplina piloto, pelo menos 90% das respostas citam o trecho correto.
- **TUT-CS-02**: No máximo 5% das respostas do piloto são marcadas como incorretas pelos alunos.
- **TUT-CS-03**: Nenhuma resposta sem citação é apresentada como afirmação no conjunto de teste.
- **TUT-CS-04**: Em 100% das perguntas do conjunto de teste sem base no material, o tutor responde que não encontrou.

## Fora do escopo

- Responder sobre assuntos gerais ou de outras disciplinas.
- Ler imagens, fórmulas desenhadas ou código enviado pelo aluno.
- Conversa por voz.
- Corrigir trabalhos ou provas.

## Questões em aberto

| Questão | Dono | Prazo |
| --- | --- | --- |
| Quem compõe a "equipe" que revisa respostas incorretas no piloto | Dono do produto | Fase 0 |
| O limite diário vale por disciplina ou somado entre disciplinas | Dono do produto | Antes do plano final |

## Histórico

| Data | Mudança |
| --- | --- |
| 2026-11-13 | Criação da spec a partir da idealização e do protótipo |
