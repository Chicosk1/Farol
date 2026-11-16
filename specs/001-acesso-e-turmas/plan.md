# Plano técnico: Acesso e turmas

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `001-acesso-e-turmas` |
| Status | Em revisão |
| Atualizado em | 2026-11-16 |

## Resumo

Login por OpenID Connect com django-allauth, perfis guardados no banco, permissões verificadas por disciplina em cada rota da API, importação de CSV como tarefa assíncrona idempotente e front-end React instalável como PWA. Esta é a primeira spec do produto, então o plano também cria a fundação do repositório (Docker Compose, Django, React, testes e integração contínua), seguindo o monólito modular da [ADR 0007](../../docs/adr/0007-monolito-modular-em-camadas.md) e o ambiente em Docker da [ADR 0008](../../docs/adr/0008-ambiente-local-em-docker.md).

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | Python 3.13, TypeScript 5, Node.js 24 LTS (só dentro do container do front-end) |
| Dependências principais | Django 5.2 LTS, Django REST Framework, django-allauth, drf-spectacular, Celery; React, Vite, Tailwind CSS, React Router, TanStack Query, vite-plugin-pwa |
| Armazenamento | PostgreSQL 16 com pgvector e Redis 7, em Docker |
| Testes | pytest, pytest-django e factory_boy no back-end; Vitest, Testing Library e axe no front-end ([estratégia de testes](../../docs/qualidade-e-testes.md)) |
| Qualidade estática | Ruff, import-linter, ESLint, Prettier, TypeScript estrito |
| Plataforma | Navegadores modernos (Chrome, Edge, Firefox, Safari), servidor Linux com Docker Compose |
| Restrições | Sem senhas próprias; dados na região de São Paulo |

## Verificação da constituição

| Princípio | Atende? | Como |
| --- | --- | --- |
| I. O professor é o dono do conteúdo | N.A. | Esta spec não trata de conteúdo |
| II. Toda resposta mostra a fonte | N.A. | |
| III. Ensinar, não entregar respostas | N.A. | |
| IV. Privacidade por padrão | Sim | Aviso de privacidade versionado, histórico apagável, nenhum dado além de nome, e-mail e matrícula |
| V. Acessível e pensado para o celular | Sim | PWA, telas mobile-first com o design system Farol, testes de acessibilidade |
| VI. Simplicidade e ferramentas populares | Sim | Login e permissões com recursos do próprio Django e django-allauth |
| VII. Especificação antes do código | Sim | Esta spec e este plano antecedem o código do produto |
| VIII. Qualidade verificável | Sim | Teste de permissão automatizado para cada rota (ACE-CS-03) |

## Fundação do repositório

### Estrutura

```
backend/
  farol/              configurações (base, desenvolvimento, teste, producao), urls, celery
  nucleo/             permissões por disciplina, pseudônimo, filtro de dados pessoais
  contas/             spec 001: pessoas, perfis, login, aviso de privacidade
  disciplinas/        spec 001: disciplinas, matrículas, favoritos, importação
  materiais/ tutor/ duvidas/ pratica/ radar/ ia/   specs 002 a 007, criados quando cada spec começar
  pyproject.toml      dependências, Ruff, pytest e contratos do import-linter
  Dockerfile
frontend/
  src/app/            rotas, provedores e layout
  src/funcionalidades/contas/ e disciplinas/
  src/componentes/    componentes do design system Farol
  src/api/            cliente e tipos gerados do OpenAPI
  src/estilos/        tokens do design system (os mesmos do protótipo)
  Dockerfile
prototipo/            o protótipo navegável, movido da raiz
docker-compose.yml
.env.exemplo
```

Cada módulo do back-end segue as camadas da ADR 0007: `api/`, `servicos.py`, `models.py`, `tarefas.py` e `testes/`.

O modelo de usuário personalizado (`contas.Pessoa`) é criado na primeira migração, antes de qualquer outra, porque o Django não permite trocá-lo depois.

Mover o protótipo para `prototipo/` muda o endereço do GitHub Pages para `/Farol/prototipo/`. Um `index.html` na raiz redireciona o endereço antigo, para os links já compartilhados continuarem funcionando. O script `scripts/verificar_specs.py` passa a procurar o código do protótipo na nova pasta.

### Docker Compose

Os serviços são os da [ADR 0008](../../docs/adr/0008-ambiente-local-em-docker.md): `db`, `redis`, `backend`, `worker`, `beat`, `frontend` e `mailpit`. O `frontend` encaminha `/api` para o `backend` (proxy do Vite), de modo que o navegador vê uma só origem. O código é montado como volume, então as mudanças aparecem sem reconstruir as imagens.

### Integração contínua

O workflow do GitHub Actions ganha os jobs Back-end, Contrato e Front-end descritos em [docs/qualidade-e-testes.md](../../docs/qualidade-e-testes.md#integração-contínua), além do job de specs que já existe.

### Login de desenvolvimento

O provedor do login institucional ainda não foi escolhido (Google ou Microsoft). Para desenvolver e demonstrar sem depender disso:

- O comando `python manage.py popular_demo` cria as pessoas, disciplinas e matrículas fictícias do protótipo: a aluna Ana Souza, o professor Carlos Mendes e as seis disciplinas do 2º período de Sistemas de Informação.
- A rota `POST /api/dev/entrar` abre a sessão de uma pessoa fictícia pelo e-mail. Ela só existe quando a configuração `FAROL_LOGIN_DESENVOLVIMENTO` está ligada, o que acontece apenas nas configurações de desenvolvimento e de teste.
- Um teste garante que, com as configurações de produção, a rota não existe (ACE-RNF-03).
- A tela de entrada mostra os botões "Entrar como aluna" e "Entrar como professor" só nesse modo, como no protótipo. O botão do login institucional entra quando o provedor for definido (tarefas ACE-T20 e ACE-T21).

## Modelo de dados

| Entidade | Campos | Observações |
| --- | --- | --- |
| `Pessoa` (estende o usuário do Django) | `email` (único), `nome`, `perfis` (lista: aluno, professor, coordenacao, admin) | Sem senha utilizável |
| `Disciplina` | `codigo`, `nome`, `turma`, `semestre`, `professor` (FK Pessoa) | Único por `codigo` + `turma` + `semestre` |
| `Matricula` | `aluno` (FK Pessoa), `disciplina` (FK), `situacao` (ativa, encerrada), `atualizada_em` | Único por `aluno` + `disciplina` |
| `Favorito` | `pessoa`, `disciplina` | |
| `CienciaPrivacidade` | `pessoa`, `versao_aviso`, `data` | |
| `Importacao` | `arquivo`, `enviada_por`, `status`, `aceitas`, `rejeitadas` (JSON com linha e motivo) | Guarda o relatório |

## Contratos

| Método e caminho | Entrada | Saída | Erros |
| --- | --- | --- | --- |
| `GET /api/saude` | | `{ status: "ok" }` | |
| `POST /api/dev/entrar` | `{ email }` | Pessoa; abre a sessão | 404 quando o login de desenvolvimento está desligado |
| `POST /api/sair` | | 204; encerra a sessão | |
| `GET /api/eu` | | Pessoa, perfis, perfil ativo, se precisa ver o aviso | 401 |
| `POST /api/eu/perfil-ativo` | `{ perfil }` | Pessoa | 400 se o perfil não pertence à pessoa |
| `POST /api/eu/ciencia-privacidade` | `{ versao }` | 204 | |
| `GET /api/eu/historico` | | Conversas do aluno | |
| `DELETE /api/eu/historico` | | 204 | |
| `GET /api/disciplinas` | `?busca=&filtro=todas\|favoritas\|com-tutor` | Lista de disciplinas da pessoa | |
| `PUT /api/disciplinas/{id}/favorito` e `DELETE` | | 204 | 403 se não matriculado |
| `POST /api/importacoes` | CSV (multipart) | `{ id, status }`; o processamento é assíncrono | 400 para arquivo inválido, 403 sem perfil admin |
| `GET /api/importacoes/{id}` | | Relatório | |

Formato proposto do CSV (UTF-8, separador vírgula): `ra,nome,email,codigo_disciplina,nome_disciplina,turma,semestre,email_professor`.

## Como o protótipo implementa

| Requisito | Cobertura | Como o protótipo faz |
| --- | --- | --- |
| ACE-RF-01 | Simulado | A tela de entrada (`js/screens/entrar.js`) oferece "Entrar como aluna" e "Entrar como professor", sem login real |
| ACE-RF-02 | Coberto | Não há senha em lugar nenhum |
| ACE-RF-03 | Parcial | Só os perfis aluno e professor, trocados pela barra de demonstração (`js/shell.js`) |
| ACE-RF-04 | Simulado | As disciplinas vêm fixas de `js/data.js` |
| ACE-RF-05 | Não coberto | Não há servidor |
| ACE-RF-06 | Simulado | O botão "Importar CSV" em `js/screens/prof-disciplina.js` só mostra um aviso |
| ACE-RF-07 | Não coberto | |
| ACE-RF-08 | Não coberto | Pendência do protótipo: tarefa ACE-T06 |
| ACE-RF-09 | Não coberto | |
| ACE-RF-10 | Coberto | Busca, abas, favoritos e grade ou lista em `js/screens/aluno-disciplinas.js` e `js/screens/aluno-inicio.js` |
| ACE-RF-11 | Não coberto | O protótipo não tem manifesto de app |

## Decisões e pesquisa

- **Filtro "Com tutor":** depende de saber se a disciplina tem material pronto, o que só existe com a spec 002. Até lá, a rota aceita o filtro e devolve uma lista vazia. A tarefa ACE-T34 liga o filtro ao serviço de materiais.

- **django-allauth** em vez de implementar OpenID Connect à mão: suporta Google e Microsoft com a mesma configuração e é a biblioteca mais usada para isso no Django.
- **Importação assíncrona** (Celery): planilhas grandes não travam a tela, e o relatório fica guardado.
- **Exclusão de histórico** apaga as conversas do aluno. Os registros pseudônimos usados no radar (spec 007) não guardam o texto ligado ao aluno e por isso não são afetados.

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| Nenhum | | |
