# Tarefas: Radar da turma

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-13 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] RAD-T01 [H4] Indicadores da semana e seletor de semana em `js/screens/prof-radar.js` (RAD-RF-01, RAD-RF-02, RAD-RF-09)
- [x] RAD-T02 [H1] Tópicos com mais dúvidas, exemplos e atalho para o material em `js/screens/prof-radar.js` (RAD-RF-03, RAD-RF-04, RAD-RF-06)
- [x] RAD-T03 [H2] Acerto nos quizzes por tópico em `js/screens/prof-radar.js` (RAD-RF-07)
- [x] RAD-T04 [H3] Sugestão para a próxima aula e atalho para gerar questões em `js/screens/prof-radar.js` (RAD-RF-08, RAD-RF-11)
- [x] RAD-T05 [H5] Chave do resumo semanal em `js/screens/prof-disciplina.js` (RAD-RF-10)

## Produto: fundação

- [ ] RAD-T10 Modelo `RadarSemanal` e `ExemploOculto`
- [ ] RAD-T11 [P] Gerador de registros sintéticos para testes, com grupos de 4, 5 e 20 alunos

## Produto: Histórias 1 e 2, tópicos e acertos (P1)

- [ ] RAD-T20 [P] [H1] Testes da regra dos 5 alunos para tópicos e taxas (RAD-RF-04, RAD-RF-07)
- [ ] RAD-T21 [H1] Tarefa `radar.calcular`: agrupamento, filtro de 5 alunos e nomes dos tópicos (RAD-RF-01, RAD-RF-03, RAD-RF-04)
- [ ] RAD-T22 [H1] Filtro de dados pessoais nos exemplos e ocultação pelo professor (RAD-RF-05)
- [ ] RAD-T23 [H2] Taxas de acerto por tópico e por questão a partir de `RespostaQuiz` (RAD-RF-07)
- [ ] RAD-T24 [H1] Teste de que a resposta da API não contém dado de aluno (RAD-RF-06)

## Produto: História 3, o que retomar (P1)

- [ ] RAD-T30 [H3] Pontuação e escolha dos 3 tópicos sugeridos (RAD-RF-08)
- [ ] RAD-T31 [H3] Atalho para gerar questões das aulas sugeridas (RAD-RF-11)

## Produto: História 4, indicadores e semanas (P2)

- [ ] RAD-T40 [H4] Indicadores, seletor de semana e tela do radar no React (RAD-RF-02, RAD-RF-09, RAD-RNF-01)

## Produto: História 5, resumo por e-mail (P2)

- [ ] RAD-T50 [H5] Tarefa `radar.enviar_resumos` e modelo do e-mail (RAD-RF-10)

## Produto: acabamento

- [ ] RAD-T90 Sessão de avaliação dos tópicos com os professores do piloto (RAD-CS-01)
- [ ] RAD-T91 Monitorar o horário de entrega dos e-mails (RAD-CS-02)

## Dependências

Depende do registro de uso da spec 003 (TUT-T91), do registro de respostas da spec 005 (QUE-T41) e das dúvidas da spec 004.
