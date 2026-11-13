# Plano técnico: Radar da turma

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `007-radar-da-turma` |
| Status | Em revisão |
| Atualizado em | 2026-11-13 |

## Resumo

Uma tarefa do Celery roda toda madrugada para cada disciplina: reúne os registros de uso da semana (spec 003), agrupa as perguntas pela proximidade dos vetores com um algoritmo simples do scikit-learn, descarta grupos com menos de 5 alunos distintos, pede ao modelo um nome curto e exemplos para cada grupo e cruza com as taxas de acerto (spec 005). O resultado é gravado pronto em `RadarSemanal`, e a tela só lê.

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | Python 3.12, TypeScript 5 |
| Dependências principais | scikit-learn (agrupamento), Celery beat, e-mail transacional |
| Armazenamento | PostgreSQL |
| Testes | pytest com registros sintéticos, incluindo grupos de 4 e de 5 alunos |
| Metas de desempenho | Tela em até 2 s (RAD-RNF-01); cálculo de todas as disciplinas antes das 6h |

## Verificação da constituição

| Princípio | Atende? | Como |
| --- | --- | --- |
| I. O professor é o dono do conteúdo | Sim | Os tópicos apontam para o material do próprio professor |
| II. Toda resposta mostra a fonte | N.A. | |
| III. Ensinar, não entregar respostas | N.A. | |
| IV. Privacidade por padrão | Sim | Mínimo de 5 alunos distintos para tópicos e taxas; só identificadores pseudônimos; exemplos filtrados |
| V. Acessível e pensado para o celular | Sim | Barras com o número escrito ao lado, sem depender só de cor |
| VI. Simplicidade e ferramentas populares | Sim | scikit-learn, sem serviço de análise externo |
| VII. Especificação antes do código | Sim | |
| VIII. Qualidade verificável | Sim | Teste automático da regra dos 5 alunos (RAD-RF-04, RAD-RF-07) |

## Modelo de dados

| Entidade | Campos | Observações |
| --- | --- | --- |
| `RadarSemanal` | `disciplina`, `semana` (data da segunda-feira), `indicadores` (JSON), `topicos` (JSON), `acertos` (JSON), `sugestao` (JSON), `calculado_em` | Único por `disciplina` + `semana` |
| `ExemploOculto` | `disciplina`, `hash_texto`, `ocultado_por`, `data` | Exemplos que o professor escondeu não voltam |

Formato de um tópico em `topicos`: `{ nome, alunos, exemplos: [..], material_id }`.

## Contratos

| Método e caminho | Entrada | Saída | Erros |
| --- | --- | --- | --- |
| `GET /api/disciplinas/{id}/radar` | `?semana=AAAA-MM-DD` | Radar pré-calculado da semana | 403 se não for professor da disciplina, 404 sem dados |
| `GET /api/disciplinas/{id}/radar/semanas` | | Semanas disponíveis | |
| `POST /api/disciplinas/{id}/radar/exemplos-ocultos` | `{ texto }` | 204 | |
| `PATCH /api/disciplinas/{id}/tutor/configuracao` | `{ resumo_semanal }` | Configuração | Mesma rota da spec 003 |

Tarefas periódicas: `radar.calcular` às 3h, para todas as disciplinas; `radar.enviar_resumos` às segundas, às 6h30.

## Como o protótipo implementa

| Requisito | Cobertura | Como o protótipo faz |
| --- | --- | --- |
| RAD-RF-01 | Simulado | Os números de cada semana são fixos em `radar` (`js/data.js`) |
| RAD-RF-02 | Coberto | Quatro indicadores no topo de `js/screens/prof-radar.js`; perguntas ao tutor e dúvidas reagem ao uso da aluna |
| RAD-RF-03 | Coberto | Cinco tópicos com barra, número de alunos, exemplos e "Ver o material da aula" |
| RAD-RF-04 | Simulado | Todos os tópicos de exemplo têm 6 ou mais alunos, e a nota de privacidade explica a regra |
| RAD-RF-05 | Não coberto | Os exemplos fictícios já não têm dados pessoais; não há como ocultar |
| RAD-RF-06 | Coberto | Nenhuma tela do professor mostra dado de aluno |
| RAD-RF-07 | Parcial | Acerto por tópico; não há acerto por questão |
| RAD-RF-08 | Coberto | Sugestão de 3 tópicos para a próxima aula |
| RAD-RF-09 | Coberto | Seletor entre a semana 17 (atual) e a 16 |
| RAD-RF-10 | Simulado | Só a chave "Resumo semanal por e-mail" em `js/screens/prof-disciplina.js` |
| RAD-RF-11 | Coberto | "Gerar 5 questões de revisão" leva à tela de Questões com rascunhos novos |

## Decisões e pesquisa

- **Pré-cálculo de madrugada** em vez de consulta ao vivo: a tela abre rápido, o custo de IA é previsível (uma chamada por tópico por dia) e a regra dos 5 alunos é aplicada uma vez, num lugar só.
- **Agrupamento:** começar com k-means sobre os vetores das perguntas, com k escolhido pelo número de perguntas. Se os professores não reconhecerem os tópicos (RAD-CS-01), testar agrupamento hierárquico.
- **Pontuação da sugestão:** `alunos_do_topico normalizado × (1 − acerto do tópico)`; tópicos sem quiz entram com acerto neutro de 50%.

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| scikit-learn como dependência nova | Agrupar perguntas parecidas sem depender de nomes de tópico escritos à mão | Agrupar por palavras-chave falha com sinônimos e erros de digitação |
