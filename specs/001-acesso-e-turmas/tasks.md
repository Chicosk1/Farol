# Tarefas: Acesso e turmas

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-16 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] ACE-T01 [H1] Tela de entrada com escolha de perfil em `js/screens/entrar.js` (ACE-RF-01, ACE-RF-02)
- [x] ACE-T02 [H2] Lista de disciplinas com busca, abas, favoritos e grade ou lista em `js/screens/aluno-disciplinas.js` (ACE-RF-10)
- [x] ACE-T03 [H2] Disciplinas favoritas no topo da tela inicial em `js/screens/aluno-inicio.js` (ACE-RF-10)
- [x] ACE-T04 [H1] Troca de perfil na barra de demonstração em `js/shell.js` (ACE-RF-03)
- [x] ACE-T05 [H3] Botão de importação simulada de CSV em `js/screens/prof-disciplina.js` (ACE-RF-06)

### Pendências do protótipo

- [ ] ACE-T06 [H4] Aviso de privacidade na primeira entrada da aluna, com botão "Entendi", em `js/screens/aluno-inicio.js` (ACE-RF-08)

## Primeira fatia: arquitetura de pé

A primeira entrega do produto prova a arquitetura em todas as camadas com uma funcionalidade pequena: entrar (com o login de desenvolvimento) e ver as próprias disciplinas. Ela é formada pelas tarefas ACE-T10 a ACE-T18, ACE-T22, ACE-T24, ACE-T25 e ACE-T30 a ACE-T33, nesta ordem. O login institucional (ACE-T20 e ACE-T21) fica para quando o provedor for definido.

## Produto: fundação do repositório

- [ ] ACE-T10 Mover o protótipo para `prototipo/`, criar na raiz um `index.html` que redireciona para lá, atualizar os caminhos em README, specs, matriz e `scripts/verificar_specs.py`, e conferir o GitHub Pages
- [ ] ACE-T11 Criar o projeto Django 5.2 em `backend/`, com configurações por ambiente lidas de variáveis, o modelo `contas.Pessoa` como usuário desde a primeira migração e a rota `GET /api/saude`
- [ ] ACE-T12 [P] Criar o projeto React + TypeScript + Vite + Tailwind em `frontend/`, com os tokens do design system Farol, React Router, TanStack Query, Vitest, Testing Library e axe
- [ ] ACE-T13 [P] Criar `docker-compose.yml`, os Dockerfiles e o `.env.exemplo` com os serviços `db`, `redis`, `backend`, `worker`, `beat`, `frontend` e `mailpit`
- [ ] ACE-T14 Acrescentar ao GitHub Actions os jobs Back-end, Contrato e Front-end, com PostgreSQL com pgvector e Redis como serviços
- [ ] ACE-T15 [P] Gerar o OpenAPI com drf-spectacular, versionar o arquivo e gerar os tipos do front-end com openapi-typescript
- [ ] ACE-T16 [P] Configurar Ruff e os contratos do import-linter com as regras da ADR 0007
- [ ] ACE-T17 Escrever `docs/desenvolvimento.md`: pré-requisitos, como subir o ambiente, rodar os testes, criar migrações e popular os dados de demonstração
- [ ] ACE-T18 Marcador `requisito` no pytest e coluna "Testes" na matriz de rastreabilidade, lida por `scripts/verificar_specs.py`

## Produto: História 1, entrar com a conta institucional (P1)

- [ ] ACE-T20 [P] [H1] Testes de aceite dos cenários 1 a 3 em `backend/contas/testes/test_login.py` (ACE-RF-01, ACE-RF-02)
- [ ] ACE-T21 [H1] Login OpenID Connect com django-allauth, restrito ao domínio institucional (ACE-RF-01, ACE-RF-02)
- [ ] ACE-T22 [H1] Perfis da `Pessoa`, rotas `GET /api/eu`, `POST /api/eu/perfil-ativo` e `POST /api/sair` (ACE-RF-03)
- [ ] ACE-T23 [H1] Tela de entrada com o login institucional e troca de perfil no front-end (ACE-RF-01, ACE-RF-03)
- [ ] ACE-T24 [H1] Login de desenvolvimento: rota `POST /api/dev/entrar`, botões "Entrar como aluna" e "Entrar como professor" e teste de que a rota não existe com as configurações de produção (ACE-RNF-03)
- [ ] ACE-T25 [H2] Comando `popular_demo` com as pessoas, disciplinas e matrículas fictícias do protótipo (ACE-RF-04)

## Produto: História 2, ver só as minhas disciplinas (P1)

- [ ] ACE-T30 [P] [H2] Testes de aceite dos cenários 1 a 5 e testes de permissão em `backend/disciplinas/testes/` (ACE-RF-04, ACE-RF-05, ACE-RF-10)
- [ ] ACE-T31 [H2] Modelos `Disciplina`, `Matricula` e `Favorito`, serviços e rotas `GET /api/disciplinas` e `PUT`/`DELETE /api/disciplinas/{id}/favorito` (ACE-RF-04, ACE-RF-10)
- [ ] ACE-T32 [H2] Permissão por disciplina reutilizável, em `backend/nucleo/` (ACE-RF-05)
- [ ] ACE-T33 [H2] Tela de disciplinas com busca, abas Todas e Favoritas, favoritos e grade ou lista, com testes de acessibilidade (ACE-RF-10)
- [ ] ACE-T34 [H2] Ligar a aba "Com tutor" ao serviço de materiais, depois da História 1 da spec 002 (ACE-RF-10)

## Produto: História 3, importar turmas (P2)

- [ ] ACE-T40 [P] [H3] Testes com CSVs de exemplo válidos e inválidos em `backend/disciplinas/testes/test_importacao.py` (ACE-RF-06, ACE-RF-07)
- [ ] ACE-T41 [H3] Importação assíncrona idempotente com relatório (ACE-RF-06, ACE-RF-07)
- [ ] ACE-T42 [H3] Tela de importação no painel administrativo do Django (ACE-RF-06)

## Produto: História 4, saber o que é registrado (P2)

- [ ] ACE-T50 [P] [H4] Testes do aviso versionado e da exclusão de histórico (ACE-RF-08, ACE-RF-09)
- [ ] ACE-T51 [H4] Aviso de privacidade versionado e registro da ciência (ACE-RF-08)
- [ ] ACE-T52 [H4] Tela "Meus dados" com exclusão do histórico (ACE-RF-09)

## Produto: História 5, usar como app (P3)

- [ ] ACE-T60 [H5] Manifesto e service worker com vite-plugin-pwa (ACE-RF-11)

## Produto: acabamento

- [ ] ACE-T90 Auditoria de acessibilidade das telas desta spec (ACE-RNF-01)
- [ ] ACE-T91 Configurar HTTPS e expiração de sessão (ACE-RNF-02)

## Dependências

A fundação (ACE-T10 a ACE-T18) vem antes de tudo. O login de desenvolvimento (ACE-T24) permite fazer a História 2 antes do login institucional (ACE-T20 e ACE-T21). Todas as outras specs dependem das Histórias 1 e 2.
