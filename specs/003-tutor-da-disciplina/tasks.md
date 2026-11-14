# Tarefas: Tutor da disciplina

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-13 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] TUT-T01 [H1] Tela do tutor com conversa, efeito de digitação e sugestões em `js/screens/aluno-tutor.js` (TUT-RF-13, TUT-RF-14)
- [x] TUT-T02 [H1] Tutor simulado por palavras-chave com base de respostas citadas em `js/tutor.js` e `js/data.js` (TUT-RF-01, TUT-RF-02, TUT-RF-03)
- [x] TUT-T03 [H2] Resposta "Não encontrei" para perguntas fora da base em `js/tutor.js` (TUT-RF-04)
- [x] TUT-T04 [H3] Respostas em modo pistas e chave no painel do professor em `js/tutor.js` e `js/screens/prof-disciplina.js` (TUT-RF-05, TUT-RF-06)
- [x] TUT-T05 [H4] Modo prova imediato, com tutor pausado para a aluna, em `js/screens/prof-disciplina.js` e `js/screens/aluno-tutor.js` (TUT-RF-07)
- [x] TUT-T06 [H5] Limite diário configurável, contador e bloqueio em `js/screens/aluno-tutor.js` (TUT-RF-08)
- [x] TUT-T08 [H7] Política de uso de IA editável e exibida no tutor (TUT-RF-10)
- [x] TUT-T09 [H1] Histórico de conversa salvo só no navegador em `js/store.js` (TUT-RF-12)

### Pendências do protótipo

- [ ] TUT-T07 [H6] Acrescentar a avaliação "Não útil" ao lado de "Útil" e "Incorreta" em `js/screens/aluno-tutor.js` (TUT-RF-09)

## Produto: fundação

- [ ] TUT-T10 Módulo `backend/ia/` com `gerar_embedding` e `responder`, e um provedor falso para testes
- [ ] TUT-T11 [P] Modelos `Conversa`, `Mensagem`, `Citacao`, `ConfiguracaoTutor`, `JanelaProva`, `RegistroUso` e `RevisaoResposta`
- [ ] TUT-T12 [P] Montar o conjunto de 100 perguntas de Estruturas de Dados com resposta e trecho esperados em `backend/tutor/avaliacao/`
- [ ] TUT-T13 Script de avaliação que roda o conjunto e calcula a taxa de citação correta, ligado ao GitHub Actions (TUT-CS-01, TUT-CS-03, TUT-CS-04)

## Produto: História 1, perguntar e receber resposta com a fonte (P1)

- [ ] TUT-T20 [P] [H1] Testes de aceite dos cenários 1 a 4 com o provedor falso (TUT-RF-01, TUT-RF-02, TUT-RF-03)
- [ ] TUT-T21 [H1] Busca dos 6 trechos mais próximos, filtrada por disciplina e por material pronto (TUT-RF-01)
- [ ] TUT-T22 [H1] Regras fixas do prompt e conversão das marcações de trecho em citações, descartando frases sem marcação (TUT-RF-02, TUT-RF-03, TUT-RNF-02)
- [ ] TUT-T23 [H1] Rota de perguntas com streaming por SSE (TUT-RF-13)
- [ ] TUT-T24 [H1] Tela do tutor no React com citações clicáveis e região `aria-live` (TUT-RF-02, TUT-RNF-03, TUT-RNF-04)
- [ ] TUT-T25 [H1] Sugestões de pergunta geradas a partir dos títulos das aulas (TUT-RF-14)

## Produto: História 2, saber quando o material não responde (P1)

- [ ] TUT-T30 [P] [H2] Testes com perguntas sem base, inclusive administrativas (TUT-RF-04, TUT-CS-04)
- [ ] TUT-T31 [H2] Limite de similaridade e resposta "não encontrei" sem chamar o modelo (TUT-RF-04)

## Produto: História 3, pistas em vez da resposta pronta (P1)

- [ ] TUT-T40 [P] [H3] Perguntas de exercício no conjunto de avaliação, com verificação de que o resultado final não aparece (TUT-RF-05)
- [ ] TUT-T41 [H3] Instruções de modo pistas nas regras fixas e marcação "Modo pistas" na resposta (TUT-RF-05)
- [ ] TUT-T42 [H3] Configuração do modo pistas por disciplina (TUT-RF-06)

## Produto: História 4, pausar o tutor durante as provas (P2)

- [ ] TUT-T50 [P] [H4] Testes de janela imediata, agendada e iniciada no meio da conversa (TUT-RF-07)
- [ ] TUT-T51 [H4] Janelas de prova e verificação antes de cada pergunta (TUT-RF-07)
- [ ] TUT-T52 [H4] Tela de agendamento no painel do professor (TUT-RF-07)

## Produto: História 5, respeitar o limite diário (P2)

- [ ] TUT-T60 [P] [H5] Testes do limite, da virada do dia e da mudança de limite (TUT-RF-08)
- [ ] TUT-T61 [H5] Contador diário no Redis e resposta 429 (TUT-RF-08)

## Produto: História 6, avaliar a resposta (P2)

- [ ] TUT-T70 [H6] Avaliação útil, não útil e incorreta, e fila de revisão no painel administrativo (TUT-RF-09)

## Produto: História 7, regras de uso de IA (P3)

- [ ] TUT-T80 [H7] Edição e exibição da política de uso de IA (TUT-RF-10)

## Produto: privacidade e acabamento

- [ ] TUT-T90 [P] Filtro de dados pessoais com testes de CPF, e-mail, telefone e nomes (TUT-RF-11)
- [ ] TUT-T91 [P] Registro de uso com identificador pseudônimo por disciplina (TUT-RF-12)
- [ ] TUT-T92 Teste de carga para a meta de 3 segundos (TUT-RNF-01)
- [ ] TUT-T93 Painel de custo por aluno e alerta de orçamento (TUT-RNF-05)

## Dependências

Depende das specs 001 (Histórias 1 e 2) e 002 (Histórias 1 e 2). A História 2 desta spec é pré-requisito da spec 004. O registro de uso (TUT-T91) é pré-requisito da spec 007.
