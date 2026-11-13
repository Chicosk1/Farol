# 0001. Adotar desenvolvimento orientado por especificação, com a convenção do GitHub Spec Kit

- **Status:** Aceita
- **Data:** 13/11/2026

## Contexto

O projeto de extensão exige desenvolvimento orientado por especificação (Spec-Driven Development, SDD) e toda a documentação no GitHub. A equipe muda a cada semestre, parte do código pode ser escrita com assistentes de IA, e o professor orientador precisa conseguir avaliar o que foi pedido, o que foi decidido e o que foi entregue.

O protótipo navegável foi construído antes desta decisão, como exploração para visualizar as telas. Ele não seguiu o fluxo de especificação.

## Decisão

1. A especificação é o artefato principal. Nenhuma mudança de comportamento entra no código sem uma spec aprovada.
2. Seguimos a estrutura de pastas e o fluxo do [GitHub Spec Kit](https://github.com/github/spec-kit): constituição em `.specify/memory/constitution.md`, modelos em `.specify/templates/`, e uma pasta por funcionalidade em `specs/NNN-nome/` com `spec.md`, `plan.md` e `tasks.md`.
3. Os documentos são escritos em português. Os nomes de arquivo seguem o Spec Kit, para que a ferramenta `specify` e os assistentes de IA compatíveis funcionem sem ajustes.
4. Usar a ferramenta de linha de comando do Spec Kit é opcional: os modelos em português permitem seguir o mesmo fluxo à mão.
5. Para o protótipo já existente, fizemos o caminho inverso uma única vez: escrevemos as specs a partir do documento de idealização e do comportamento do protótipo, e marcamos em cada requisito o que o protótipo cobre. Daqui em diante, toda mudança no protótipo ou no produto começa pela spec.
6. Identificadores de requisito (por exemplo, `TUT-RF-03`) ligam spec, tarefas, código e testes. Uma verificação automática no GitHub Actions confere essa ligação em todo pull request.

## Alternativas consideradas

| Alternativa | Por que não |
| --- | --- |
| Documento de requisitos único (estilo IEEE 830) | Fica grande e desatualizado rápido; não separa o que é regra de negócio do que é decisão técnica |
| Wiki do GitHub | Não é versionada junto com o código, não passa por pull request e não pode ser verificada pela integração contínua |
| Kiro Specs | Formato parecido (requisitos, design e tarefas), mas ligado a um editor específico; o Spec Kit é aberto e mantido pelo próprio GitHub |
| Só issues e quadro de projeto | Bom para acompanhar trabalho, ruim para registrar o comportamento esperado do sistema |

## Consequências

- Mais escrita antes de codificar, compensada por menos retrabalho e por um histórico que qualquer pessoa nova entende.
- A spec vira o roteiro de testes: cada cenário Dado / Quando / Então vira um teste de aceite.
- O histórico do Git mostra o protótipo antes das specs. Este ADR registra o motivo.
- Issues e quadro do GitHub Projects continuam sendo usados, mas para acompanhar tarefas: cada tarefa de `tasks.md` pode virar uma issue.
