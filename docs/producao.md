# Colocar o Farol em produção

Lista do que o servidor precisa para o piloto, conforme a [ADR 0006](adr/0006-docker-compose-em-um-servidor.md) (Docker Compose num servidor) e a [ADR 0009](adr/0009-ia-com-modelos-abertos-no-ollama.md) (IA no Ollama). As configurações de produção ficam em `backend/farol/configuracoes/producao.py`: sem uma variável obrigatória, o Django não sobe e diz qual falta.

O arquivo do Docker Compose de produção, com o proxy HTTPS e o front-end compilado, ainda não existe. Este guia diz o que ele precisa ter.

## Servidor

- Máquina virtual com Docker, na região de São Paulo (constituição, localização dos dados).
- Memória: cerca de 4 GB para o Farol (banco, Redis, Django e Celery) e mais 6 GB para o Ollama com os dois modelos. Com GPU, as respostas do tutor ficam bem mais rápidas.
- Disco com backup diário para o banco e para a pasta dos PDFs.

## Variáveis de ambiente obrigatórias

| Variável | O que é |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `farol.configuracoes.producao` |
| `DJANGO_SECRET_KEY` | Chave longa e aleatória, só do servidor |
| `DJANGO_ALLOWED_HOSTS` | Endereço público, por exemplo `farol.unimater.edu.br` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` | Banco PostgreSQL 16 com pgvector |
| `FAROL_ARQUIVOS` | Pasta dos PDFs enviados, num disco com backup |
| `FAROL_SEGREDO_PSEUDONIMO` | Segredo dos identificadores pseudônimos (TUT-RF-12). Trocá-lo muda todos os identificadores |
| `FAROL_IA_ADAPTADOR` | `ia.adaptadores.compativel_openai.ProvedorCompativelOpenAI` |
| `FAROL_DOMINIO_INSTITUCIONAL` | Opcional. Restringe a entrada a um domínio de Google Workspace, por exemplo `unimater.edu.br`; vazio, entra qualquer conta Google de e-mail verificado |
| `FAROL_GOOGLE_CLIENT_ID`, `FAROL_GOOGLE_SECRET` | Credencial OAuth do Google ([passo a passo](desenvolvimento.md#configurar-o-login-com-o-google)). O endereço de retorno é `https://<endereço>/contas/google/login/callback/` |

Opcionais, com padrão:

- `FAROL_IA_ENDERECO`, os modelos e `FAROL_TUTOR_SIMILARIDADE_MINIMA` (calibrada para o `embeddinggemma`, como no `.env.exemplo`);
- `FAROL_SESSAO_HORAS` (12) e `DJANGO_HSTS_SEGUNDOS` (um ano).

## Proxy com HTTPS

O certificado fica num proxy à frente do Django (Nginx ou Caddy), que:

- redireciona HTTP para HTTPS e repassa o cabeçalho `X-Forwarded-Proto` (o Django confia nele para saber que a conexão era segura);
- encaminha ao Django as rotas `/api/`, `/contas/`, `/admin/` e `/static/`;
- serve o front-end compilado (`npm run build`, pasta `frontend/dist`) e responde `index.html` nas outras rotas, para o React Router;
- não serve `/media/` diretamente: os PDFs saem pelo Django, que confere a permissão de quem pede.

Os arquivos estáticos do painel administrativo vêm de `python manage.py collectstatic`, na pasta `backend/staticfiles`.

## Banco de dados

As migrações criam as extensões `vector` (pgvector) e `unaccent`. Para isso, o usuário do banco precisa poder criar extensões. Se a TI não der essa permissão, um administrador do banco cria as duas antes da primeira migração:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS unaccent;
```

## Depois de subir

1. `python manage.py migrate` e `python manage.py collectstatic`.
2. `python manage.py createsuperuser`, para a equipe de TI entrar no `/admin/`. A pessoa precisa entrar pelo Google depois: o Farol não tem senha própria.
3. Importar as turmas pelo `/admin/` (CSV do sistema acadêmico).
4. Medir no próprio servidor:
   - `python manage.py medir_processamento`: um PDF de 40 páginas, meta de 2 minutos;
   - `python manage.py medir_tutor --disciplina ID`: primeira palavra do tutor, meta de 3 segundos no p95;
   - `python manage.py avaliar_tutor`: qualidade das respostas, com as metas TUT-CS-01, 03 e 04.
