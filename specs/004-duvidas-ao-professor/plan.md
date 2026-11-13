# Plano técnico: Dúvidas ao professor

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `004-duvidas-ao-professor` |
| Status | Em revisão |
| Atualizado em | 2026-11-13 |

## Resumo

A dúvida é um registro separado da conversa: guarda só o texto filtrado, a disciplina e a data do dia. A ligação com o aluno fica numa tabela de envio que só as rotas do aluno consultam. O professor lê as dúvidas pelo radar e recebe uma notificação no sino.

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | Python 3.12, TypeScript 5 |
| Dependências principais | Django REST Framework; o filtro de dados pessoais da spec 003 (TUT-RF-11) |
| Armazenamento | PostgreSQL |
| Testes | pytest, incluindo testes que garantem que nenhuma rota do professor devolve dados do aluno |

## Verificação da constituição

| Princípio | Atende? | Como |
| --- | --- | --- |
| I. O professor é o dono do conteúdo | N.A. | |
| II. Toda resposta mostra a fonte | Sim | A dúvida nasce justamente quando não há fonte, em vez de o tutor inventar |
| III. Ensinar, não entregar respostas | N.A. | |
| IV. Privacidade por padrão | Sim | Texto filtrado, data arredondada, ligação com o aluno isolada |
| V. Acessível e pensado para o celular | Sim | Pré-visualização em modal acessível, notificação com texto |
| VI. Simplicidade e ferramentas populares | Sim | Duas tabelas, sem serviço novo |
| VII. Especificação antes do código | Sim | |
| VIII. Qualidade verificável | Sim | Teste automático de que as rotas do professor não expõem o aluno |

## Modelo de dados

| Entidade | Campos | Observações |
| --- | --- | --- |
| `Duvida` | `disciplina`, `texto` (filtrado), `data` (só o dia), `status` (aberta, respondida, oculta), `vista` (booleano), `ocultada_por`, `ocultada_em` | Não tem chave para o aluno |
| `EnvioDuvida` | `mensagem` (FK Mensagem do aluno, única), `duvida` (FK) | Consultada só por rotas do aluno |
| `Notificacao` | `pessoa`, `tipo`, `referencia`, `lida` | Compartilhada com a spec 002 |

## Contratos

| Método e caminho | Entrada | Saída | Erros |
| --- | --- | --- | --- |
| `POST /api/mensagens/{id}/duvida/previa` | | `{ texto_filtrado }` | 400 se a mensagem não for "não encontrei", 409 se já enviada |
| `POST /api/mensagens/{id}/duvida` | | `{ duvida_id, status }` | 409 se já enviada |
| `GET /api/disciplinas/{id}/duvidas` | `?status=aberta\|respondida` | Lista para o professor: texto, data, status, vista | 403 se não for o professor |
| `PATCH /api/duvidas/{id}` | `{ status }` | Dúvida | 403 |
| `GET /api/notificacoes` | | Notificações da pessoa | |

## Como o protótipo implementa

| Requisito | Cobertura | Como o protótipo faz |
| --- | --- | --- |
| DUV-RF-01 | Coberto | Botão "Enviar dúvida ao professor" em toda resposta "não encontrei" (`js/screens/aluno-tutor.js`) |
| DUV-RF-02 | Não coberto | O envio é imediato, sem pré-visualização (tarefa DUV-T05) |
| DUV-RF-03 | Coberto | A dúvida guarda só o texto e "há quanto tempo" |
| DUV-RF-04 | Coberto | Depois do envio, o botão é trocado pela nota "Dúvida enviada ao professor, sem o seu nome." |
| DUV-RF-05 | Coberto | Lista com a marca "Nova" em `js/screens/prof-radar.js` |
| DUV-RF-06 | Coberto | Sino de notificações com ponto em `js/shell.js` |
| DUV-RF-07 | Parcial | "Respondida em aula" existe; ocultar não existe |
| DUV-RF-08 | Não coberto | |
| DUV-RF-09 | Não coberto | O resumo semanal é só uma chave de configuração |

## Decisões e pesquisa

- **Data arredondada para o dia:** com horário exato, o professor poderia ligar a dúvida a quem saiu cedo da aula, por exemplo.
- **Tabela de envio separada** em vez de um campo `aluno` na dúvida: deixa explícito, no próprio modelo, que a dúvida não conhece o autor.

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| Nenhum | | |
