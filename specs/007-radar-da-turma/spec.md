# Especificação: Radar da turma

| Campo | Valor |
| --- | --- |
| Código | `RAD` |
| Branch | `007-radar-da-turma` |
| Status | Em revisão |
| Criada em | 2026-11-13 |
| Origem | Documento de idealização, funcionalidade F3 |

## Contexto

O professor só descobre o que a turma não entendeu quando corrige a prova, tarde demais para ajustar. O radar transforma as perguntas ao tutor, as dúvidas enviadas e os acertos nos quizzes num painel semanal que se lê em 5 minutos, com uma sugestão do que retomar na próxima aula. Tudo de forma agregada e anônima (princípio IV da [constituição](../../.specify/memory/constitution.md)): o professor vê padrões, nunca pessoas.

## Histórias de usuário e testes de aceite

### História 1: Ver os tópicos com mais dúvidas (Prioridade: P1)

Como professor, quero ver os tópicos em que a turma mais teve dúvidas na semana, com exemplos de perguntas, para saber o que não ficou claro.

**Por que esta prioridade:** é a informação que o professor não tem hoje.

**Teste independente:** com perguntas de 25 alunos sobre 6 assuntos, o radar mostra os 5 tópicos com mais alunos.

**Cenários de aceite:**

1. **Dado** perguntas ao tutor na semana, **quando** o professor abre o radar, **então** vê até 5 tópicos, ordenados pelo número de alunos distintos, cada um com uma barra proporcional e o número de alunos.
2. **Dado** um tópico, **quando** o professor toca nele, **então** vê 2 ou 3 perguntas de exemplo, sem dados pessoais, e o atalho "Ver o material da aula".
3. **Dado** um assunto perguntado por só 4 alunos diferentes, **quando** o radar é calculado, **então** esse assunto não aparece.

### História 2: Ver onde a turma erra (Prioridade: P1)

Como professor, quero ver a taxa de acerto por tópico e por questão nos quizzes, para saber se a turma entendeu de fato.

**Teste independente:** com respostas de 30 alunos, o radar mostra o acerto de cada tópico.

**Cenários de aceite:**

1. **Dado** respostas aos quizzes na semana, **quando** o professor abre o radar, **então** vê a taxa de acerto por tópico, do menor para o maior.
2. **Dado** uma questão respondida por menos de 5 alunos, **quando** o radar é calculado, **então** a taxa dessa questão não aparece.

### História 3: Saber o que retomar na próxima aula (Prioridade: P1)

Como professor, quero uma sugestão pronta dos tópicos a retomar, para abrir a próxima aula sem precisar analisar nada.

**Cenários de aceite:**

1. **Dado** o radar da semana, **quando** o professor o abre, **então** a primeira seção sugere 3 tópicos para retomar, escolhidos pela combinação de mais dúvidas e menor acerto.
2. **Dado** a sugestão, **quando** o professor toca em "Gerar 5 questões de revisão", **então** vai para a tela de questões com rascunhos gerados a partir das aulas desses tópicos (spec [005](../005-questoes-e-quizzes/spec.md)).

### História 4: Acompanhar os indicadores da semana (Prioridade: P2)

Como professor, quero ver de relance quantos alunos usaram o Farol e como foi a semana, e comparar com semanas anteriores.

**Cenários de aceite:**

1. **Dado** o radar, **quando** o professor o abre, **então** vê: alunos ativos (de quantos matriculados), perguntas ao tutor, acerto médio nos quizzes e dúvidas sem resposta.
2. **Dado** o seletor de semana, **quando** o professor escolhe uma semana anterior, **então** todo o radar mostra os dados daquela semana.

### História 5: Receber o resumo por e-mail (Prioridade: P2)

Como professor, quero receber o resumo do radar por e-mail toda segunda de manhã, para não precisar lembrar de abrir.

**Cenários de aceite:**

1. **Dado** o resumo semanal ligado na disciplina, **quando** chega segunda-feira, **então** o professor recebe até as 7h um e-mail com os tópicos sugeridos, os tópicos com mais dúvidas e as dúvidas sem resposta, e um link para o radar.
2. **Dado** o resumo desligado, **quando** chega segunda-feira, **então** nada é enviado.

### Casos de borda

- Semana com pouco uso (menos de 5 alunos ativos): o radar mostra só os indicadores e explica que não há dados suficientes para tópicos, sem nada que identifique alguém.
- Pergunta de exemplo com nome de colega ou do professor: removido pelo filtro de dados pessoais; se o filtro falhar, o professor pode ocultar o exemplo.
- Disciplina com dois professores: os dois veem o mesmo radar.
- Semana sem aula (feriado): o radar mostra a semana vazia, e o resumo por e-mail não é enviado.

## Requisitos

### Requisitos funcionais

- **RAD-RF-01**: O radar DEVE ser recalculado todo dia, de madrugada, com os dados da semana corrente.
- **RAD-RF-02**: O radar DEVE mostrar os indicadores da semana: alunos ativos e total de matriculados, perguntas ao tutor, acerto médio nos quizzes e dúvidas sem resposta.
- **RAD-RF-03**: O radar DEVE mostrar até 5 tópicos com mais alunos distintos na semana, cada um com 2 ou 3 perguntas de exemplo e o atalho para o material relacionado.
- **RAD-RF-04**: Um tópico SÓ DEVE aparecer se vier de pelo menos 5 alunos distintos.
- **RAD-RF-05**: As perguntas de exemplo DEVEM passar pela remoção de dados pessoais, e o professor DEVE poder ocultar um exemplo.
- **RAD-RF-06**: O radar NÃO DEVE exibir nome, RA, e-mail, horário exato ou qualquer contagem por aluno.
- **RAD-RF-07**: O radar DEVE mostrar a taxa de acerto por tópico e por questão, e só exibir taxas calculadas com pelo menos 5 alunos distintos.
- **RAD-RF-08**: O radar DEVE sugerir 3 tópicos para retomar na próxima aula, combinando mais dúvidas e menor acerto.
- **RAD-RF-09**: O professor DEVE poder escolher a semana exibida entre a atual e as anteriores do semestre.
- **RAD-RF-10**: Com o resumo semanal ligado, o professor DEVE receber toda segunda-feira, até as 7h, um e-mail com os tópicos sugeridos, os tópicos com mais dúvidas e as dúvidas sem resposta.
- **RAD-RF-11**: O radar DEVE oferecer o atalho "Gerar 5 questões de revisão" a partir dos tópicos sugeridos.

### Requisitos não funcionais

- **RAD-RNF-01**: O radar abre em até 2 segundos, porque é pré-calculado.
- **RAD-RNF-02**: O cálculo usa só registros com identificador pseudônimo (TUT-RF-12, QUE-RF-11).

### Entidades principais

- **Radar semanal**: disciplina, semana, indicadores, tópicos, taxas de acerto, sugestão, data do cálculo.
- **Tópico**: nome curto, número de alunos distintos, perguntas de exemplo, material relacionado.

## Critérios de sucesso

- **RAD-CS-01**: Em teste com os professores do piloto, pelo menos 4 dos 5 tópicos mostrados são reconhecidos como relevantes.
- **RAD-CS-02**: O e-mail semanal chega até as 7h de segunda-feira em todas as semanas do piloto.
- **RAD-CS-03**: 80% dos professores do piloto abrem o radar toda semana.
- **RAD-CS-04**: O professor lê o radar e decide o que retomar em até 5 minutos.

## Fora do escopo

- Painel da coordenação e do NDE, com vários cursos (expansão).
- Alerta de desengajamento de alunos individuais (expansão, só com consentimento).
- Qualquer visão por aluno.

## Questões em aberto

| Questão | Dono | Prazo |
| --- | --- | --- |
| A semana do radar vai de segunda a domingo ou acompanha o calendário de aulas | Professores do piloto | Fase 0 |

## Histórico

| Data | Mudança |
| --- | --- |
| 2026-11-13 | Criação da spec a partir da idealização e do protótipo |
