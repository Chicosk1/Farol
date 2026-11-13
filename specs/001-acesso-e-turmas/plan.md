# Plano técnico: Acesso e turmas

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `001-acesso-e-turmas` |
| Status | Em revisão |
| Atualizado em | 2026-11-13 |

## Resumo

Login por OpenID Connect com django-allauth, perfis guardados no banco, permissões verificadas por disciplina em cada rota da API, importação de CSV como tarefa assíncrona idempotente e front-end React instalável como PWA. Esta é a primeira spec do produto, então o plano também cria a fundação do repositório (Docker Compose, Django, React e integração contínua).

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | Python 3.12, TypeScript 5 |
| Dependências principais | Django LTS, Django REST Framework, django-allauth, React, Vite, Tailwind CSS, vite-plugin-pwa |
| Armazenamento | PostgreSQL 16 |
| Testes | pytest e pytest-django no back-end, Vitest no front-end |
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

## Estrutura do repositório para o produto

Quando o desenvolvimento do produto começar, o repositório passa a ter:

```
backend/              projeto Django
  farol/              configurações
  contas/             login, perfis, aviso de privacidade (spec 001)
  disciplinas/        disciplinas, matrículas, importação (spec 001)
  materiais/          spec 002
  tutor/              specs 003 e 004
  ia/                 módulo único de acesso ao provedor de IA (ADR 0005)
  pratica/            specs 005 e 006
  radar/              spec 007
frontend/             React + Vite + TypeScript
prototipo/            o protótipo navegável atual, movido da raiz
docker-compose.yml
```

Mover o protótipo para `prototipo/` muda o endereço do GitHub Pages para `/Farol/prototipo/`. Essa mudança é a tarefa ACE-T10 e só acontece quando o produto começar.

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

- **django-allauth** em vez de implementar OpenID Connect à mão: suporta Google e Microsoft com a mesma configuração e é a biblioteca mais usada para isso no Django.
- **Importação assíncrona** (Celery): planilhas grandes não travam a tela, e o relatório fica guardado.
- **Exclusão de histórico** apaga as conversas do aluno. Os registros pseudônimos usados no radar (spec 007) não guardam o texto ligado ao aluno e por isso não são afetados.

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| Nenhum | | |
