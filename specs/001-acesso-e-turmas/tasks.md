# Tarefas: Acesso e turmas

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-16 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] ACE-T01 [H1] Tela de entrada com escolha de perfil em `prototipo/js/screens/entrar.js` (ACE-RF-01, ACE-RF-02)
- [x] ACE-T02 [H2] Lista de disciplinas com busca, abas, favoritos e grade ou lista em `prototipo/js/screens/aluno-disciplinas.js` (ACE-RF-10)
- [x] ACE-T03 [H2] Disciplinas favoritas no topo da tela inicial em `prototipo/js/screens/aluno-inicio.js` (ACE-RF-10)
- [x] ACE-T04 [H1] Troca de perfil na barra de demonstração em `prototipo/js/shell.js` (ACE-RF-03)
- [x] ACE-T05 [H3] Botão de importação simulada de CSV em `prototipo/js/screens/prof-disciplina.js` (ACE-RF-06)

### Pendências do protótipo

- [x] ACE-T06 [H4] Aviso de privacidade na primeira entrada da aluna, com botão "Entendi", em `prototipo/js/screens/aluno-inicio.js` (ACE-RF-08)

## Primeira fatia: arquitetura de pé

A primeira entrega do produto prova a arquitetura em todas as camadas com uma funcionalidade pequena: entrar (com o login de desenvolvimento) e ver as próprias disciplinas. Ela é formada pelas tarefas ACE-T10 a ACE-T19, ACE-T22, ACE-T24, ACE-T25, ACE-T26, ACE-T30, ACE-T27, ACE-T31 a ACE-T33, ACE-T35 e ACE-T36, nesta ordem. Cada tarefa leva os próprios testes, escritos antes do código, e vira um commit e um push. O login institucional com o Google (ACE-T20, ACE-T21 e ACE-T23) vem depois, quando o provedor foi definido.

## Produto: fundação do repositório

- [x] ACE-T10 Mover o protótipo para `prototipo/`, criar na raiz um `index.html` que redireciona para lá, atualizar os caminhos em README, specs, matriz e `scripts/verificar_specs.py`, e conferir o GitHub Pages
- [x] ACE-T11 Criar o projeto Django 5.2 em `backend/`, com configurações por ambiente lidas de variáveis, o modelo `contas.Pessoa` como usuário desde a primeira migração, a rota `GET /api/saude` e o `backend/Dockerfile`
- [x] ACE-T12 [P] Criar o projeto React + TypeScript + Vite em `frontend/`, com React Router, TanStack Query, Vitest, Testing Library, axe, ESLint, Prettier e o `frontend/Dockerfile`
- [x] ACE-T19 Configurar o Tailwind CSS com os tokens do design system Farol (temas claro e escuro) e a fonte Nunito Sans em `frontend/src/estilos/`
- [x] ACE-T13 Criar `docker-compose.yml`, o `.env.exemplo` e a configuração do Celery, com os serviços `db`, `redis`, `backend`, `worker`, `beat`, `frontend` e `mailpit`
- [x] ACE-T14 Acrescentar ao GitHub Actions os jobs Back-end (migrações e pytest) e Front-end (ESLint, tipos, Vitest e build), com PostgreSQL com pgvector e Redis como serviços
- [x] ACE-T15 [P] Gerar o OpenAPI com drf-spectacular, versionar o arquivo, gerar os tipos do front-end com openapi-typescript e acrescentar o job Contrato ao GitHub Actions
- [x] ACE-T16 [P] Configurar Ruff e os contratos do import-linter com as regras da ADR 0007 e acrescentar os dois ao job Back-end do GitHub Actions
- [x] ACE-T17 Escrever `docs/desenvolvimento.md`: pré-requisitos, como subir o ambiente, rodar os testes, criar migrações e popular os dados de demonstração
- [x] ACE-T18 Marcador `requisito` no pytest e coluna "Testes" na matriz de rastreabilidade, lida por `scripts/verificar_specs.py`

## Produto: História 1, entrar com a conta institucional (P1)

- [x] ACE-T20 [P] [H1] Testes de aceite dos cenários 1 a 3 em `backend/contas/testes/test_login.py`, entregues junto da ACE-T21 (ACE-RF-01, ACE-RF-02)
- [x] ACE-T21 [H1] Login OpenID Connect com django-allauth, restrito ao domínio institucional (ACE-RF-01, ACE-RF-02)
- [x] ACE-T22 [H1] Perfis da `Pessoa` e rotas `GET /api/eu`, `POST /api/eu/perfil-ativo` e `POST /api/sair`, com testes (ACE-RF-03)
- [x] ACE-T23 [H1] Tela de entrada com o login institucional e troca de perfil no front-end (ACE-RF-01, ACE-RF-03)
- [x] ACE-T24 [H1] Login de desenvolvimento no back-end: rota `POST /api/dev/entrar` e teste de que a rota não existe com as configurações de produção (ACE-RNF-03)
- [x] ACE-T25 [H2] Comando `popular_demo` com as pessoas fictícias do protótipo (Ana Souza e Carlos Mendes), com teste (ACE-RF-04)
- [x] ACE-T26 [H1] Cliente de sessão no front-end (`/api/eu`, entrar, sair, token CSRF) e tela de entrada com os botões "Entrar como aluna" e "Entrar como professor", só em desenvolvimento (ACE-RNF-03)
- [x] ACE-T27 [H2] Acrescentar ao `popular_demo` as seis disciplinas do 2º período e as matrículas, depois da ACE-T30, com teste (ACE-RF-04)

## Produto: História 2, ver só as minhas disciplinas (P1)

- [x] ACE-T30 [H2] Modelos `Disciplina` e `Matricula`, serviço de listagem com busca e rota `GET /api/disciplinas`, com testes dos cenários 1, 2 e 5 (ACE-RF-04, ACE-RF-10)
- [x] ACE-T31 [H2] Permissão por disciplina reutilizável em `backend/nucleo/`, com testes de acesso negado (ACE-RF-05)
- [x] ACE-T32 [H2] Favoritos: modelo `Favorito`, rotas `PUT` e `DELETE /api/disciplinas/{id}/favorito` e filtro Favoritas, com testes do cenário 3 (ACE-RF-10)
- [x] ACE-T33 [H2] Tela de disciplinas com lista, busca e alternância entre grade e lista, com testes de tela e de acessibilidade (ACE-RF-10)
- [x] ACE-T35 [H2] Abas Todas e Favoritas e botão de favoritar na tela de disciplinas, com testes (ACE-RF-10)
- [x] ACE-T36 [H2] Disciplinas favoritas no topo da tela inicial, com testes do cenário 3 (ACE-RF-10)
- [x] ACE-T34 [H2] Ligar a aba "Com tutor" ao serviço de materiais, depois da História 1 da spec 002, com testes do cenário 4 (ACE-RF-10)

## Produto: História 3, importar turmas (P2)

- [x] ACE-T40 [H3] Testes com CSVs de exemplo válidos e inválidos em `backend/disciplinas/testes/test_importacao.py`, entregues junto da ACE-T41 (ACE-RF-06, ACE-RF-07)
- [x] ACE-T41 [H3] Modelo `Importacao` e serviço de importação do CSV: validação sem importar nada pela metade, linhas aceitas e rejeitadas com o motivo, idempotência e encerramento das matrículas ausentes (ACE-RF-06, ACE-RF-07)
- [x] ACE-T43 [H3] Tarefa Celery de importação e rotas `POST /api/importacoes` e `GET /api/importacoes/{id}`, só para o perfil administrador (ACE-RF-06)
- [x] ACE-T42 [H3] Tela de importação no painel administrativo do Django, com o perfil administrador fictício no `popular_demo` (ACE-RF-06)

## Produto: História 4, saber o que é registrado (P2)

- [x] ACE-T50 [H4] Testes do aviso versionado, entregues junto da ACE-T51; os da exclusão de histórico vão com a ACE-T52 (ACE-RF-08, ACE-RF-09)
- [x] ACE-T51 [H4] Aviso de privacidade versionado no back-end: modelo `CienciaPrivacidade`, `GET /api/aviso-privacidade`, `POST /api/eu/ciencia-privacidade` e `precisa_ver_aviso` em `GET /api/eu` (ACE-RF-08)
- [x] ACE-T53 [H4] Tela do aviso de privacidade no front-end, que bloqueia o uso até o aluno confirmar que leu (ACE-RF-08)
- [x] ACE-T52 [H4] Tela "Meus dados" com exclusão do histórico, depois da spec 003, com os testes da exclusão (ACE-RF-09)

## Produto: História 5, usar como app (P3)

- [x] ACE-T60 [H5] Manifesto e service worker com vite-plugin-pwa (ACE-RF-11)

## Produto: acabamento

- [x] ACE-T90 Auditoria de acessibilidade das telas desta spec (ACE-RNF-01)
- [x] ACE-T91 Configurar HTTPS e expiração de sessão (ACE-RNF-02)

## Produto: telas iguais ao protótipo

As telas do produto passam a ter o mesmo visual e a mesma organização do protótipo navegável. O CSS de componentes do protótipo é reaproveitado no front-end, com as mesmas classes `fr-`.

- [x] ACE-T70 Design system do protótipo no React: CSS de componentes e de layout, ícones do Tabler e os componentes `Icone`, `Botao`, `Selo`, `Avatar`, `Progresso`, `Modal`, `EstadoVazio` e `Avisos` (ACE-RNF-01)
- [x] ACE-T71 Casca do protótipo: cabeçalho com a marca, o sino e o menu da conta (trocar de perfil e sair), menu lateral por perfil e barra inferior no celular (ACE-RF-03)
- [x] ACE-T72 Tela de entrada no formato do protótipo (ACE-RF-01)
- [x] ACE-T73 Rota `GET /api/disciplinas/{id}` e campo `tem_tutor` na lista de disciplinas, para os cartões e a página da disciplina (ACE-RF-04, ACE-RF-10)
- [x] ACE-T74 Disciplinas em cartões e em lista, com busca, abas e favoritas, como no protótipo (ACE-RF-10)
- [x] ACE-T75 Início do aluno no formato do protótipo: cartão do tutor, novidades e as disciplinas favoritas (ACE-RF-10)
- [ ] ACE-T76 Início do professor: as disciplinas que leciona, com os atalhos para materiais, dúvidas e configuração (ACE-RF-04)
- [ ] ACE-T77 Aviso de privacidade e Meus dados no formato do protótipo (ACE-RF-08, ACE-RF-09)

## Dependências

A fundação (ACE-T10 a ACE-T19) vem antes de tudo. Dentro dela, a ordem é ACE-T10, ACE-T11, ACE-T12, ACE-T19, ACE-T13 e depois ACE-T14 a ACE-T18. O login de desenvolvimento (ACE-T24) permite fazer a História 2 antes do login institucional (ACE-T20 e ACE-T21). Todas as outras specs dependem das Histórias 1 e 2.
