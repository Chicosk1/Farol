# Especificação: Materiais da disciplina

| Campo | Valor |
| --- | --- |
| Código | `MAT` |
| Branch | `002-materiais-da-disciplina` |
| Status | Em revisão |
| Criada em | 2026-11-13 |
| Origem | Documento de idealização, seções "Princípios do produto" e "Como funciona por dentro" |

## Contexto

O material publicado pelo professor é a única fonte do tutor e do gerador de questões (princípio I da constituição). Publicar precisa ser tão simples quanto subir um PDF, porque o esforço do professor é o maior risco de adesão. Esta spec cobre o envio, o processamento, a consulta pelo aluno e a retirada de materiais.

## Histórias de usuário e testes de aceite

### História 1: Publicar o PDF de uma aula (Prioridade: P1)

Como professor, quero enviar o PDF de uma aula e saber quando ele está pronto, para que o tutor e os quizzes passem a usá-lo.

**Por que esta prioridade:** sem material publicado, nenhuma outra funcionalidade de estudo funciona.

**Teste independente:** enviar um PDF de 30 páginas e ver o status chegar a "Pronto para o tutor".

**Cenários de aceite:**

1. **Dado** um professor na tela de materiais da sua disciplina, **quando** arrasta um PDF ou escolhe o arquivo e informa a aula, **então** o material aparece na lista com a etapa atual do processamento.
2. **Dado** um material em processamento, **quando** cada etapa termina, **então** a lista mostra a etapa seguinte: Enviando arquivo, Lendo as páginas, Dividindo em trechos, Gerando a busca semântica, Pronto para o tutor.
3. **Dado** um material que terminou de processar, **quando** o professor está em qualquer tela, **então** recebe o aviso "Aula N, título, está pronta para o tutor".
4. **Dado** um arquivo que não é PDF, **quando** o professor tenta enviá-lo, **então** vê "Envie um arquivo PDF. Slides podem ser exportados como PDF." e nada é enviado.

### História 2: Consultar os materiais da disciplina (Prioridade: P1)

Como aluno, quero ver os materiais de cada aula e abrir o PDF, inclusive na página exata citada pelo tutor.

**Por que esta prioridade:** a citação só tem valor se o aluno consegue abrir a fonte.

**Teste independente:** abrir um material pela lista e por uma citação, que leva à página certa.

**Cenários de aceite:**

1. **Dado** uma disciplina com 7 materiais prontos, **quando** o aluno abre a disciplina, **então** vê os 7, ordenados por aula, com título e número de páginas.
2. **Dado** um material ainda em processamento, **quando** o aluno abre a disciplina, **então** ele não aparece.
3. **Dado** uma citação "Aula 4, p. 5", **quando** o aluno toca nela, **então** o PDF abre na página 5 com o trecho citado destacado.

### História 3: Avisar quando o PDF não tem texto (Prioridade: P2)

Como professor, quero ser avisado se o PDF é escaneado ou não tem texto selecionável, para enviar outra versão.

**Teste independente:** enviar um PDF só com imagens e ver o aviso.

**Cenários de aceite:**

1. **Dado** um PDF em que a maioria das páginas não tem texto, **quando** o processamento termina, **então** o material fica com o status "Precisa de atenção" e a mensagem explica que o tutor não consegue ler páginas escaneadas.
2. **Dado** um PDF com algumas páginas sem texto, **quando** o processamento termina, **então** o material fica pronto, e o professor vê quais páginas foram ignoradas.

### História 4: Retirar ou substituir um material (Prioridade: P2)

Como professor, quero retirar um material ou trocar por uma versão corrigida, e ter certeza de que o tutor para de usar o antigo.

**Teste independente:** retirar um material e fazer ao tutor uma pergunta que só ele respondia.

**Cenários de aceite:**

1. **Dado** um material publicado, **quando** o professor o retira, **então** ele some da lista do aluno e o tutor deixa de usá-lo na próxima pergunta.
2. **Dado** um material publicado, **quando** o professor envia uma versão nova dele, **então** a versão antiga continua em uso até a nova ficar pronta, e depois é substituída.
3. **Dado** questões aprovadas que vieram de um material retirado, **quando** a retirada acontece, **então** essas questões aparecem para o professor marcadas "Origem retirada", para ele decidir se mantém.

### Casos de borda

- PDF protegido por senha: o envio é recusado com uma mensagem clara.
- PDF muito grande: [PRECISA ESCLARECER: tamanho máximo do arquivo; sugestão inicial de 50 MB e 300 páginas]
- Dois professores na mesma disciplina enviando ao mesmo tempo: os dois materiais são processados, cada um na sua aula.
- Falha no processamento (por exemplo, provedor de embeddings fora do ar): o material fica com "Erro, tente de novo", e o professor pode reenviar sem perder o arquivo.
- Citações antigas no histórico do aluno apontando para um material substituído: [PRECISA ESCLARECER: abrir a versão antiga, guardada como arquivo morto, ou a versão nova?]

## Requisitos

### Requisitos funcionais

- **MAT-RF-01**: O sistema DEVE aceitar somente arquivos PDF e recusar os demais com uma mensagem que explica como exportar slides para PDF.
- **MAT-RF-02**: Todo material DEVE pertencer a uma disciplina e a uma aula (número e título).
- **MAT-RF-03**: O processamento DEVE acontecer em segundo plano e mostrar ao professor a etapa atual: Enviando arquivo, Lendo as páginas, Dividindo em trechos, Gerando a busca semântica, Pronto para o tutor.
- **MAT-RF-04**: O sistema DEVE extrair o texto página por página e guardar em cada trecho a aula, o arquivo e a página de origem.
- **MAT-RF-05**: O sistema DEVE detectar páginas sem texto e marcar como "Precisa de atenção" o material em que a maioria das páginas não tem texto.
- **MAT-RF-06**: O sistema DEVE avisar o professor quando um material fica pronto ou falha.
- **MAT-RF-07**: Um material só DEVE aparecer para o aluno e ser usado pelo tutor e pelo gerador de questões depois de pronto.
- **MAT-RF-08**: O aluno DEVE ver os materiais prontos da disciplina, ordenados por aula, e poder abrir cada PDF.
- **MAT-RF-09**: O sistema DEVE abrir um material numa página específica, com o trecho citado destacado.
- **MAT-RF-10**: O professor DEVE poder retirar um material; a partir daí, o tutor e o gerador de questões não o usam mais, e as questões aprovadas que vieram dele ficam marcadas para revisão.
- **MAT-RF-11**: O professor DEVE poder enviar uma versão nova de um material, que substitui a anterior quando fica pronta.

### Requisitos não funcionais

- **MAT-RNF-01**: Um PDF de 40 páginas com texto fica pronto em até 2 minutos.
- **MAT-RNF-02**: Só o professor da disciplina e a administração podem enviar ou retirar materiais.
- **MAT-RNF-03**: Os arquivos ficam armazenados na região de São Paulo.

### Entidades principais

- **Material**: disciplina, aula (número e título), arquivo, número de páginas, status (processando, pronto, precisa de atenção, erro, retirado), versão.
- **Trecho**: material, página, texto, posição na página, vetor de busca.

## Critérios de sucesso

- **MAT-CS-01**: O professor publica um material em até 2 minutos de esforço próprio (escolher arquivo, informar aula, confirmar).
- **MAT-CS-02**: 95% dos PDFs com texto enviados no piloto ficam prontos sem erro na primeira tentativa.
- **MAT-CS-03**: Em 100% dos testes, um material retirado deixa de ser usado pelo tutor na pergunta seguinte.

## Fora do escopo

- OCR de PDFs escaneados e leitura direta de PPTX (expansão).
- Vídeos e transcrição de aulas gravadas (expansão).
- Edição do conteúdo do PDF dentro do Farol.

## Questões em aberto

| Questão | Dono | Prazo |
| --- | --- | --- |
| Tamanho máximo do arquivo e número máximo de páginas | Equipe técnica | Antes do plano final |
| O que a citação antiga abre depois de uma substituição | Dono do produto | Antes do plano final |

## Histórico

| Data | Mudança |
| --- | --- |
| 2026-11-13 | Criação da spec a partir da idealização e do protótipo |
