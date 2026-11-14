# Plano técnico: Questões e quizzes

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `005-questoes-e-quizzes` |
| Status | Em revisão |
| Atualizado em | 2026-11-13 |

## Resumo

O pedido de geração vira uma tarefa no Celery, que envia os trechos da aula ao modelo pelo módulo `ia/`, pedindo as questões em JSON com esquema fixo. O servidor valida cada questão contra o esquema e confere se o trecho de origem existe na aula; o que não passa é descartado. As questões aprovadas são servidas ao aluno pela rota do quiz, e cada resposta gera um registro pseudônimo para o radar.

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | Python 3.12, TypeScript 5 |
| Dependências principais | Celery, validação de JSON com Pydantic, módulo `ia/` |
| Armazenamento | PostgreSQL |
| Testes | pytest com provedor falso que devolve JSON válido, inválido e sem trecho |
| Metas de desempenho | 10 rascunhos em até 1 minuto (QUE-RNF-01) |

## Verificação da constituição

| Princípio | Atende? | Como |
| --- | --- | --- |
| I. O professor é o dono do conteúdo | Sim | Só material pronto da aula; nada publicado sem aprovação; filtro de status em todas as rotas do aluno |
| II. Toda resposta mostra a fonte | Sim | Toda questão tem trecho de origem, e o retorno do quiz leva a ele |
| III. Ensinar, não entregar respostas | Sim | O erro leva à justificativa e ao tutor, não só ao gabarito |
| IV. Privacidade por padrão | Sim | Respostas registradas com identificador pseudônimo |
| V. Acessível e pensado para o celular | Sim | Alternativas como botões grandes, retorno com `role="status"` |
| VI. Simplicidade e ferramentas populares | Sim | Pydantic para validar o JSON, sem biblioteca de orquestração |
| VII. Especificação antes do código | Sim | |
| VIII. Qualidade verificável | Sim | Taxa de aprovação sem edição pesada medida na própria tela (QUE-CS-02) |

## Modelo de dados

| Entidade | Campos | Observações |
| --- | --- | --- |
| `PedidoGeracao` | `material`, `quantidade` (5 a 20), `status`, `pedido_por`, `criado_em` | |
| `Questao` | `material`, `pedido` (opcional), `enunciado`, `alternativas` (4), `correta` (0 a 3), `justificativa`, `trecho` (FK Trecho), `status` (pendente, publicada, descartada), `nova`, `editada`, `origem_retirada` | Índice por `material` + `status` |
| `RespostaQuiz` | `questao`, `aluno_pseudonimo`, `alternativa`, `acerto`, `respondida_em`, `contexto` (quiz ou revisão) | Base da taxa de acerto do radar |
| `ProgressoQuiz` | `aluno`, `material`, `indice_atual`, `respostas` | Permite continuar de onde parou |

## Contratos

| Método e caminho | Entrada | Saída | Erros |
| --- | --- | --- | --- |
| `POST /api/materiais/{id}/geracoes` | `{ quantidade }` | `{ pedido_id }` (202) | 400 fora de 5 a 20, 409 material não pronto |
| `GET /api/geracoes/{id}` | | Status do pedido | |
| `GET /api/disciplinas/{id}/questoes` | `?status=pendente\|publicada\|descartada` | Questões e contagens (só professor) | 403 |
| `PATCH /api/questoes/{id}` | Campos editáveis ou `{ status }` | Questão | 400 se a edição quebrar o formato, 403 |
| `GET /api/materiais/{id}/quiz` | | Questões publicadas, sem o gabarito | 403 |
| `POST /api/questoes/{id}/respostas` | `{ alternativa }` | `{ acerto, correta, justificativa, citacao }` | 403, 404 se não publicada |

O gabarito só é enviado ao aluno depois que ele responde.

## Como o protótipo implementa

| Requisito | Cobertura | Como o protótipo faz |
| --- | --- | --- |
| QUE-RF-01 | Parcial | Escolha da aula e da quantidade (2, 3 ou 5) em `js/screens/prof-questoes.js`; o banco de exemplo limita a quantidade |
| QUE-RF-02 | Simulado | Os rascunhos saem de `bancoGeracao` em `js/data.js`, após uma espera simulada |
| QUE-RF-03 | Não coberto | O banco de exemplo só tem questões válidas |
| QUE-RF-04 | Coberto | A aluna só recebe questões com status aprovada (`js/screens/aluno-pratica.js`) |
| QUE-RF-05 | Coberto | Aprovar, editar, descartar e voltar para pendentes em `js/screens/prof-questoes.js` |
| QUE-RF-06 | Coberto | Abas com contagem |
| QUE-RF-07 | Parcial | A questão aprovada entra no quiz da aula; a revisão do dia ainda usa um conjunto fixo |
| QUE-RF-08 | Coberto | Retorno imediato com justificativa e link para o trecho |
| QUE-RF-09 | Parcial | Os tópicos errados aparecem no resumo final com atalho para o tutor; falta o botão em cada questão errada (tarefa QUE-T07) |
| QUE-RF-10 | Coberto | Resumo com acertos e tópicos para revisar |
| QUE-RF-11 | Não coberto | As taxas do radar são fixas |

## Decisões e pesquisa

- **JSON com esquema fixo e validação no servidor** em vez de confiar no texto do modelo: questões malformadas são descartadas antes de chegar ao professor (QUE-RF-03).
- **Conferência do trecho de origem:** o modelo devolve o número do trecho recebido; o servidor confere se ele pertence à aula pedida.
- **Gabarito escondido até a resposta:** evita que o aluno veja a correta inspecionando a rede.

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| Pydantic como dependência nova | Validar o JSON do modelo com mensagens de erro claras | Validação manual com `if` espalhados é frágil e difícil de testar |
