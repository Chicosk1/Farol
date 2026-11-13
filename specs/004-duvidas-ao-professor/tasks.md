# Tarefas: Dúvidas ao professor

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-13 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] DUV-T01 [H1] Botão "Enviar dúvida ao professor" e bloqueio de reenvio em `js/screens/aluno-tutor.js` (DUV-RF-01, DUV-RF-03, DUV-RF-04)
- [x] DUV-T02 [H2] Seção de dúvidas no radar com a marca "Nova" em `js/screens/prof-radar.js` (DUV-RF-05)
- [x] DUV-T03 [H2] Sino de notificações do professor em `js/shell.js` (DUV-RF-06)
- [x] DUV-T04 [H3] Ação "Respondida em aula" em `js/screens/prof-radar.js` (DUV-RF-07)

### Pendências do protótipo

- [ ] DUV-T05 [H1] Modal de pré-visualização antes do envio, com o aviso de anonimato, em `js/screens/aluno-tutor.js` (DUV-RF-02)

## Produto: História 1, enviar a dúvida (P1)

- [ ] DUV-T10 [P] [H1] Testes de pré-visualização, envio e reenvio bloqueado (DUV-RF-02, DUV-RF-04)
- [ ] DUV-T11 [H1] Modelos `Duvida` e `EnvioDuvida` e rotas de prévia e envio (DUV-RF-01, DUV-RF-02, DUV-RF-03, DUV-RF-04)
- [ ] DUV-T12 [H1] Modal de pré-visualização no tutor (DUV-RF-02)

## Produto: História 2, ver as dúvidas da turma (P1)

- [ ] DUV-T20 [P] [H2] Teste de que nenhuma rota do professor devolve dados do aluno (DUV-RF-03, DUV-RNF-01, DUV-CS-01)
- [ ] DUV-T21 [H2] Rota de listagem para o professor e marcação de vista (DUV-RF-05)
- [ ] DUV-T22 [H2] Notificação de nova dúvida (DUV-RF-06)

## Produto: Histórias 3 e 4, acompanhar a resposta (P2 e P3)

- [ ] DUV-T30 [H3] Marcar como respondida e ocultar dúvida ofensiva (DUV-RF-07)
- [ ] DUV-T31 [H4] Status da dúvida na conversa do aluno (DUV-RF-08)

## Produto: acabamento

- [ ] DUV-T90 Incluir as dúvidas abertas no resumo semanal, junto com a spec 007 (DUV-RF-09)

## Dependências

Depende da História 2 da spec 003 (resposta "não encontrei") e do filtro de dados pessoais (TUT-T90).
