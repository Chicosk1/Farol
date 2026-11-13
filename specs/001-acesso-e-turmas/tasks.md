# Tarefas: Acesso e turmas

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-13 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] ACE-T01 [H1] Tela de entrada com escolha de perfil em `js/screens/entrar.js` (ACE-RF-01, ACE-RF-02)
- [x] ACE-T02 [H2] Lista de disciplinas com busca, abas, favoritos e grade ou lista em `js/screens/aluno-disciplinas.js` (ACE-RF-10)
- [x] ACE-T03 [H2] Disciplinas favoritas no topo da tela inicial em `js/screens/aluno-inicio.js` (ACE-RF-10)
- [x] ACE-T04 [H1] Troca de perfil na barra de demonstração em `js/shell.js` (ACE-RF-03)
- [x] ACE-T05 [H3] Botão de importação simulada de CSV em `js/screens/prof-disciplina.js` (ACE-RF-06)

### Pendências do protótipo

- [ ] ACE-T06 [H4] Aviso de privacidade na primeira entrada da aluna, com botão "Entendi", em `js/screens/aluno-inicio.js` (ACE-RF-08)

## Produto: fundação do repositório

- [ ] ACE-T10 Mover o protótipo para `prototipo/` e ajustar o GitHub Pages e os links do README
- [ ] ACE-T11 Criar o projeto Django em `backend/` com configurações por variáveis de ambiente
- [ ] ACE-T12 [P] Criar o projeto React + Vite + TypeScript + Tailwind em `frontend/`, com os tokens do design system Farol
- [ ] ACE-T13 [P] Criar `docker-compose.yml` com Nginx, Django, PostgreSQL, Redis e Celery
- [ ] ACE-T14 Configurar o GitHub Actions para rodar pytest, Vitest e a verificação de specs em todo pull request

## Produto: História 1, entrar com a conta institucional (P1)

- [ ] ACE-T20 [P] [H1] Testes de aceite dos cenários 1 a 3 em `backend/contas/tests/test_login.py` (ACE-RF-01, ACE-RF-02)
- [ ] ACE-T21 [H1] Login OpenID Connect com django-allauth, restrito ao domínio institucional (ACE-RF-01, ACE-RF-02)
- [ ] ACE-T22 [H1] Modelo `Pessoa` com perfis e rota `GET /api/eu` (ACE-RF-03)
- [ ] ACE-T23 [H1] Tela de entrada e troca de perfil no front-end (ACE-RF-03)

## Produto: História 2, ver só as minhas disciplinas (P1)

- [ ] ACE-T30 [P] [H2] Testes de permissão para todas as rotas em `backend/disciplinas/tests/test_permissoes.py` (ACE-RF-04, ACE-RF-05)
- [ ] ACE-T31 [H2] Modelos `Disciplina`, `Matricula` e `Favorito` e rota `GET /api/disciplinas` (ACE-RF-04, ACE-RF-10)
- [ ] ACE-T32 [H2] Permissão por disciplina reutilizável no Django REST Framework (ACE-RF-05)
- [ ] ACE-T33 [H2] Tela de disciplinas com busca, abas e favoritos (ACE-RF-10)

## Produto: História 3, importar turmas (P2)

- [ ] ACE-T40 [P] [H3] Testes com CSVs de exemplo válidos e inválidos em `backend/disciplinas/tests/test_importacao.py` (ACE-RF-06, ACE-RF-07)
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

A fundação (ACE-T10 a ACE-T14) vem antes de tudo. A História 1 bloqueia as demais. Todas as outras specs dependem das Histórias 1 e 2.
