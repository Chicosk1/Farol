# Especificação: Revisão do dia

| Campo | Valor |
| --- | --- |
| Código | `REV` |
| Branch | `006-revisao-do-dia` |
| Status | Em revisão |
| Criada em | 2026-11-13 |
| Origem | Documento de idealização, funcionalidade F2 |

## Contexto

O aluno que trabalha tem pouco tempo e esquece o que viu na semana anterior. A revisão do dia é uma sessão curta, de cerca de 5 minutos, com questões já aprovadas pelos professores, reapresentadas em intervalos crescentes (repetição espaçada). Ela cabe no ônibus e cria o hábito de estudar um pouco todo dia.

## Histórias de usuário e testes de aceite

### História 1: Fazer a revisão do dia (Prioridade: P1)

Como aluno, quero uma sessão curta de revisão todo dia, com as questões certas para mim, para não esquecer o conteúdo.

**Por que esta prioridade:** é o núcleo da funcionalidade.

**Teste independente:** um aluno com questões publicadas em duas disciplinas faz uma sessão de até 10 cartões.

**Cenários de aceite:**

1. **Dado** um aluno com cartões vencidos, **quando** abre a tela inicial, **então** vê o cartão "Revisão do dia" com o número de cartões, as disciplinas e o tempo estimado, e o botão "Começar revisão".
2. **Dado** uma sessão iniciada, **quando** o aluno responde a um cartão, **então** vê se acertou, a justificativa e o link para o trecho do material.
3. **Dado** o retorno de um cartão, **quando** o aluno avalia como Difícil, Bom ou Fácil, **então** vê quando o cartão volta (por exemplo, "Este cartão volta em 3 dias.") e passa ao próximo.
4. **Dado** o último cartão avaliado, **quando** a sessão termina, **então** vê o número de acertos, os tópicos para perguntar ao tutor e quando a próxima revisão fica pronta.
5. **Dado** uma sessão interrompida, **quando** o aluno volta, **então** o botão diz "Continuar" e a sessão segue do cartão em que parou.

### História 2: Cartões no momento certo (Prioridade: P2)

Como aluno, quero que as questões em que tive dificuldade voltem antes e as fáceis demorem mais, para usar bem o pouco tempo que tenho.

**Teste independente:** um cartão avaliado como Difícil volta no dia seguinte; um avaliado como Fácil, vários dias depois.

**Cenários de aceite:**

1. **Dado** um cartão respondido errado, **quando** é agendado, **então** volta no dia seguinte, independente da avaliação.
2. **Dado** um cartão respondido certo e avaliado como Fácil várias vezes seguidas, **quando** é agendado, **então** o intervalo cresce a cada vez.
3. **Dado** mais de 10 cartões vencidos, **quando** a sessão é montada, **então** entram primeiro os mais atrasados e os que o aluno achou difíceis.

### História 3: Manter a sequência (Prioridade: P2)

Como aluno, quero ver em quantos dias da semana fiz a revisão, para manter o hábito.

**Cenários de aceite:**

1. **Dado** o cartão "Sequência" na tela inicial, **quando** o aluno o vê, **então** aparecem os últimos 7 dias, marcando os dias com revisão feita e o dia de hoje.
2. **Dado** a revisão de hoje concluída, **quando** o aluno volta à tela inicial, **então** o cartão diz que a revisão de hoje foi feita e convida a voltar amanhã.

### História 4: Lembrete diário (Prioridade: P3)

Como aluno, quero receber um lembrete no horário que eu escolher, se eu quiser.

**Cenários de aceite:**

1. **Dado** o lembrete desligado (padrão), **quando** o dia passa, **então** o aluno não recebe nada.
2. **Dado** o lembrete ligado para 7h, **quando** há cartões vencidos às 7h, **então** o aluno recebe uma notificação ou e-mail; se não há cartões, não recebe.

### Casos de borda

- Aluno sem nenhuma questão publicada nas suas disciplinas: o cartão da tela inicial explica que a revisão começa quando os professores publicarem questões.
- Questão despublicada pelo professor (QUE-RF-05): sai da agenda do aluno.
- Aluno faz a sessão duas vezes no mesmo dia: a segunda é opcional, com "Refazer revisão", e não altera a agenda.
- Revisão durante o modo prova: [PRECISA ESCLARECER: a revisão do dia e os quizzes ficam disponíveis quando o tutor da disciplina está pausado?]

## Requisitos

### Requisitos funcionais

- **REV-RF-01**: O sistema DEVE criar um cartão de revisão para cada questão publicada nas disciplinas do aluno.
- **REV-RF-02**: A sessão diária DEVE ter no máximo 10 cartões, priorizando os mais atrasados e os avaliados como difíceis.
- **REV-RF-03**: Depois de cada resposta, o sistema DEVE mostrar se o aluno acertou, a justificativa e o link para o trecho de origem.
- **REV-RF-04**: O aluno DEVE avaliar cada cartão como Difícil, Bom ou Fácil, e o próximo intervalo DEVE ser calculado pelo algoritmo SM-2; uma resposta errada faz o cartão voltar no dia seguinte.
- **REV-RF-05**: O sistema DEVE informar quando cada cartão volta.
- **REV-RF-06**: A tela inicial DEVE mostrar o cartão da revisão do dia com o número de cartões, as disciplinas, o tempo estimado e o progresso de uma sessão em andamento.
- **REV-RF-07**: A tela inicial DEVE mostrar a sequência de revisões dos últimos 7 dias.
- **REV-RF-08**: Uma nova sessão DEVE ficar disponível todo dia às 6h, horário de Brasília.
- **REV-RF-09**: O aluno PODE ligar um lembrete diário, por notificação ou e-mail, no horário que escolher; o padrão é desligado.
- **REV-RF-10**: Ao final da sessão, o sistema DEVE mostrar o número de acertos e atalhos para o tutor nos tópicos errados.

### Requisitos não funcionais

- **REV-RNF-01**: A sessão funciona bem no celular com uma mão: alternativas e botões de avaliação com área de toque de pelo menos 44 por 44 pixels.

### Entidades principais

- **Cartão**: aluno, questão, facilidade, intervalo atual, repetições, próxima data, última avaliação.
- **Sessão de revisão**: aluno, data, cartões, respostas, concluída (sim ou não).
- **Preferência de lembrete**: aluno, ligado, canal, horário.

## Critérios de sucesso

- **REV-CS-01**: 90% das sessões terminam em até 6 minutos.
- **REV-CS-02**: Meta inicial, a calibrar no mini-piloto: 80% das sessões iniciadas são concluídas.

## Fora do escopo

- Cartões criados pelo próprio aluno.
- Ranking ou competição entre alunos.

## Questões em aberto

| Questão | Dono | Prazo |
| --- | --- | --- |
| Revisão e quizzes durante o modo prova | Professores do piloto | Fase 0 |
| Canal do lembrete no iPhone (notificação de PWA exige instalar na tela inicial) | Equipe técnica | Antes do plano final |

## Histórico

| Data | Mudança |
| --- | --- |
| 2026-11-13 | Criação da spec a partir da idealização e do protótipo |
