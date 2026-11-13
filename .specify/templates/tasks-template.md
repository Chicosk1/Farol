# Tarefas: [NOME DA FUNCIONALIDADE]

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | [AAAA-MM-DD] |

<!--
Formato de cada tarefa:
  - [ ] [XXX]-T01 [P] [H1] Descrição com o caminho do arquivo ([XXX]-RF-01, [XXX]-RF-02)
    [P]  = pode ser feita em paralelo com outras [P] do mesmo bloco (arquivos diferentes, sem dependência)
    [H1] = história de usuário da spec a que a tarefa pertence
    Entre parênteses, os requisitos que a tarefa atende. Todo requisito funcional precisa aparecer em pelo menos uma tarefa.
Numeração: T01 a T09 para o protótipo, T10 em diante para o produto, T90 em diante para o acabamento.
Marque [x] quando a tarefa estiver no branch principal. Uma tarefa grande pode virar uma issue no GitHub.
Testes vêm antes da implementação: escreva o teste, veja falhar, implemente.
-->

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [ ] [XXX]-T01 [H1] [...] em `js/screens/[arquivo].js` ([XXX]-RF-01)

### Pendências do protótipo

- [ ] [XXX]-T05 [H2] [...] ([XXX]-RF-02)

## Produto: fundação

- [ ] [XXX]-T10 Modelos e migrações

## Produto: História 1, [título] (P1)

- [ ] [XXX]-T20 [P] [H1] Testes de aceite dos cenários da História 1 ([XXX]-RF-01)
- [ ] [XXX]-T21 [H1] Implementação em `[caminho]` ([XXX]-RF-01)

## Produto: acabamento

- [ ] [XXX]-T90 Medição dos critérios de sucesso ([XXX]-CS-01)

## Dependências

[Quais specs, histórias ou tarefas precisam estar prontas antes.]
