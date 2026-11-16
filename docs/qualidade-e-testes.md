# Qualidade e testes

Este documento diz como o Farol é testado e o que precisa estar verdadeiro para uma tarefa ser considerada pronta. Ele aplica o princípio VIII da [constituição](../.specify/memory/constitution.md): todo requisito tem um teste, e todo teste diz qual requisito verifica.

## Níveis de teste

| Nível | O que verifica | Ferramenta | Onde fica | Quando roda |
| --- | --- | --- | --- | --- |
| Unidade | Funções e serviços isolados: SM-2, filtro de dados pessoais, pontuação do radar, regras de permissão | pytest | `backend/<modulo>/testes/test_servicos*.py` | Todo pull request |
| API e integração | Rotas com banco real (PostgreSQL com pgvector em Docker), permissões e formato das respostas | pytest-django e o cliente de testes do Django REST Framework | `backend/<modulo>/testes/test_api*.py` | Todo pull request |
| Aceite | Cada cenário Dado / Quando / Então das specs | pytest, com o marcador do requisito | Junto aos testes de API | Todo pull request |
| Front-end | Telas e componentes, incluindo acessibilidade | Vitest, Testing Library e axe | `frontend/src/**/*.test.tsx` | Todo pull request |
| Ponta a ponta | Jornadas completas no navegador (entrar, perguntar, citar) | Playwright | `e2e/` | A partir da segunda funcionalidade pronta |
| Avaliação do tutor | As 100 perguntas por disciplina piloto (TUT-CS-01) | Script próprio | `backend/tutor/avaliacao/` | Mudança de prompt ou de modelo |

## Regras

1. **Teste antes do código, no mesmo commit.** Dentro de cada tarefa, escreva o teste, veja falhar e só então implemente. Teste e implementação vão juntos no commit da tarefa, para o branch nunca ficar com o CI vermelho.
2. **Todo teste de aceite cita o requisito** com o marcador `requisito`:

   ```python
   @pytest.mark.requisito("ACE-RF-04")
   def test_aluno_ve_so_as_disciplinas_em_que_esta_matriculado(cliente_aluno, disciplinas):
       ...
   ```

   O script `scripts/verificar_specs.py` passará a ler esses marcadores e a mostrar os testes de cada requisito na matriz de rastreabilidade (tarefa ACE-T18).
3. **A IA é sempre falsa nos testes.** Os testes usam o adaptador falso do módulo `ia`, que devolve respostas previsíveis. Nenhum teste acessa a internet nem gera custo.
4. **Banco de verdade.** Os testes de API rodam contra o PostgreSQL com pgvector do Docker, e não contra SQLite, para que a busca vetorial e as restrições do banco sejam testadas de fato.
5. **Dados fictícios.** Os dados de teste e de demonstração são inventados, como no protótipo. Nenhum dado real de aluno entra no repositório.
6. **Acessibilidade testada.** Toda tela nova tem pelo menos um teste com o axe sem violações (princípio V).

## Verificações estáticas

| O que | Ferramenta |
| --- | --- |
| Estilo e erros comuns em Python | Ruff (lint e formatação) |
| Fronteiras entre módulos ([ADR 0007](adr/0007-monolito-modular-em-camadas.md)) | import-linter |
| Migrações esquecidas | `manage.py makemigrations --check` |
| Contrato da API atualizado | Comparação do OpenAPI gerado com o arquivo versionado |
| Tipos e estilo no front-end | TypeScript em modo estrito, ESLint e Prettier |
| Specs e rastreabilidade | `scripts/verificar_specs.py` |

## Integração contínua

O GitHub Actions roda a cada push, em qualquer branch, e em todo pull request:

| Job | Passos |
| --- | --- |
| Specs | Verificação das specs, da rastreabilidade e dos links; sintaxe do protótipo |
| Back-end | Ruff, import-linter, verificação de migrações, pytest com PostgreSQL e Redis como serviços do job |
| Contrato | Gera o OpenAPI e confere se o arquivo versionado e os tipos do front-end estão atualizados |
| Front-end | ESLint, verificação de tipos, Vitest e build de produção |

Como cada tarefa é enviada assim que termina, o resultado aparece em minutos no branch da spec. Um pull request só pode ser mesclado com todos os jobs passando.

## Quando uma tarefa está pronta

- [ ] Os testes da tarefa existem, citam os requisitos e passam.
- [ ] Todos os outros testes continuam passando.
- [ ] O código respeita as camadas e as fronteiras entre módulos.
- [ ] A documentação foi atualizada junto: o OpenAPI é gerado sozinho, mas comandos novos vão para o guia de desenvolvimento e decisões novas viram ADR.
- [ ] A tarefa está marcada em `tasks.md`, e a matriz de rastreabilidade foi gerada de novo.
- [ ] A tarefa virou um único commit pequeno, já enviado para o branch da spec, com o GitHub Actions passando.
- [ ] Telas novas foram testadas no celular, com o teclado e nos temas claro e escuro.
