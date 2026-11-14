# Matriz de rastreabilidade

Gerada por `scripts/verificar_specs.py --gerar` a partir das specs, dos planos, das tarefas e dos comentários `Specs:` no código do protótipo. Não edite à mão: mude a fonte e rode o script de novo.

Legenda da coluna Protótipo: **Coberto** funciona como no produto, com dados fictícios; **Simulado** a tela existe, mas o comportamento por trás é encenado com dados fixos; **Parcial** cobre parte do requisito; **Não coberto** ainda não existe no protótipo.

## Resumo

| Spec | Requisitos funcionais | Coberto | Simulado | Parcial | Não coberto | Tarefas feitas | Pontos a esclarecer |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [001 Acesso e turmas](../specs/001-acesso-e-turmas/spec.md) | 11 | 2 | 3 | 1 | 5 | 5 de 28 | 3 |
| [002 Materiais da disciplina](../specs/002-materiais-da-disciplina/spec.md) | 11 | 2 | 5 | 1 | 3 | 4 de 21 | 2 |
| [003 Tutor da disciplina](../specs/003-tutor-da-disciplina/spec.md) | 14 | 6 | 5 | 2 | 1 | 8 de 35 | 0 |
| [004 Dúvidas ao professor](../specs/004-duvidas-ao-professor/spec.md) | 9 | 5 | 0 | 1 | 3 | 4 de 14 | 1 |
| [005 Questões e quizzes](../specs/005-questoes-e-quizzes/spec.md) | 11 | 5 | 1 | 3 | 2 | 6 de 20 | 1 |
| [006 Revisão do dia](../specs/006-revisao-do-dia/spec.md) | 10 | 5 | 3 | 1 | 1 | 5 de 17 | 1 |
| [007 Radar da turma](../specs/007-radar-da-turma/spec.md) | 11 | 6 | 3 | 1 | 1 | 5 de 18 | 0 |

## Pendências do protótipo

Tarefas já especificadas que aproximam o protótipo do comportamento descrito nas specs:

- `ACE-T06` [H4] Aviso de privacidade na primeira entrada da aluna, com botão "Entendi", em `js/screens/aluno-inicio.js` (ACE-RF-08) ([tarefas](../specs/001-acesso-e-turmas/tasks.md))
- `TUT-T07` [H6] Acrescentar a avaliação "Não útil" ao lado de "Útil" e "Incorreta" em `js/screens/aluno-tutor.js` (TUT-RF-09) ([tarefas](../specs/003-tutor-da-disciplina/tasks.md))
- `DUV-T05` [H1] Modal de pré-visualização antes do envio, com o aviso de anonimato, em `js/screens/aluno-tutor.js` (DUV-RF-02) ([tarefas](../specs/004-duvidas-ao-professor/tasks.md))
- `QUE-T07` [H3] Botão "Perguntar ao tutor sobre isso" no retorno de cada questão errada em `js/screens/aluno-pratica.js` (QUE-RF-09) ([tarefas](../specs/005-questoes-e-quizzes/tasks.md))
- `REV-T06` [H1] Incluir na revisão do dia as questões aprovadas pelo professor na tela de Questões (REV-RF-01) ([tarefas](../specs/006-revisao-do-dia/tasks.md))

## 001 Acesso e turmas

| Requisito | Descrição | Protótipo | Código do protótipo | Tarefas feitas | Tarefas pendentes |
| --- | --- | --- | --- | --- | --- |
| `ACE-RF-01` | O sistema DEVE permitir a entrada somente com conta institucional, via OpenID Connect. [PRECISA ESCLARECER: Google Workspace ou Microsoft 365] | Simulado | [entrar.js](../js/screens/entrar.js) | ACE-T01 | ACE-T20, ACE-T21 |
| `ACE-RF-02` | O sistema NÃO DEVE criar nem guardar senhas próprias. | Coberto | [entrar.js](../js/screens/entrar.js) | ACE-T01 | ACE-T20, ACE-T21 |
| `ACE-RF-03` | O sistema DEVE atribuir a cada pessoa um ou mais perfis entre aluno, professor, coordenação e administrador, e permitir trocar de perfil sem sair. | Parcial | [shell.js](../js/shell.js) | ACE-T04 | ACE-T22, ACE-T23 |
| `ACE-RF-04` | O sistema DEVE mostrar ao aluno só as disciplinas em que está matriculado e ao professor só as que leciona. | Simulado | [data.js](../js/data.js) |  | ACE-T30, ACE-T31 |
| `ACE-RF-05` | O sistema DEVE verificar no servidor, em toda operação, se a pessoa tem permissão na disciplina envolvida. | Não coberto |  |  | ACE-T30, ACE-T32 |
| `ACE-RF-06` | O sistema DEVE importar disciplinas, turmas e matrículas de um CSV exportado do sistema acadêmico e mostrar um relatório de linhas aceitas e rejeitadas. [PRECISA ESCLARECER: a importação é feita só pela TI ou cada professor também pode importar a própria turma?] | Simulado | [prof-disciplina.js](../js/screens/prof-disciplina.js) | ACE-T05 | ACE-T40, ACE-T41, ACE-T42 |
| `ACE-RF-07` | A importação DEVE ser idempotente: importar o mesmo arquivo duas vezes não duplica registros, e matrículas ausentes no arquivo novo são encerradas. | Não coberto |  |  | ACE-T40, ACE-T41 |
| `ACE-RF-08` | Na primeira entrada e a cada nova versão do aviso, o sistema DEVE mostrar ao aluno o que é registrado, para quê e por quanto tempo, e guardar a data da ciência. | Não coberto |  |  | ACE-T06, ACE-T50, ACE-T51 |
| `ACE-RF-09` | O aluno DEVE poder ver e apagar o próprio histórico de conversas com o tutor. | Não coberto |  |  | ACE-T50, ACE-T52 |
| `ACE-RF-10` | A lista de disciplinas DEVE permitir buscar por nome, filtrar por Todas, Favoritas e Com tutor, marcar favoritas e alternar entre grade e lista. | Coberto | [aluno-disciplinas.js](../js/screens/aluno-disciplinas.js), [aluno-inicio.js](../js/screens/aluno-inicio.js) | ACE-T02, ACE-T03 | ACE-T31, ACE-T33 |
| `ACE-RF-11` | A interface DEVE poder ser instalada na tela inicial do celular como aplicativo web (PWA). | Não coberto |  |  | ACE-T60 |

## 002 Materiais da disciplina

| Requisito | Descrição | Protótipo | Código do protótipo | Tarefas feitas | Tarefas pendentes |
| --- | --- | --- | --- | --- | --- |
| `MAT-RF-01` | O sistema DEVE aceitar somente arquivos PDF e recusar os demais com uma mensagem que explica como exportar slides para PDF. | Coberto | [prof-materiais.js](../js/screens/prof-materiais.js) | MAT-T01 | MAT-T20, MAT-T21 |
| `MAT-RF-02` | Todo material DEVE pertencer a uma disciplina e a uma aula (número e título). | Parcial | [prof-materiais.js](../js/screens/prof-materiais.js) | MAT-T01 | MAT-T20, MAT-T21 |
| `MAT-RF-03` | O processamento DEVE acontecer em segundo plano e mostrar ao professor a etapa atual: Enviando arquivo, Lendo as páginas, Dividindo em trechos, Gerando a busca semântica, Pronto para o tutor. | Simulado | [prof-materiais.js](../js/screens/prof-materiais.js) | MAT-T02 | MAT-T20, MAT-T22, MAT-T24 |
| `MAT-RF-04` | O sistema DEVE extrair o texto página por página e guardar em cada trecho a aula, o arquivo e a página de origem. | Simulado | [data.js](../js/data.js) | MAT-T04 | MAT-T22 |
| `MAT-RF-05` | O sistema DEVE detectar páginas sem texto e marcar como "Precisa de atenção" o material em que a maioria das páginas não tem texto. | Não coberto |  |  | MAT-T40 |
| `MAT-RF-06` | O sistema DEVE avisar o professor quando um material fica pronto ou falha. | Simulado | [prof-materiais.js](../js/screens/prof-materiais.js) | MAT-T02 | MAT-T23 |
| `MAT-RF-07` | Um material só DEVE aparecer para o aluno e ser usado pelo tutor e pelo gerador de questões depois de pronto. | Simulado | [aluno-disciplina.js](../js/screens/aluno-disciplina.js) | MAT-T03 | MAT-T30 |
| `MAT-RF-08` | O aluno DEVE ver os materiais prontos da disciplina, ordenados por aula, e poder abrir cada PDF. | Coberto | [aluno-disciplina.js](../js/screens/aluno-disciplina.js) | MAT-T03 | MAT-T31 |
| `MAT-RF-09` | O sistema DEVE abrir um material numa página específica, com o trecho citado destacado. | Simulado | [ui.js](../js/ui.js) | MAT-T04 | MAT-T31, MAT-T32 |
| `MAT-RF-10` | O professor DEVE poder retirar um material; a partir daí, o tutor e o gerador de questões não o usam mais, e as questões aprovadas que vieram dele ficam marcadas para revisão. | Não coberto |  |  | MAT-T50, MAT-T51 |
| `MAT-RF-11` | O professor DEVE poder enviar uma versão nova de um material, que substitui a anterior quando fica pronta. | Não coberto |  |  | MAT-T52 |

## 003 Tutor da disciplina

| Requisito | Descrição | Protótipo | Código do protótipo | Tarefas feitas | Tarefas pendentes |
| --- | --- | --- | --- | --- | --- |
| `TUT-RF-01` | O tutor DEVE responder somente com base nos trechos de materiais prontos da disciplina selecionada. | Simulado | [tutor.js](../js/tutor.js) | TUT-T02 | TUT-T20, TUT-T21 |
| `TUT-RF-02` | Toda resposta DEVE trazer pelo menos uma citação (aula e página ou slide), que abre o material na página citada com o trecho destacado. | Coberto | [aluno-tutor.js](../js/screens/aluno-tutor.js), [ui.js](../js/ui.js) | TUT-T02 | TUT-T20, TUT-T22, TUT-T24 |
| `TUT-RF-03` | O sistema NÃO DEVE apresentar como resposta nenhuma afirmação sem citação. | Coberto | [tutor.js](../js/tutor.js) | TUT-T02 | TUT-T20, TUT-T22 |
| `TUT-RF-04` | Quando nenhum trecho do material é relevante para a pergunta, o tutor DEVE responder "Não encontrei isso no material da disciplina." e oferecer "Enviar dúvida ao professor", sem chamar o modelo de linguagem. | Simulado | [aluno-tutor.js](../js/screens/aluno-tutor.js), [tutor.js](../js/tutor.js) | TUT-T03 | TUT-T30, TUT-T31 |
| `TUT-RF-05` | Com o modo pistas ligado, quando a pergunta pede a resolução de um exercício, o tutor DEVE responder com pistas em etapas, sem o resultado final, e marcar a resposta com "Modo pistas". | Simulado | [aluno-tutor.js](../js/screens/aluno-tutor.js), [tutor.js](../js/tutor.js) | TUT-T04 | TUT-T40, TUT-T41 |
| `TUT-RF-06` | O professor DEVE poder ligar e desligar o modo pistas por disciplina; o padrão é ligado. | Coberto | [prof-disciplina.js](../js/screens/prof-disciplina.js) | TUT-T04 | TUT-T42 |
| `TUT-RF-07` | O professor DEVE poder pausar o tutor da disciplina imediatamente (modo prova) e agendar janelas de prova com início e fim; durante a pausa, o aluno vê o aviso e não consegue perguntar. | Parcial | [aluno-tutor.js](../js/screens/aluno-tutor.js), [prof-disciplina.js](../js/screens/prof-disciplina.js) | TUT-T05 | TUT-T50, TUT-T51, TUT-T52 |
| `TUT-RF-08` | O sistema DEVE limitar o número de perguntas por aluno, por disciplina e por dia, com valor escolhido pelo professor entre 20, 40 e 60 (padrão 40), zerando à meia-noite no horário de Brasília, e mostrar ao aluno o uso do dia. | Coberto | [aluno-tutor.js](../js/screens/aluno-tutor.js), [prof-disciplina.js](../js/screens/prof-disciplina.js) | TUT-T06 | TUT-T60, TUT-T61 |
| `TUT-RF-09` | O aluno DEVE poder avaliar cada resposta como útil, não útil ou incorreta; respostas marcadas como incorretas entram na fila de revisão da equipe. | Parcial | [aluno-tutor.js](../js/screens/aluno-tutor.js) |  | TUT-T07, TUT-T70 |
| `TUT-RF-10` | O tutor DEVE exibir a política de uso de IA da disciplina, escrita e editável pelo professor. | Coberto | [aluno-tutor.js](../js/screens/aluno-tutor.js), [prof-disciplina.js](../js/screens/prof-disciplina.js) | TUT-T08 | TUT-T80 |
| `TUT-RF-11` | O sistema DEVE remover dados pessoais (nome, e-mail, CPF, telefone) da pergunta antes de enviá-la ao provedor de IA ou registrá-la para análise. | Não coberto |  |  | TUT-T90 |
| `TUT-RF-12` | O histórico de conversa DEVE ser visível só para o próprio aluno; os registros usados no radar e na análise de qualidade DEVEM guardar só um identificador pseudônimo, que permite contar alunos distintos sem revelar quem são. | Simulado | [store.js](../js/store.js) | TUT-T09 | TUT-T91 |
| `TUT-RF-13` | O tutor DEVE mostrar a resposta aos poucos (streaming), à medida que é gerada. | Simulado | [aluno-tutor.js](../js/screens/aluno-tutor.js) | TUT-T01 | TUT-T23 |
| `TUT-RF-14` | O tutor PODE sugerir perguntas iniciais sobre o material da disciplina quando a conversa está vazia. | Coberto | [data.js](../js/data.js), [aluno-tutor.js](../js/screens/aluno-tutor.js) | TUT-T01 | TUT-T25 |

## 004 Dúvidas ao professor

| Requisito | Descrição | Protótipo | Código do protótipo | Tarefas feitas | Tarefas pendentes |
| --- | --- | --- | --- | --- | --- |
| `DUV-RF-01` | O sistema DEVE oferecer "Enviar dúvida ao professor" em toda resposta do tipo "não encontrei" do tutor. | Coberto | [aluno-tutor.js](../js/screens/aluno-tutor.js) | DUV-T01 | DUV-T11 |
| `DUV-RF-02` | Antes do envio, o sistema DEVE mostrar ao aluno o texto que será enviado, já sem dados pessoais, e pedir confirmação. | Não coberto |  |  | DUV-T05, DUV-T10, DUV-T11, DUV-T12 |
| `DUV-RF-03` | A dúvida DEVE chegar ao professor sem nome, RA, e-mail, turma ou horário exato do aluno. | Coberto | [aluno-tutor.js](../js/screens/aluno-tutor.js) | DUV-T01 | DUV-T11, DUV-T20 |
| `DUV-RF-04` | O sistema DEVE impedir o envio repetido da mesma dúvida a partir da mesma mensagem. | Coberto | [aluno-tutor.js](../js/screens/aluno-tutor.js) | DUV-T01 | DUV-T10, DUV-T11 |
| `DUV-RF-05` | O professor DEVE ver as dúvidas da disciplina no radar, da mais recente para a mais antiga, com a marca "Nova" nas que ainda não viu. | Coberto | [prof-radar.js](../js/screens/prof-radar.js) | DUV-T02 | DUV-T21 |
| `DUV-RF-06` | O sistema DEVE avisar o professor de novas dúvidas pelo sino de notificações. | Coberto | [shell.js](../js/shell.js) | DUV-T03 | DUV-T22 |
| `DUV-RF-07` | O professor DEVE poder marcar uma dúvida como respondida em aula e ocultar dúvidas ofensivas. | Parcial | [prof-radar.js](../js/screens/prof-radar.js) | DUV-T04 | DUV-T30 |
| `DUV-RF-08` | O aluno DEVE ver o status da dúvida que enviou (aberta ou respondida em aula). | Não coberto |  |  | DUV-T31 |
| `DUV-RF-09` | As dúvidas abertas da semana DEVEM entrar no resumo semanal por e-mail do professor (spec 007). | Não coberto |  |  | DUV-T90 |

## 005 Questões e quizzes

| Requisito | Descrição | Protótipo | Código do protótipo | Tarefas feitas | Tarefas pendentes |
| --- | --- | --- | --- | --- | --- |
| `QUE-RF-01` | O professor DEVE poder escolher uma aula com material pronto e pedir de 5 a 20 questões. | Parcial | [prof-questoes.js](../js/screens/prof-questoes.js) | QUE-T01, QUE-T06 | QUE-T22 |
| `QUE-RF-02` | O sistema DEVE gerar, em segundo plano, rascunhos de múltipla escolha com 4 alternativas, 1 correta, justificativa e trecho de origem. | Simulado | [data.js](../js/data.js), [prof-questoes.js](../js/screens/prof-questoes.js) | QUE-T01 | QUE-T20, QUE-T21 |
| `QUE-RF-03` | O sistema DEVE descartar automaticamente rascunhos sem trecho de origem válido ou fora do formato. | Não coberto |  |  | QUE-T20, QUE-T21 |
| `QUE-RF-04` | Rascunhos NÃO DEVEM ser visíveis para alunos em nenhuma tela ou rota. | Coberto | [aluno-disciplina.js](../js/screens/aluno-disciplina.js), [aluno-pratica.js](../js/screens/aluno-pratica.js) | QUE-T03 | QUE-T30 |
| `QUE-RF-05` | O professor DEVE poder aprovar, editar ou descartar cada rascunho, e devolver uma questão publicada para pendentes. | Coberto | [prof-questoes.js](../js/screens/prof-questoes.js) | QUE-T02 | QUE-T31, QUE-T32 |
| `QUE-RF-06` | A tela de questões DEVE separar Pendentes, Publicadas e Descartadas, com a contagem de cada uma. | Coberto | [prof-questoes.js](../js/screens/prof-questoes.js) | QUE-T02 | QUE-T31, QUE-T32 |
| `QUE-RF-07` | Uma questão aprovada DEVE entrar no quiz da sua aula e ficar disponível para a revisão do dia (spec 006). | Parcial | [aluno-disciplina.js](../js/screens/aluno-disciplina.js) | QUE-T03 | QUE-T41 |
| `QUE-RF-08` | No quiz, o aluno DEVE receber retorno imediato com acerto ou erro, a alternativa correta, a justificativa e o link para o trecho de origem. | Coberto | [aluno-pratica.js](../js/screens/aluno-pratica.js) | QUE-T04 | QUE-T40, QUE-T41 |
| `QUE-RF-09` | Ao errar, o aluno DEVE ver o botão "Perguntar ao tutor sobre isso", que abre o tutor da disciplina com a questão como contexto. | Parcial | [aluno-pratica.js](../js/screens/aluno-pratica.js) | QUE-T05 | QUE-T07, QUE-T42 |
| `QUE-RF-10` | Ao final do quiz, o sistema DEVE mostrar o total de acertos e os tópicos a revisar. | Coberto | [aluno-pratica.js](../js/screens/aluno-pratica.js) | QUE-T05 | QUE-T42 |
| `QUE-RF-11` | O sistema DEVE registrar cada resposta com o identificador pseudônimo do aluno, para calcular a taxa de acerto por questão e por tópico no radar (spec 007). | Não coberto |  |  | QUE-T41 |

## 006 Revisão do dia

| Requisito | Descrição | Protótipo | Código do protótipo | Tarefas feitas | Tarefas pendentes |
| --- | --- | --- | --- | --- | --- |
| `REV-RF-01` | O sistema DEVE criar um cartão de revisão para cada questão publicada nas disciplinas do aluno. | Simulado | [data.js](../js/data.js), [aluno-pratica.js](../js/screens/aluno-pratica.js) | REV-T01 | REV-T06, REV-T20, REV-T21 |
| `REV-RF-02` | A sessão diária DEVE ter no máximo 10 cartões, priorizando os mais atrasados e os avaliados como difíceis. | Simulado | [aluno-pratica.js](../js/screens/aluno-pratica.js) | REV-T01 | REV-T20, REV-T22, REV-T30 |
| `REV-RF-03` | Depois de cada resposta, o sistema DEVE mostrar se o aluno acertou, a justificativa e o link para o trecho de origem. | Coberto | [aluno-pratica.js](../js/screens/aluno-pratica.js) | REV-T01 | REV-T20, REV-T23 |
| `REV-RF-04` | O aluno DEVE avaliar cada cartão como Difícil, Bom ou Fácil, e o próximo intervalo DEVE ser calculado pelo algoritmo SM-2; uma resposta errada faz o cartão voltar no dia seguinte. | Parcial | [aluno-pratica.js](../js/screens/aluno-pratica.js) | REV-T02 | REV-T11, REV-T30 |
| `REV-RF-05` | O sistema DEVE informar quando cada cartão volta. | Coberto | [aluno-pratica.js](../js/screens/aluno-pratica.js) | REV-T02 | REV-T23 |
| `REV-RF-06` | A tela inicial DEVE mostrar o cartão da revisão do dia com o número de cartões, as disciplinas, o tempo estimado e o progresso de uma sessão em andamento. | Coberto | [aluno-inicio.js](../js/screens/aluno-inicio.js) | REV-T03 | REV-T24 |
| `REV-RF-07` | A tela inicial DEVE mostrar a sequência de revisões dos últimos 7 dias. | Coberto | [aluno-inicio.js](../js/screens/aluno-inicio.js) | REV-T04 | REV-T40 |
| `REV-RF-08` | Uma nova sessão DEVE ficar disponível todo dia às 6h, horário de Brasília. | Simulado | [aluno-pratica.js](../js/screens/aluno-pratica.js) | REV-T05 | REV-T22 |
| `REV-RF-09` | O aluno PODE ligar um lembrete diário, por notificação ou e-mail, no horário que escolher; o padrão é desligado. | Não coberto |  |  | REV-T50 |
| `REV-RF-10` | Ao final da sessão, o sistema DEVE mostrar o número de acertos e atalhos para o tutor nos tópicos errados. | Coberto | [aluno-pratica.js](../js/screens/aluno-pratica.js) | REV-T05 | REV-T23 |

## 007 Radar da turma

| Requisito | Descrição | Protótipo | Código do protótipo | Tarefas feitas | Tarefas pendentes |
| --- | --- | --- | --- | --- | --- |
| `RAD-RF-01` | O radar DEVE ser recalculado todo dia, de madrugada, com os dados da semana corrente. | Simulado | [data.js](../js/data.js) | RAD-T01 | RAD-T21 |
| `RAD-RF-02` | O radar DEVE mostrar os indicadores da semana: alunos ativos e total de matriculados, perguntas ao tutor, acerto médio nos quizzes e dúvidas sem resposta. | Coberto | [prof-radar.js](../js/screens/prof-radar.js) | RAD-T01 | RAD-T40 |
| `RAD-RF-03` | O radar DEVE mostrar até 5 tópicos com mais alunos distintos na semana, cada um com 2 ou 3 perguntas de exemplo e o atalho para o material relacionado. | Coberto | [prof-radar.js](../js/screens/prof-radar.js) | RAD-T02 | RAD-T21 |
| `RAD-RF-04` | Um tópico SÓ DEVE aparecer se vier de pelo menos 5 alunos distintos. | Simulado | [prof-radar.js](../js/screens/prof-radar.js) | RAD-T02 | RAD-T20, RAD-T21 |
| `RAD-RF-05` | As perguntas de exemplo DEVEM passar pela remoção de dados pessoais, e o professor DEVE poder ocultar um exemplo. | Não coberto |  |  | RAD-T22 |
| `RAD-RF-06` | O radar NÃO DEVE exibir nome, RA, e-mail, horário exato ou qualquer contagem por aluno. | Coberto | [prof-radar.js](../js/screens/prof-radar.js) | RAD-T02 | RAD-T24 |
| `RAD-RF-07` | O radar DEVE mostrar a taxa de acerto por tópico e por questão, e só exibir taxas calculadas com pelo menos 5 alunos distintos. | Parcial | [prof-radar.js](../js/screens/prof-radar.js) | RAD-T03 | RAD-T20, RAD-T23 |
| `RAD-RF-08` | O radar DEVE sugerir 3 tópicos para retomar na próxima aula, combinando mais dúvidas e menor acerto. | Coberto | [prof-radar.js](../js/screens/prof-radar.js) | RAD-T04 | RAD-T30 |
| `RAD-RF-09` | O professor DEVE poder escolher a semana exibida entre a atual e as anteriores do semestre. | Coberto | [prof-radar.js](../js/screens/prof-radar.js) | RAD-T01 | RAD-T40 |
| `RAD-RF-10` | Com o resumo semanal ligado, o professor DEVE receber toda segunda-feira, até as 7h, um e-mail com os tópicos sugeridos, os tópicos com mais dúvidas e as dúvidas sem resposta. | Simulado | [prof-disciplina.js](../js/screens/prof-disciplina.js) | RAD-T05 | RAD-T50 |
| `RAD-RF-11` | O radar DEVE oferecer o atalho "Gerar 5 questões de revisão" a partir dos tópicos sugeridos. | Coberto | [prof-radar.js](../js/screens/prof-radar.js) | RAD-T04 | RAD-T31 |
