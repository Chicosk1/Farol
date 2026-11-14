# Tarefas: Questões e quizzes

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-13 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] QUE-T01 [H1] Gerador de rascunhos com escolha de aula e quantidade em `js/screens/prof-questoes.js` (QUE-RF-01, QUE-RF-02)
- [x] QUE-T02 [H2] Aprovar, editar, descartar e voltar para pendentes, com abas e contagens, em `js/screens/prof-questoes.js` (QUE-RF-05, QUE-RF-06)
- [x] QUE-T03 [H2] Questão aprovada aparece no quiz da aula em `js/screens/aluno-disciplina.js` (QUE-RF-04, QUE-RF-07)
- [x] QUE-T04 [H3] Motor do quiz com retorno imediato, justificativa e link para o trecho em `js/screens/aluno-pratica.js` (QUE-RF-08)
- [x] QUE-T05 [H3] Resumo final com acertos e atalhos para o tutor em `js/screens/aluno-pratica.js` (QUE-RF-09, QUE-RF-10)
- [x] QUE-T06 [H1] Atalho "Gerar 5 questões de revisão" a partir do radar em `js/screens/prof-radar.js` (QUE-RF-01)

### Pendências do protótipo

- [ ] QUE-T07 [H3] Botão "Perguntar ao tutor sobre isso" no retorno de cada questão errada em `js/screens/aluno-pratica.js` (QUE-RF-09)

## Produto: fundação

- [ ] QUE-T10 Modelos `PedidoGeracao`, `Questao`, `RespostaQuiz` e `ProgressoQuiz`
- [ ] QUE-T11 [P] Esquema Pydantic da questão e provedor falso com respostas válidas e inválidas

## Produto: História 1, gerar rascunhos (P1)

- [ ] QUE-T20 [P] [H1] Testes de geração, validação e descarte automático (QUE-RF-02, QUE-RF-03)
- [ ] QUE-T21 [H1] Tarefa de geração no Celery com prompt fixo e validação do trecho (QUE-RF-02, QUE-RF-03)
- [ ] QUE-T22 [H1] Rota de pedido de geração e tela com progresso (QUE-RF-01)

## Produto: História 2, revisar e publicar (P1)

- [ ] QUE-T30 [P] [H2] Teste de que nenhuma rota do aluno devolve rascunhos (QUE-RF-04)
- [ ] QUE-T31 [H2] Edição, mudança de status e contagens (QUE-RF-05, QUE-RF-06)
- [ ] QUE-T32 [H2] Tela de revisão do professor no React (QUE-RF-05, QUE-RF-06)

## Produto: História 3, fazer o quiz (P1)

- [ ] QUE-T40 [P] [H3] Testes do quiz: gabarito escondido até a resposta, retorno e progresso (QUE-RF-08)
- [ ] QUE-T41 [H3] Rotas do quiz e registro de respostas com identificador pseudônimo (QUE-RF-07, QUE-RF-08, QUE-RF-11)
- [ ] QUE-T42 [H3] Tela do quiz com retorno, botão "Perguntar ao tutor sobre isso" e resumo final (QUE-RF-09, QUE-RF-10, QUE-RNF-02)

## Produto: acabamento

- [ ] QUE-T90 Medir o tempo de geração de 10 rascunhos (QUE-RNF-01)
- [ ] QUE-T91 Painel com a taxa de aprovação sem edição pesada (QUE-CS-02)

## Dependências

Depende das specs 001 e 002 (material pronto). A História 2 desta spec é pré-requisito da spec 006, e o registro de respostas (QUE-T41) é pré-requisito da taxa de acerto na spec 007.
