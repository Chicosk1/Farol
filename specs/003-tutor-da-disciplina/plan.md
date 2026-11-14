# Plano técnico: Tutor da disciplina

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `003-tutor-da-disciplina` |
| Status | Em revisão |
| Atualizado em | 2026-11-13 |

## Resumo

RAG (geração aumentada por recuperação) com o PostgreSQL e o pgvector: a pergunta é filtrada, vira um vetor, e o banco devolve os 6 trechos mais próximos da disciplina. Se nenhum passa do limite de similaridade, o tutor responde que não encontrou, sem chamar o modelo. Se há trechos, o módulo `ia/` envia ao modelo as regras fixas, os trechos numerados e a pergunta, e a resposta volta em streaming com marcações do trecho de cada afirmação, que o servidor converte em citações. O fluxo completo está em [docs/arquitetura.md](../../docs/arquitetura.md#2-o-aluno-pergunta-specs-003-e-004).

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | Python 3.12, TypeScript 5 |
| Dependências principais | Django REST Framework, pgvector, Redis (contador do limite), SDK oficial do provedor de IA |
| Armazenamento | PostgreSQL com pgvector; Redis para contadores diários |
| Testes | pytest; conjunto de 100 perguntas por disciplina (avaliação automática); Vitest no front-end |
| Metas de desempenho | Primeira palavra em até 3 s no p95 (TUT-RNF-01) |
| Restrições | Até R$ 2 por aluno por mês; nada de identificação do aluno no prompt |

## Verificação da constituição

| Princípio | Atende? | Como |
| --- | --- | --- |
| I. O professor é o dono do conteúdo | Sim | A busca filtra por disciplina e por material pronto |
| II. Toda resposta mostra a fonte | Sim | O servidor descarta frases sem marcação de trecho antes de exibir (TUT-RF-03) |
| III. Ensinar, não entregar respostas | Sim | Modo pistas no prompt e modo prova verificado antes de qualquer processamento |
| IV. Privacidade por padrão | Sim | Filtro de dados pessoais antes do provedor; registros com identificador pseudônimo |
| V. Acessível e pensado para o celular | Sim | Região `aria-live` para respostas, conversa operável por teclado |
| VI. Simplicidade e ferramentas populares | Sim | Sem LangChain; um módulo próprio pequeno (ADR 0005) |
| VII. Especificação antes do código | Sim | |
| VIII. Qualidade verificável | Sim | Conjunto de 100 perguntas roda no GitHub Actions a cada mudança de prompt ou modelo |

## Modelo de dados

| Entidade | Campos | Observações |
| --- | --- | --- |
| `Conversa` | `aluno`, `disciplina`, `criada_em` | Visível só para o aluno; apagável (ACE-RF-09) |
| `Mensagem` | `conversa`, `autor`, `texto`, `tipo` (resposta, pistas, nao_encontrado, saudacao, erro), `avaliacao` (util, nao_util, incorreta, nula) | |
| `Citacao` | `mensagem`, `trecho` (FK Trecho), `ordem` | Rótulo "Aula N, p. M" montado a partir do trecho |
| `ConfiguracaoTutor` | `disciplina`, `modo_pistas` (padrão verdadeiro), `limite_diario` (20, 40 ou 60), `politica` | |
| `JanelaProva` | `disciplina`, `inicio`, `fim`, `criada_por` | Modo prova imediato = janela com início agora e fim em aberto |
| `RegistroUso` | `aluno_pseudonimo` (HMAC do id do aluno com segredo por disciplina), `disciplina`, `pergunta_filtrada`, `trechos`, `tipo`, `avaliacao`, `tokens_entrada`, `tokens_saida`, `custo` | Base do radar (spec 007) e da análise de qualidade |
| `RevisaoResposta` | `mensagem`, `status`, `nota_da_equipe` | Fila de respostas marcadas como incorretas |

Contador diário no Redis: chave `limite:{disciplina}:{aluno}:{AAAA-MM-DD}` com expiração de 48 horas.

## Contratos

| Método e caminho | Entrada | Saída | Erros |
| --- | --- | --- | --- |
| `GET /api/disciplinas/{id}/tutor` | | Configuração, se está pausado, uso do dia, sugestões | 403 |
| `POST /api/disciplinas/{id}/tutor/perguntas` | `{ texto }` (até 1.000 caracteres) | Stream de eventos (SSE): `inicio`, `texto`, `citacao`, `fim` com o tipo da resposta | 400 texto inválido, 423 modo prova, 429 limite atingido, 503 provedor indisponível |
| `PUT /api/mensagens/{id}/avaliacao` | `{ avaliacao }` | 204 | 403 |
| `PATCH /api/disciplinas/{id}/tutor/configuracao` | `{ modo_pistas?, limite_diario?, politica? }` | Configuração | 403 se não for o professor |
| `POST /api/disciplinas/{id}/janelas-prova` | `{ inicio, fim? }` | Janela | 400 se `fim` antes de `inicio` |
| `DELETE /api/janelas-prova/{id}` | | 204 | |

Interface do módulo `ia/` (ADR 0005):

```python
def gerar_embedding(texto: str) -> list[float]: ...
def responder(regras: str, trechos: list[TrechoNumerado], pergunta: str) -> Iterator[EventoResposta]: ...
```

## Como o protótipo implementa

| Requisito | Cobertura | Como o protótipo faz |
| --- | --- | --- |
| TUT-RF-01 | Simulado | `js/tutor.js` escolhe uma resposta pronta de `tutor` em `js/data.js` por palavras-chave |
| TUT-RF-02 | Coberto | Cada resposta pronta tem citação clicável que abre o trecho destacado (`js/ui.js`) |
| TUT-RF-03 | Coberto | Toda resposta da base tem citação; o que não está na base cai em "não encontrei" |
| TUT-RF-04 | Simulado | Perguntas sem palavra-chave conhecida ou com termos administrativos recebem "Não encontrei" e o botão de envio |
| TUT-RF-05 | Simulado | Pedidos com palavras como "resposta" ou "exercício" recebem a versão `pistas` da resposta, marcada "Modo pistas" |
| TUT-RF-06 | Coberto | Chave "Modo pistas" em `js/screens/prof-disciplina.js` |
| TUT-RF-07 | Parcial | Liga e desliga na hora; não há agendamento de janelas |
| TUT-RF-08 | Coberto | Contador, escolha entre 20, 40 e 60 e bloqueio ao atingir o limite (`js/screens/aluno-tutor.js`) |
| TUT-RF-09 | Parcial | Só "Útil" e "Incorreta"; falta "Não útil" (tarefa TUT-T07) |
| TUT-RF-10 | Coberto | Política editável em `js/screens/prof-disciplina.js` e exibida no tutor |
| TUT-RF-11 | Não coberto | |
| TUT-RF-12 | Simulado | O histórico fica só no navegador de quem usa |
| TUT-RF-13 | Simulado | Efeito de digitação na resposta pronta |
| TUT-RF-14 | Coberto | Sugestões de pergunta em `sugestoesTutor` (`js/data.js`) |

## Decisões e pesquisa

- **Limite de similaridade para "não encontrei":** valor inicial calibrado com o conjunto de 100 perguntas, que inclui perguntas sem base no material (TUT-CS-04).
- **Detecção de pedido de exercício para o modo pistas:** feita pelo próprio modelo, com instrução nas regras fixas, e não por palavras-chave. As palavras-chave do protótipo servem só para a demonstração.
- **Streaming por SSE (Server-Sent Events)** e não WebSocket: comunicação de uma via, suportada pelo Django e pelo Nginx sem componente extra.
- **Identificador pseudônimo por disciplina:** conta alunos distintos para a regra dos 5 alunos do radar sem permitir cruzar disciplinas.
- **Avaliação automática no GitHub Actions:** o conjunto de 100 perguntas fica em `backend/tutor/avaliacao/`, com resposta esperada e trecho esperado. A métrica principal é a proporção de respostas que citam o trecho esperado.

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| Redis para o contador diário | Contagem rápida e com expiração automática, várias vezes por segundo | Contar no PostgreSQL a cada pergunta gera carga e corrida entre requisições; o Redis já existe para o Celery |
