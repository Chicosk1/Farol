# Plano técnico: Revisão do dia

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `006-revisao-do-dia` |
| Status | Em revisão |
| Atualizado em | 2026-11-13 |

## Resumo

Cada questão publicada gera um cartão por aluno matriculado. O agendamento usa o SM-2, implementado numa função pura e testável. Uma tarefa periódica do Celery, às 6h, monta a sessão do dia de cada aluno com até 10 cartões vencidos. As respostas da revisão reaproveitam o registro de respostas da spec 005, com o contexto "revisão".

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | Python 3.12, TypeScript 5 |
| Dependências principais | Celery beat para tarefas periódicas; e-mail transacional; Web Push para notificações |
| Armazenamento | PostgreSQL |
| Testes | pytest com casos de tabela para o SM-2 |

## Verificação da constituição

| Princípio | Atende? | Como |
| --- | --- | --- |
| I. O professor é o dono do conteúdo | Sim | Só questões publicadas viram cartões |
| II. Toda resposta mostra a fonte | Sim | Cada cartão leva ao trecho de origem |
| III. Ensinar, não entregar respostas | Sim | Justificativa e atalho para o tutor no erro |
| IV. Privacidade por padrão | Sim | Lembrete desligado por padrão; respostas pseudônimas para o radar |
| V. Acessível e pensado para o celular | Sim | Sessão curta, áreas de toque grandes (REV-RNF-01) |
| VI. Simplicidade e ferramentas populares | Sim | SM-2 em uma função de poucas linhas, sem biblioteca |
| VII. Especificação antes do código | Sim | |
| VIII. Qualidade verificável | Sim | Testes de tabela para todos os caminhos do SM-2 |

## Modelo de dados

| Entidade | Campos | Observações |
| --- | --- | --- |
| `Cartao` | `aluno`, `questao`, `facilidade` (inicia em 2,5), `intervalo_dias`, `repeticoes`, `proxima_data`, `ultima_avaliacao` | Único por `aluno` + `questao` |
| `SessaoRevisao` | `aluno`, `data`, `cartoes` (lista ordenada), `indice_atual`, `concluida` | Uma por aluno por dia |
| `PreferenciaLembrete` | `aluno`, `ligado`, `canal` (push, email), `horario` | |

Mapeamento da avaliação para a nota do SM-2: erro = 1 (reinicia o cartão), Difícil = 3, Bom = 4, Fácil = 5.

## Contratos

| Método e caminho | Entrada | Saída | Erros |
| --- | --- | --- | --- |
| `GET /api/revisao/hoje` | | Sessão do dia: cartões (sem gabarito), progresso, disciplinas, tempo estimado | |
| `POST /api/revisao/cartoes/{id}/resposta` | `{ alternativa }` | `{ acerto, correta, justificativa, citacao }` | 409 se já respondido na sessão |
| `POST /api/revisao/cartoes/{id}/avaliacao` | `{ avaliacao: dificil\|bom\|facil }` | `{ proxima_data, texto: "volta em 3 dias" }` | |
| `GET /api/revisao/sequencia` | | Últimos 7 dias com revisão feita | |
| `PUT /api/eu/lembrete` | `{ ligado, canal, horario }` | Preferência | |

Tarefas periódicas: `revisao.montar_sessoes` às 6h; `revisao.enviar_lembretes` a cada 15 minutos para quem tem lembrete naquele horário.

## Como o protótipo implementa

| Requisito | Cobertura | Como o protótipo faz |
| --- | --- | --- |
| REV-RF-01 | Simulado | A revisão usa um conjunto fixo de 8 cartões (`revisao` em `js/data.js`), não as questões aprovadas |
| REV-RF-02 | Simulado | 8 cartões fixos, abaixo do máximo de 10 |
| REV-RF-03 | Coberto | Mesmo motor do quiz em `js/screens/aluno-pratica.js` |
| REV-RF-04 | Parcial | Botões Difícil, Bom e Fácil com intervalos fixos (amanhã, 3 dias, 7 dias), sem SM-2 |
| REV-RF-05 | Coberto | Aviso "Este cartão volta em ..." |
| REV-RF-06 | Coberto | Cartão da revisão com progresso e "Continuar" em `js/screens/aluno-inicio.js` |
| REV-RF-07 | Coberto | Cartão de sequência com os últimos 7 dias em `js/screens/aluno-inicio.js` |
| REV-RF-08 | Simulado | Texto "A próxima revisão fica pronta amanhã às 6h" |
| REV-RF-09 | Não coberto | |
| REV-RF-10 | Coberto | Resumo final com acertos e atalhos para o tutor |

## Decisões e pesquisa

- **SM-2** em vez de algoritmos mais novos (como FSRS): é simples, conhecido e documentado, e suficiente para sessões de 10 cartões. Pode ser trocado depois sem mudar a spec, porque a spec exige só que os difíceis voltem antes.
- **Sessão montada às 6h** em vez de na hora: a tela inicial abre rápido e o número de cartões não muda ao longo do dia.

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| Web Push para o lembrete | Notificação no celular sem app nativo | Só e-mail tem pouca chance de ser visto no horário certo; o e-mail continua como opção |
