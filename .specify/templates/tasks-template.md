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
Tamanho: cada tarefa cabe em um commit pequeno, revisável em poucos minutos (um assunto, de preferência uma camada).
Se ficar grande, divida antes de começar, com os números livres do mesmo bloco. Uma tarefa = um commit = um push.
Marque [x] quando a tarefa estiver no branch principal. Uma tarefa grande pode virar uma issue no GitHub.
Cada tarefa leva os próprios testes: escreva o teste, veja falhar, implemente, e faça um commit só com os dois.
-->

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [ ] [XXX]-T01 [H1] [...] em `js/screens/[arquivo].js` ([XXX]-RF-01)

### Pendências do protótipo

- [ ] [XXX]-T05 [H2] [...] ([XXX]-RF-02)

## Produto: fundação

- [ ] [XXX]-T10 Modelos e migrações

## Produto: História 1, [título] (P1)

- [ ] [XXX]-T20 [H1] [Parte pequena da História 1] em `[caminho]`, com testes do cenário 1 ([XXX]-RF-01)
- [ ] [XXX]-T21 [H1] [Próxima parte pequena], com testes do cenário 2 ([XXX]-RF-01)

## Produto: acabamento

- [ ] [XXX]-T90 Medição dos critérios de sucesso ([XXX]-CS-01)

## Dependências

[Quais specs, histórias ou tarefas precisam estar prontas antes.]
