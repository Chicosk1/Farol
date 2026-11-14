# 0006. Rodar tudo com Docker Compose em um servidor em São Paulo

- **Status:** Proposta
- **Data:** 12/11/2026

## Contexto

O piloto atende cerca de 400 alunos. A TI da instituição precisa conseguir operar o sistema, e os dados devem ficar no Brasil.

## Decisão

Nginx, Django, Celery, Redis e PostgreSQL rodam com Docker Compose em uma máquina virtual na região de São Paulo (4 vCPU e 8 GB), com HTTPS e backup diário. Os PDFs ficam em armazenamento compatível com S3.

## Alternativas consideradas

| Alternativa | Prós | Contras |
| --- | --- | --- |
| Kubernetes | Escala e alta disponibilidade | Complexidade muito acima do necessário para o piloto |
| Plataformas prontas (Render, Railway, Heroku) | Deploy simples | Custo maior por recurso e pouca escolha de região no Brasil |

## Consequências

- O mesmo arquivo sobe o sistema no notebook do desenvolvedor e em produção.
- Uma única máquina é ponto único de falha. Aceitável no piloto com backup diário e teste de restauração mensal.
- Ao escalar para a instituição inteira, o banco migra para um serviço gerenciado.
