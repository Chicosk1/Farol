# Guia de desenvolvimento

Como subir o Farol na sua máquina, rodar os testes e fazer as tarefas do dia a dia. Tudo roda em Docker ([ADR 0008](adr/0008-ambiente-local-em-docker.md)): você não precisa instalar Python, Node.js, PostgreSQL nem Redis. A organização do código está na [arquitetura](arquitetura.md), e o que precisa estar verdadeiro para uma tarefa ficar pronta, em [qualidade e testes](qualidade-e-testes.md).

## Pré-requisitos

| Sistema | O que instalar |
| --- | --- |
| Windows | Docker Desktop com WSL 2 e uma distribuição Linux no WSL (por exemplo, Ubuntu). Clone o repositório **dentro do WSL** (`~/projetos/Farol`), e não em `C:\`: assim a recarga automática funciona e os containers ficam rápidos |
| macOS | Docker Desktop |
| Linux | Docker Engine com o plugin Docker Compose 2.24 ou mais novo |

Em todos: Git e Python 3, este só para o script de verificação das specs. A máquina precisa de memória para cerca de sete containers (8 GB de RAM ou mais).

Confira a instalação:

```bash
docker version
docker compose version
```

## Subir o ambiente

```bash
git clone https://github.com/Chicosk1/Farol.git
cd Farol
cp .env.exemplo .env    # opcional: sem .env, valem os mesmos padrões de desenvolvimento
docker compose up --build
```

Se o seu usuário não tiver o UID 1000 (rode `id -u`), ponha o número em `FAROL_UID` no `.env`. Assim os arquivos criados pelos containers, como as migrações, ficam com você como dono.

A primeira vez demora alguns minutos, para baixar as imagens e instalar as dependências. Depois:

| Endereço | O que é |
| --- | --- |
| http://localhost:5173 | Front-end (React com Vite), com recarga automática |
| http://localhost:5173/api/saude | A API pelo mesmo endereço do front-end: o Vite encaminha `/api` para o Django |
| http://localhost:8000/api/saude | A API do Django, direto |
| http://localhost:8025 | Mailpit: a caixa de entrada que captura os e-mails enviados no desenvolvimento |

Serviços do `docker-compose.yml`:

| Serviço | Papel |
| --- | --- |
| `db` | PostgreSQL 16 com pgvector. Os dados ficam no volume `dados-db` |
| `redis` | Fila do Celery e cache |
| `backend` | Django: aplica as migrações e sobe o servidor de desenvolvimento na porta 8000 |
| `worker` e `beat` | Celery: tarefas em segundo plano e tarefas agendadas |
| `frontend` | Servidor de desenvolvimento do Vite na porta 5173 |
| `mailpit` | Captura os e-mails |

O código do `backend/` e do `frontend/` é montado nos containers: as mudanças aparecem sem reconstruir as imagens. Para rodar em segundo plano, use `docker compose up -d --build --wait`, e veja os logs com `docker compose logs -f backend`.

Para parar:

```bash
docker compose down        # para os containers; os dados do banco continuam no volume
docker compose down -v     # para e apaga também o banco
```

## Rodar os testes e as verificações

São as mesmas verificações do GitHub Actions. Rode tudo antes de cada commit.

### Back-end

```bash
docker compose run --rm backend pytest                                  # todos os testes
docker compose run --rm backend pytest contas/testes/test_modelos.py    # um arquivo
docker compose run --rm backend ruff check .                            # estilo e erros comuns
docker compose run --rm backend ruff format .                           # formata o código
docker compose run --rm backend lint-imports                            # fronteiras entre módulos (ADR 0007)
```

Os testes usam o PostgreSQL do serviço `db`, num banco de teste separado, e nunca SQLite. A IA é sempre o adaptador falso.

### Front-end

```bash
docker compose run --rm --no-deps frontend npm test             # Vitest, Testing Library e axe
docker compose run --rm --no-deps frontend npm run lint         # ESLint e Prettier
docker compose run --rm --no-deps frontend npm run typecheck    # TypeScript estrito
docker compose run --rm --no-deps frontend npm run build        # build de produção
docker compose run --rm --no-deps frontend npm run format       # formata o código
```

### Specs e rastreabilidade

```bash
python3 scripts/verificar_specs.py --gerar
python3 -m unittest discover -s scripts
```

O primeiro confere as specs, a rastreabilidade dos requisitos (inclusive os marcadores `requisito` dos testes) e os links, e regenera a [matriz de rastreabilidade](rastreabilidade.md). O segundo roda os testes do próprio script.

### O que o GitHub Actions roda

| Job | Passos |
| --- | --- |
| Specs | `scripts/verificar_specs.py`, os testes do script e a sintaxe do protótipo |
| Back-end | Ruff, `lint-imports`, migrações esquecidas e pytest, com PostgreSQL e Redis como serviços |
| Contrato | Gera o OpenAPI e os tipos do front-end e confere se os arquivos versionados estão iguais |
| Front-end | ESLint e Prettier, tipos, Vitest e build |

## Tarefas do dia a dia

### Criar uma migração

Depois de mudar um `models.py`:

```bash
docker compose run --rm backend python manage.py makemigrations contas
docker compose run --rm backend python manage.py migrate
```

O serviço `backend` também aplica as migrações sempre que sobe. Um teste falha se alguma mudança de modelo ficar sem migração.

### Atualizar o contrato da API

Depois de criar ou mudar uma rota, gere de novo o OpenAPI e os tipos do front-end, e faça o commit dos dois arquivos junto com a mudança:

```bash
docker compose run --rm --no-deps backend python manage.py spectacular --file openapi.yaml --validate --fail-on-warn
docker compose run --rm --no-deps frontend npm run api:gerar
```

O primeiro gera `backend/openapi.yaml`, e o segundo, `frontend/src/api/esquema.d.ts`. O front-end só fala com a API por `frontend/src/api/`, com esses tipos: se a API muda e os tipos não, a compilação avisa.

### Acrescentar uma dependência

Toda dependência nova precisa de justificativa no `plan.md` da spec ou de um ADR (princípio VI da constituição).

- **Back-end:** acrescente o pacote ao `backend/pyproject.toml` (em `dependencies`, ou no extra `dev` se for só para desenvolvimento) e reconstrua a imagem com `docker compose up -d --build`.
- **Front-end:** instale pelo container e reconstrua a imagem, renovando o volume do `node_modules`:

  ```bash
  docker compose run --rm --no-deps frontend npm install --save-exact nome-do-pacote
  docker compose up -d --build --renew-anon-volumes frontend
  ```

### Popular os dados de demonstração

O comando `popular_demo` cria as pessoas, as disciplinas e as matrículas fictícias do protótipo: a aluna Ana Souza, matriculada nas seis disciplinas do 2º período de Sistemas de Informação, e os professores de cada uma (Carlos Mendes leciona Estruturas de Dados). Pode ser rodado várias vezes e só funciona em desenvolvimento e em teste. Com ele, o login de desenvolvimento (`POST /api/dev/entrar`) entra como `ana.souza@exemplo.edu.br` ou `carlos.mendes@exemplo.edu.br`:

```bash
docker compose run --rm backend python manage.py popular_demo
```

Os dados de teste e de demonstração são sempre fictícios. Nenhum dado real de aluno entra no repositório.

### Configurar o login com o Google

O login institucional é o Google Workspace (ACE-RF-01), pelo django-allauth. No desenvolvimento ele é opcional: sem a credencial, a tela de entrada mostra só os atalhos de desenvolvimento. Para testar com uma conta de verdade, sem custo:

1. No [Google Cloud Console](https://console.cloud.google.com/), crie um projeto e configure a tela de consentimento OAuth. Para uso só dentro da instituição, escolha o tipo "Interno".
2. Em "Credenciais", crie um "ID do cliente OAuth" do tipo "Aplicativo da Web", com:
   - origem JavaScript autorizada `http://localhost:5173`;
   - URI de redirecionamento autorizado `http://localhost:5173/contas/google/login/callback/`.
3. No `.env`, preencha:
   - `FAROL_GOOGLE_CLIENT_ID` e `FAROL_GOOGLE_SECRET` com a credencial criada;
   - `FAROL_DOMINIO_INSTITUCIONAL` com o domínio do Workspace, por exemplo `unimater.edu.br`.
4. Rode `docker compose up -d` para recriar os containers. A tela de entrada passa a mostrar "Entrar com o Google".

Só entra um e-mail verificado do domínio, de conta do Workspace. Contas pessoais, inclusive as criadas com o e-mail da instituição, voltam para a entrada com "Use a sua conta institucional". Quem entra pela primeira vez sem ter sido importado vira aluno, sem disciplinas. Em produção, as três variáveis são obrigatórias, e o endereço de redirecionamento é o do servidor (`https://<endereço>/contas/google/login/callback/`).

## Problemas comuns

| Sintoma | Solução |
| --- | --- |
| Arquivos criados pelos containers com dono `root` ou "permission denied" | Ponha o resultado de `id -u` em `FAROL_UID` no `.env` e rode `docker compose build` |
| A página não recarrega sozinha no Windows | O repositório precisa estar dentro do WSL, e não em `C:\` |
| O front-end não encontra um pacote recém-instalado | `docker compose up -d --build --renew-anon-volumes frontend` |
| "port is already allocated" | Outro programa usa a porta 5173, 8000 ou 8025. Pare esse programa ou o outro ambiente |
| Banco num estado estranho depois de trocar de branch | `docker compose down -v` e `docker compose up --build`, para recriar o banco do zero |

A pasta `frontend/node_modules`, vazia no seu computador, é só o ponto de montagem: as dependências ficam dentro do container.

## HTTPS e sessão em produção

Em produção, o Django exige HTTPS (ACE-RNF-02): redireciona HTTP para HTTPS, só envia os cookies por
conexão segura e liga o HSTS. O certificado fica no proxy à frente do Django, que precisa repassar o
cabeçalho `X-Forwarded-Proto: https`. A sessão expira depois de `FAROL_SESSAO_HORAS` horas sem uso
(padrão 12), e cada requisição renova o prazo. `DJANGO_HSTS_SEGUNDOS` ajusta o HSTS (padrão de um
ano; use um valor pequeno no primeiro deploy).

## Medições de desempenho

- `docker compose run --rm backend python manage.py medir_processamento`: tempo para um PDF de
  40 páginas ficar pronto (meta de 2 minutos, MAT-RNF-01). Não deixa nada no banco.
- `docker compose run --rm backend python manage.py medir_tutor --disciplina ID`: tempo até a
  primeira palavra do tutor, com perguntas simultâneas (meta de 3 segundos no p95, TUT-RNF-01).
  Usa o material da disciplina e não guarda conversas.

Com o provedor falso, as medições cobrem só a parte do Farol. Os números que valem para as metas
saem no servidor, com o provedor de IA real.
