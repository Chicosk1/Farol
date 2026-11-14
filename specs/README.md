# Especificações

Cada pasta descreve uma funcionalidade do Farol em três arquivos, na convenção do [GitHub Spec Kit](https://github.com/github/spec-kit):

| Arquivo | Responde | Quem lê primeiro |
| --- | --- | --- |
| `spec.md` | O que a funcionalidade faz e por quê: histórias de usuário, cenários de aceite, requisitos e critérios de sucesso. Sem tecnologia. | Professor orientador, professores do piloto, dono do produto |
| `plan.md` | Como será construída: modelo de dados, rotas da API, verificação da constituição e o que o protótipo já cobre | Equipe técnica |
| `tasks.md` | Em que ordem: tarefas pequenas, com o requisito que cada uma atende, marcadas quando concluídas | Quem vai implementar |

As regras que valem para todas as funcionalidades estão na [constituição](../.specify/memory/constitution.md). O passo a passo para criar ou mudar uma spec está no [CONTRIBUTING.md](../CONTRIBUTING.md).

## Funcionalidades

| Nº | Funcionalidade | Código | Fase do MVP | Status |
| --- | --- | --- | --- | --- |
| [001](001-acesso-e-turmas/spec.md) | Acesso e turmas | `ACE` | 1 | Em revisão |
| [002](002-materiais-da-disciplina/spec.md) | Materiais da disciplina | `MAT` | 1 | Em revisão |
| [003](003-tutor-da-disciplina/spec.md) | Tutor da disciplina | `TUT` | 1 | Em revisão |
| [004](004-duvidas-ao-professor/spec.md) | Dúvidas ao professor | `DUV` | 1 | Em revisão |
| [005](005-questoes-e-quizzes/spec.md) | Questões e quizzes | `QUE` | 2 | Em revisão |
| [006](006-revisao-do-dia/spec.md) | Revisão do dia | `REV` | 2 | Em revisão |
| [007](007-radar-da-turma/spec.md) | Radar da turma | `RAD` | 2 | Em revisão |

O quanto o protótipo já cobre de cada spec está na [matriz de rastreabilidade](../docs/rastreabilidade.md).

## Identificadores

| Padrão | Exemplo | Onde aparece |
| --- | --- | --- |
| `XXX-RF-NN` requisito funcional | `TUT-RF-04` | spec, plano, tarefas, código e testes |
| `XXX-RNF-NN` requisito não funcional | `TUT-RNF-01` | spec, tarefas e testes |
| `XXX-CS-NN` critério de sucesso | `TUT-CS-01` | spec e tarefas de medição |
| `XXX-TNN` tarefa | `TUT-T07` | tarefas, issues, commits e pull requests |

Um identificador nunca é reaproveitado. Se um requisito deixa de valer, ele fica na spec riscado, com a data e o motivo.

## Status de uma spec

1. **Rascunho:** alguém está escrevendo.
2. **Em revisão:** pull request aberto, aguardando o professor orientador e o dono do produto.
3. **Aprovada:** pode virar plano e tarefas.
4. **Implementada no protótipo** ou **Implementada no produto:** todas as tarefas da etapa correspondente estão marcadas.
