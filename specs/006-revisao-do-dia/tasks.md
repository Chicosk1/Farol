# Tarefas: Revisão do dia

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-13 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] REV-T01 [H1] Sessão de revisão com 8 cartões fixos em `js/screens/aluno-pratica.js` e `js/data.js` (REV-RF-01, REV-RF-02, REV-RF-03)
- [x] REV-T02 [H1] Avaliação Difícil, Bom e Fácil com aviso de quando o cartão volta (REV-RF-04, REV-RF-05)
- [x] REV-T03 [H1] Cartão da revisão na tela inicial, com progresso e "Continuar", em `js/screens/aluno-inicio.js` (REV-RF-06)
- [x] REV-T04 [H3] Cartão de sequência dos últimos 7 dias em `js/screens/aluno-inicio.js` (REV-RF-07)
- [x] REV-T05 [H1] Resumo final com acertos, atalhos para o tutor e horário da próxima revisão (REV-RF-08, REV-RF-10)

### Pendências do protótipo

- [ ] REV-T06 [H1] Incluir na revisão do dia as questões aprovadas pelo professor na tela de Questões (REV-RF-01)

## Produto: fundação

- [ ] REV-T10 Modelos `Cartao`, `SessaoRevisao` e `PreferenciaLembrete`
- [ ] REV-T11 [P] Função `agendar(cartao, acerto, avaliacao)` com o SM-2 e testes de tabela (REV-RF-04)

## Produto: História 1, fazer a revisão do dia (P1)

- [ ] REV-T20 [P] [H1] Testes de montagem da sessão, resposta e retomada (REV-RF-01, REV-RF-02, REV-RF-03)
- [ ] REV-T21 [H1] Criação de cartões quando uma questão é publicada e remoção quando é despublicada (REV-RF-01)
- [ ] REV-T22 [H1] Tarefa `revisao.montar_sessoes` às 6h (REV-RF-02, REV-RF-08)
- [ ] REV-T23 [H1] Rotas da sessão e tela da revisão no React (REV-RF-03, REV-RF-05, REV-RF-10, REV-RNF-01)
- [ ] REV-T24 [H1] Cartão da revisão na tela inicial (REV-RF-06)

## Produto: História 2, cartões no momento certo (P2)

- [ ] REV-T30 [H2] Priorização dos cartões atrasados e difíceis na montagem da sessão (REV-RF-02, REV-RF-04)

## Produto: História 3, manter a sequência (P2)

- [ ] REV-T40 [H3] Rota e cartão da sequência de 7 dias (REV-RF-07)

## Produto: História 4, lembrete diário (P3)

- [ ] REV-T50 [H4] Preferência de lembrete e tarefa de envio por Web Push e e-mail (REV-RF-09)

## Produto: acabamento

- [ ] REV-T90 Medir a duração das sessões no mini-piloto (REV-CS-01, REV-CS-02)

## Dependências

Depende da História 2 da spec 005 (questões publicadas) e do registro de respostas (QUE-T41).
