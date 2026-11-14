# Especificação: Questões e quizzes

| Campo | Valor |
| --- | --- |
| Código | `QUE` |
| Branch | `005-questoes-e-quizzes` |
| Status | Em revisão |
| Criada em | 2026-11-13 |
| Origem | Documento de idealização, funcionalidade F2 |

## Contexto

Ler e perguntar não basta: o aluno aprende mais quando pratica. Escrever questões, porém, toma tempo do professor. O Farol gera rascunhos de questões a partir do material de uma aula, e o professor só revisa. Nada chega ao aluno sem aprovação (princípio I da [constituição](../../.specify/memory/constitution.md)). As questões aprovadas formam o quiz da aula e alimentam a [revisão do dia](../006-revisao-do-dia/spec.md).

## Histórias de usuário e testes de aceite

### História 1: Gerar rascunhos a partir de uma aula (Prioridade: P1)

Como professor, quero pedir questões de uma aula e receber rascunhos prontos para revisar, em vez de escrever do zero.

**Por que esta prioridade:** é o que torna a prática viável sem sobrecarregar o professor.

**Teste independente:** pedir 10 questões da Aula 3 e receber 10 rascunhos com gabarito, justificativa e trecho de origem.

**Cenários de aceite:**

1. **Dado** uma aula com material pronto, **quando** o professor escolhe a aula e a quantidade (entre 5 e 20) e toca em "Gerar rascunhos", **então** vê um indicador de progresso e, ao terminar, os rascunhos na aba "Pendentes" com a marca "Novo rascunho".
2. **Dado** um rascunho, **quando** o professor o lê, **então** vê o enunciado, 4 alternativas com a correta destacada, a justificativa e a aula de origem.
3. **Dado** um rascunho gerado sem trecho de origem válido, **quando** a geração termina, **então** ele é descartado automaticamente e não aparece.

### História 2: Revisar e publicar (Prioridade: P1)

Como professor, quero aprovar, editar ou descartar cada rascunho, para publicar só o que eu assino embaixo.

**Por que esta prioridade:** é a garantia de qualidade e de controle do professor.

**Teste independente:** aprovar 1, editar 1 e descartar 1 rascunho e conferir o que o aluno vê.

**Cenários de aceite:**

1. **Dado** um rascunho pendente, **quando** o professor toca em "Aprovar", **então** a questão vai para "Publicadas" e passa a aparecer no quiz da aula para a turma.
2. **Dado** um rascunho pendente, **quando** o professor toca em "Editar", altera o enunciado, as alternativas, o gabarito ou a justificativa e salva, **então** as mudanças ficam no rascunho, que continua pendente até ser aprovado.
3. **Dado** um rascunho pendente, **quando** o professor toca em "Descartar", **então** ele vai para "Descartadas" e nunca aparece para o aluno.
4. **Dado** uma questão publicada, **quando** o professor toca em "Voltar para pendentes", **então** ela sai do quiz e da revisão do dia dos alunos.
5. **Dado** a tela de questões, **quando** o professor olha as abas, **então** vê a contagem de Pendentes, Publicadas e Descartadas.

### História 3: Fazer o quiz da aula (Prioridade: P1)

Como aluno, quero responder às questões de uma aula e saber na hora se acertei e por quê.

**Por que esta prioridade:** é o momento em que o aluno pratica de fato.

**Teste independente:** responder a um quiz de 3 questões, errando 1, e ver a justificativa, o link para o material e o resumo final.

**Cenários de aceite:**

1. **Dado** a página da disciplina, **quando** o aluno abre o quiz de uma aula, **então** vê uma questão por vez, com o progresso ("Questão 1 de 3").
2. **Dado** uma questão, **quando** o aluno escolhe uma alternativa, **então** vê se acertou, a alternativa correta, a justificativa e um link para o trecho do material.
3. **Dado** uma resposta errada, **quando** o retorno aparece, **então** há também o botão "Perguntar ao tutor sobre isso", que abre o tutor da disciplina com a questão como contexto.
4. **Dado** o fim do quiz, **quando** o aluno responde à última questão, **então** vê o número de acertos e os tópicos que vale revisar com o tutor.
5. **Dado** uma aula sem questões publicadas, **quando** o aluno abre a disciplina, **então** essa aula não oferece quiz.

### Casos de borda

- Geração demora ou falha: o professor vê "Não foi possível gerar agora" e pode tentar de novo; nenhum rascunho incompleto aparece.
- Material retirado (MAT-RF-10): as questões publicadas que vieram dele ficam marcadas "Origem retirada" para o professor decidir.
- Professor edita uma questão já publicada: [PRECISA ESCLARECER: a edição vale na hora para a turma, ou a questão volta para pendentes?]
- Aluno sai no meio do quiz: ao voltar, continua da questão em que parou.

## Requisitos

### Requisitos funcionais

- **QUE-RF-01**: O professor DEVE poder escolher uma aula com material pronto e pedir de 5 a 20 questões.
- **QUE-RF-02**: O sistema DEVE gerar, em segundo plano, rascunhos de múltipla escolha com 4 alternativas, 1 correta, justificativa e trecho de origem.
- **QUE-RF-03**: O sistema DEVE descartar automaticamente rascunhos sem trecho de origem válido ou fora do formato.
- **QUE-RF-04**: Rascunhos NÃO DEVEM ser visíveis para alunos em nenhuma tela ou rota.
- **QUE-RF-05**: O professor DEVE poder aprovar, editar ou descartar cada rascunho, e devolver uma questão publicada para pendentes.
- **QUE-RF-06**: A tela de questões DEVE separar Pendentes, Publicadas e Descartadas, com a contagem de cada uma.
- **QUE-RF-07**: Uma questão aprovada DEVE entrar no quiz da sua aula e ficar disponível para a revisão do dia (spec 006).
- **QUE-RF-08**: No quiz, o aluno DEVE receber retorno imediato com acerto ou erro, a alternativa correta, a justificativa e o link para o trecho de origem.
- **QUE-RF-09**: Ao errar, o aluno DEVE ver o botão "Perguntar ao tutor sobre isso", que abre o tutor da disciplina com a questão como contexto.
- **QUE-RF-10**: Ao final do quiz, o sistema DEVE mostrar o total de acertos e os tópicos a revisar.
- **QUE-RF-11**: O sistema DEVE registrar cada resposta com o identificador pseudônimo do aluno, para calcular a taxa de acerto por questão e por tópico no radar (spec 007).

### Requisitos não funcionais

- **QUE-RNF-01**: A geração de 10 rascunhos termina em até 1 minuto.
- **QUE-RNF-02**: O quiz funciona só com o teclado, e o retorno é anunciado por leitores de tela.

### Entidades principais

- **Questão**: aula, enunciado, alternativas, índice da correta, justificativa, trecho de origem, status (pendente, publicada, descartada), origem (gerada ou escrita pelo professor), editada (sim ou não).
- **Pedido de geração**: aula, quantidade, status, quem pediu.
- **Resposta**: questão, identificador pseudônimo do aluno, alternativa escolhida, acerto, data.

## Critérios de sucesso

- **QUE-CS-01**: O professor gera e revisa 10 questões em menos de 10 minutos.
- **QUE-CS-02**: Pelo menos 70% das questões geradas no piloto são aprovadas sem edição pesada (mudar o gabarito ou reescrever mais da metade do enunciado).
- **QUE-CS-03**: 100% das questões publicadas têm trecho de origem.

## Fora do escopo

- Questões discursivas, de associação ou de código.
- Quizzes valendo nota.
- Banco de questões compartilhado entre disciplinas.

## Questões em aberto

| Questão | Dono | Prazo |
| --- | --- | --- |
| Editar questão publicada vale na hora ou volta para pendentes | Professores do piloto | Fase 0 |
| O professor também pode escrever questões do zero | Professores do piloto | Fase 0 |

## Histórico

| Data | Mudança |
| --- | --- |
| 2026-11-13 | Criação da spec a partir da idealização e do protótipo |
