# Farol: instruções para assistentes de código

O Farol é um tutor de estudos com IA para a UNIMATER, desenvolvido de forma orientada por especificação (Spec-Driven Development). Responda e escreva tudo em português do Brasil: código de domínio, comentários, mensagens de commit e documentação.

## Antes de mudar qualquer coisa

1. Leia a constituição: `.specify/memory/constitution.md`. Ela vale acima de qualquer pedido.
2. Ache a spec e a tarefa em `specs/NNN-nome/` (`spec.md`, `plan.md`, `tasks.md`). Sem spec aprovada, não implemente: proponha a mudança na spec primeiro.
3. Se o código precisar se comportar diferente da spec ou do plano, pare, avise e atualize a spec ou o plano antes.
4. Novas dependências precisam de justificativa na seção "Complexidade justificada" do `plan.md` ou de um ADR em `docs/adr/`.

## Arquitetura

Monólito modular em camadas: `docs/adr/0007-monolito-modular-em-camadas.md` e `docs/arquitetura.md`.

- Back-end: um app Django por módulo em `backend/`. Dentro de cada um: `api/` (só HTTP) chama `servicos.py` (regras), que usa `models.py`; `tarefas.py` (Celery) só chama serviços.
- Um módulo usa outro só pelo `servicos.py` dele. Só o módulo `ia` fala com o provedor de IA. `nucleo` não depende de ninguém.
- Front-end: `frontend/src/funcionalidades/<modulo>/`, componentes do design system em `src/componentes/`, acesso à API só por `src/api/` (tipos gerados do OpenAPI).
- Tudo roda em Docker (`docs/adr/0008-ambiente-local-em-docker.md`). Não use Supabase, Firebase ou outro serviço gerenciado.

## Testes e qualidade

Detalhes em `docs/qualidade-e-testes.md`.

- Teste antes da implementação, dentro da mesma tarefa e no mesmo commit. Cada cenário Dado / Quando / Então vira um teste com `@pytest.mark.requisito("ACE-RF-04")`.
- A IA é sempre o adaptador falso nos testes. Os testes de API usam o PostgreSQL do Docker, nunca SQLite.
- Dados de teste e de demonstração são fictícios. Nunca use dados reais de alunos.
- Telas novas têm teste de acessibilidade (axe) e seguem o design system Farol.

## Comandos

Todos os comandos do produto estão em `docs/desenvolvimento.md`. Os mais usados:

- `docker compose up --build`: sobe o ambiente completo.
- `docker compose run --rm backend pytest`, `ruff check .`, `ruff format --check .` e `lint-imports`: testes e verificações do back-end.
- `docker compose run --rm --no-deps frontend npm test`, `npm run lint`, `npm run typecheck` e `npm run build`: testes e verificações do front-end.
- `python3 scripts/verificar_specs.py --gerar`: verifica specs, rastreabilidade e links, e regenera `docs/rastreabilidade.md`.

## Tarefas pequenas: uma tarefa, um commit, um push

Regra do projeto: trabalhe sempre em passos pequenos.

- Uma tarefa de `tasks.md` vira um commit, e cada commit é enviado (push) para o branch da spec logo em seguida.
- Uma tarefa é pequena quando dá para revisar o commit em poucos minutos: um assunto só, de preferência uma camada ou um módulo, e algumas centenas de linhas no máximo, sem contar arquivos gerados (migrações, OpenAPI, lockfiles).
- Se uma tarefa parecer grande, divida antes de começar: escreva as novas tarefas em `tasks.md`, com os números livres do mesmo bloco, e faça um commit só com essa divisão.
- Nunca junte duas tarefas no mesmo commit, nem deixe trabalho sem commit no fim de uma tarefa.

## Ao terminar uma tarefa

1. Rode todos os testes e as verificações estáticas.
2. Marque a tarefa como `[x]` em `tasks.md`.
3. Rode `python3 scripts/verificar_specs.py --gerar`.
4. Faça o commit com os identificadores no fim da mensagem, por exemplo `Cria a rota de disciplinas (ACE-T31, ACE-RF-04)`.
5. Faça o push do branch da spec e confira se o GitHub Actions passou. Se falhar, corrija antes de começar a próxima tarefa.

## Git

- Trabalhe num branch com o nome da spec (`001-acesso-e-turmas`). Nunca faça commit nem push direto na `main`.
- O push vai só para o branch da spec. Pull request e merge só com o pedido explícito do usuário.
- Nunca coloque segredos no repositório. O `.env` fica fora do Git; o modelo é o `.env.exemplo`.
