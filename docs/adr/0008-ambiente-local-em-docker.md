# 0008. Rodar todos os serviços em Docker, sem plataforma gerenciada

- **Status:** Proposta
- **Data:** 16/11/2026

## Contexto

O Farol precisa de banco de dados com busca vetorial, fila, cache, armazenamento de arquivos e envio de e-mail. Plataformas gerenciadas como o Supabase entregam parte disso pronto, mas tiram o controle de onde os dados ficam e ligam o projeto a um fornecedor. Os requisitos que pesam:

- Dados de alunos sob controle da instituição (princípio IV da constituição e LGPD).
- Ambiente de desenvolvimento igual ao de produção, que qualquer aluno sobe com um comando, em Windows, macOS ou Linux.
- Nenhuma conta em serviço externo para começar a desenvolver.

## Decisão

1. Tudo roda com Docker Compose, em desenvolvimento, nos testes e em produção (ADR 0006).
2. Serviços do ambiente de desenvolvimento:

   | Serviço | Imagem | Papel |
   | --- | --- | --- |
   | `db` | `pgvector/pgvector` com PostgreSQL 16 | Dados e vetores |
   | `redis` | `redis` 7 | Fila do Celery, cache e contador do limite diário |
   | `backend` | construída de `backend/Dockerfile` | API Django |
   | `worker` e `beat` | mesma imagem do `backend` | Tarefas do Celery e tarefas agendadas |
   | `frontend` | construída de `frontend/Dockerfile` | Servidor de desenvolvimento do Vite |
   | `mailpit` | `axllent/mailpit` | Captura os e-mails enviados, com uma caixa de entrada no navegador |

3. **Arquivos** (PDFs dos professores) passam pela API de armazenamento do Django. Em desenvolvimento e nos testes, ficam num volume do Docker. Em produção, ficam no disco do servidor com backup diário ou num serviço compatível com S3, via django-storages. A escolha é feita na fase 0, sem mudar o código.
4. O envio de PDF passa pelo Django (upload multipart), e não por URL assinada direto no S3. Funciona igual em todos os ambientes.
5. No GitHub Actions, os testes usam as mesmas imagens de PostgreSQL com pgvector e de Redis, como serviços do job.
6. Configurações e segredos ficam em variáveis de ambiente, num arquivo `.env` fora do Git, com um modelo `.env.exemplo` versionado.

## Alternativas consideradas

| Alternativa | Por que não |
| --- | --- |
| Supabase na nuvem | Dados num fornecedor externo, regras de acesso no banco (RLS) longe do código Django e dependência de plataforma |
| Supabase auto-hospedado | É ele próprio um conjunto de muitos containers; acrescenta autenticação e API próprias que duplicariam o Django |
| Firebase | Banco NoSQL sem busca vetorial no PostgreSQL e dependência forte do Google |
| PostgreSQL e Redis instalados direto na máquina | Cada sistema operacional se comporta de um jeito; o ambiente deixa de ser reproduzível |
| MinIO como S3 local | A edição comunitária parou de publicar imagens Docker em outubro de 2025 e entrou em modo de manutenção |
| Outro S3 local (RustFS, SeaweedFS) | Mais um serviço só para imitar o S3; o volume local resolve o desenvolvimento |

## Consequências

- `docker compose up` sobe o sistema inteiro, sem nenhuma conta externa.
- No Windows, é preciso o Docker Desktop com WSL 2. A máquina precisa de memória suficiente para cerca de seis containers.
- O ambiente de desenvolvimento, os testes no CI e a produção usam as mesmas versões de banco e de Redis.
- A ADR 0006 continua valendo para produção. O armazenamento de arquivos passa a seguir esta decisão.
