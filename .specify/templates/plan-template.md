# Plano técnico: [NOME DA FUNCIONALIDADE]

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `[NNN-nome-curto]` |
| Status | Rascunho · Em revisão · Aprovado |
| Atualizado em | [AAAA-MM-DD] |

<!--
O plano descreve COMO a spec será implementada. Ele não acrescenta comportamento:
se surgir uma regra nova, ela volta para a spec primeiro.
Quando este arquivo crescer, separe o modelo de dados em data-model.md e os contratos em contracts/, como no Spec Kit.
-->

## Resumo

[Uma ou duas frases: a abordagem técnica escolhida para atender a spec.]

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | [ex.: TypeScript 5, Python 3.12] |
| Dependências principais | [ex.: React, Django REST Framework] |
| Armazenamento | [ex.: PostgreSQL 16 com pgvector] |
| Testes | [ex.: pytest, Vitest, Playwright] |
| Plataforma | [ex.: PWA em navegadores modernos, servidor Linux] |
| Metas de desempenho | [ex.: primeira palavra em até 3 s] |
| Restrições | [ex.: limite diário, dados no Brasil] |

## Verificação da constituição

<!-- Marque cada princípio. Se algum não for atendido, explique em "Complexidade justificada". -->

| Princípio | Atende? | Como |
| --- | --- | --- |
| I. O professor é o dono do conteúdo | [Sim/Não/N.A.] | [...] |
| II. Toda resposta mostra a fonte | [Sim/Não/N.A.] | [...] |
| III. Ensinar, não entregar respostas | [Sim/Não/N.A.] | [...] |
| IV. Privacidade por padrão | [Sim/Não/N.A.] | [...] |
| V. Acessível e pensado para o celular | [Sim/Não/N.A.] | [...] |
| VI. Simplicidade e ferramentas populares | [Sim/Não/N.A.] | [...] |
| VII. Especificação antes do código | [Sim/Não/N.A.] | [...] |
| VIII. Qualidade verificável | [Sim/Não/N.A.] | [...] |

## Modelo de dados

[Entidades, campos, tipos e relações.]

## Contratos

[Endpoints da API (método, caminho, entrada, saída, erros) ou eventos e tarefas assíncronas.]

## Como o protótipo implementa

[Arquivos do protótipo que simulam esta funcionalidade e o que é simulado. Use a coluna "Cobertura" com: Coberto, Simulado, Parcial ou Não coberto.]

## Decisões e pesquisa

[Alternativas avaliadas e por que a escolhida venceu. Decisões que afetam o projeto todo viram um ADR em docs/adr/.]

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| [nenhum] | | |
