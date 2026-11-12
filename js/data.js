/* Farol — dados fictícios do protótipo (curso de Sistemas de Informação).
   Nenhum nome, número ou conteúdo aqui é real. Para trocar o cenário da demonstração, edite este arquivo. */
(function () {
  'use strict';
  const F = (window.Farol = window.Farol || {});

  const curso = { nome: 'Bacharelado em Sistemas de Informação', turma: 'SINF2NA', periodo: '2º período' };

  const pessoas = {
    aluno: { nome: 'Ana Souza', iniciais: 'AS', descricao: `${curso.periodo}, turma ${curso.turma}` },
    professor: { nome: 'Carlos Mendes', iniciais: 'CM', descricao: 'Estruturas de Dados, turma SINF2NA' },
  };

  const disciplinas = [
    { id: 'ed', nome: 'Estruturas de Dados', codigo: 'SINF2NA', professor: 'Prof. Carlos Mendes', icone: 'binary-tree', progresso: 62, tutor: true, novidade: '2 questões novas' },
    { id: 'bd1', nome: 'Banco de Dados I', codigo: 'SINF2NA', professor: 'Prof.ª Marta Ribeiro', icone: 'database', progresso: 70, tutor: true, novidade: 'Aula nova' },
    { id: 'poo', nome: 'Programação Orientada a Objetos', codigo: 'SINF2NA', professor: 'Prof. João Pereira', icone: 'code', progresso: 55, tutor: false },
    { id: 'md', nome: 'Matemática Discreta', codigo: 'SINF2NA', professor: 'Prof.ª Luciana Alves', icone: 'math-symbols', progresso: 48, tutor: false },
    { id: 'calc', nome: 'Cálculo Diferencial e Integral', codigo: 'SINF2NA', professor: 'Prof. Rogério Lima', icone: 'math-function', progresso: 51, tutor: false },
    { id: 'es1', nome: 'Engenharia de Software I', codigo: 'SINF2NA', professor: 'Prof. Paulo Nunes', icone: 'git-branch', progresso: 66, tutor: false },
  ].map((d) => Object.assign({ inicio: '20/07/2026', fim: '31/12/2026' }, d));

  /* Materiais publicados (PDFs). status: pronto | processando */
  const materiais = [
    { id: 'ed-a1', disciplina: 'ed', aula: 1, titulo: 'Introdução e análise de complexidade', paginas: 18, enviadoEm: '22/07/2026', status: 'pronto' },
    { id: 'ed-a2', disciplina: 'ed', aula: 2, titulo: 'Vetores e busca binária', paginas: 22, enviadoEm: '05/08/2026', status: 'pronto' },
    { id: 'ed-a3', disciplina: 'ed', aula: 3, titulo: 'Recursão', paginas: 16, enviadoEm: '19/08/2026', status: 'pronto' },
    { id: 'ed-a4', disciplina: 'ed', aula: 4, titulo: 'Listas encadeadas', paginas: 24, enviadoEm: '02/09/2026', status: 'pronto' },
    { id: 'ed-a5', disciplina: 'ed', aula: 5, titulo: 'Pilhas e filas', paginas: 20, enviadoEm: '23/09/2026', status: 'pronto' },
    { id: 'ed-a6', disciplina: 'ed', aula: 6, titulo: 'Árvores binárias', paginas: 26, enviadoEm: '21/10/2026', status: 'pronto' },
    { id: 'ed-a7', disciplina: 'ed', aula: 7, titulo: 'Árvores AVL', paginas: 28, enviadoEm: 'hoje', status: 'processando', etapa: 1 },
    { id: 'bd-a3', disciplina: 'bd1', aula: 3, titulo: 'Modelo relacional e chaves', paginas: 20, enviadoEm: '12/08/2026', status: 'pronto' },
    { id: 'bd-a5', disciplina: 'bd1', aula: 5, titulo: 'Normalização', paginas: 18, enviadoEm: '09/09/2026', status: 'pronto' },
    { id: 'bd-a7', disciplina: 'bd1', aula: 7, titulo: 'Consultas com JOIN', paginas: 22, enviadoEm: '10/11/2026', status: 'pronto' },
  ];

  /* Trechos dos PDFs que o tutor cita. A chave é o identificador da citação. */
  const citations = {
    'ed-a1-p9': {
      materialId: 'ed-a1', page: 9, heading: 'Notação O',
      before: 'Para comparar algoritmos, observamos como o número de passos cresce quando a entrada cresce.',
      excerpt: 'A notação O descreve o crescimento do tempo de execução ignorando constantes: O(1) não depende do tamanho da entrada, O(n) cresce junto com ela e O(n²) aparece, por exemplo, em dois laços aninhados sobre os mesmos dados.',
      code: 'for (i = 0; i < n; i++)\n    for (j = 0; j < n; j++)\n        soma += v[i] * v[j];   // n * n passos: O(n²)',
    },
    'ed-a2-p12': {
      materialId: 'ed-a2', page: 12, heading: 'Busca binária',
      before: 'A busca binária exige que o vetor esteja ordenado.',
      excerpt: 'A cada comparação com o elemento do meio, metade do vetor é descartada. Com n elementos, o número de passos é quantas vezes dá para dividir n por 2 até sobrar um: log de n na base 2. Por isso a busca binária é O(log n).',
      after: 'Exemplo: em um vetor com 1.000.000 de elementos, bastam cerca de 20 comparações.',
    },
    'ed-a3-p4': {
      materialId: 'ed-a3', page: 4, heading: 'Caso base e passo recursivo',
      excerpt: 'Toda função recursiva precisa de um caso base, que encerra as chamadas, e de um passo recursivo, que resolve um problema menor. Sem caso base, as chamadas se acumulam na pilha de execução até estourar.',
      code: 'int fatorial(int n) {\n    if (n == 0) return 1;          // caso base\n    return n * fatorial(n - 1);   // passo recursivo\n}',
    },
    'ed-a4-p2': {
      materialId: 'ed-a4', page: 2, heading: 'Vetor ou lista encadeada?',
      excerpt: 'No vetor, os elementos ficam lado a lado na memória: acessar a posição i custa O(1), mas inserir no meio exige deslocar elementos. Na lista encadeada, inserir e remover é simples, mas acessar a posição i exige percorrer a lista desde o início: O(n).',
      after: 'A escolha depende da operação que o programa faz com mais frequência.',
    },
    'ed-a4-p5': {
      materialId: 'ed-a4', page: 5, heading: 'Nós e ponteiros',
      before: 'Cada elemento da lista é guardado em um nó.',
      excerpt: 'Um nó guarda o valor e um ponteiro para o próximo nó. A lista só precisa saber onde está o primeiro nó; o último aponta para NULL. Inserir ou remover no início custa O(1).',
      code: 'typedef struct No {\n    int valor;\n    struct No *proximo;\n} No;',
    },
    'ed-a5-p3': {
      materialId: 'ed-a5', page: 3, heading: 'Pilha (LIFO)',
      excerpt: 'Na pilha, o último elemento a entrar é o primeiro a sair. As operações push (empilhar) e pop (desempilhar) acontecem sempre no topo e custam O(1). Fazer pop em uma pilha vazia deve sinalizar erro.',
      after: 'Exemplos: o botão desfazer de um editor e a pilha de chamadas de função.',
    },
    'ed-a5-p11': {
      materialId: 'ed-a5', page: 11, heading: 'Fila (FIFO)',
      excerpt: 'Na fila, o primeiro elemento a entrar é o primeiro a sair. Inserimos no fim e removemos do início. Com uma lista encadeada que guarda ponteiros para o início e para o fim, as duas operações custam O(1).',
      after: 'Exemplo: pedidos de impressão atendidos na ordem de chegada.',
    },
    'ed-a6-p8': {
      materialId: 'ed-a6', page: 8, heading: 'Percursos',
      before: 'Em uma árvore binária, cada nó tem no máximo dois filhos.',
      excerpt: 'No percurso em ordem, visitamos a subárvore esquerda, depois o nó e depois a subárvore direita. Em uma árvore binária de busca, esse percurso devolve os valores em ordem crescente.',
    },
    'bd-a3-p6': {
      materialId: 'bd-a3', page: 6, heading: 'Chaves',
      excerpt: 'A chave primária identifica cada linha de forma única e não pode ser nula. A chave estrangeira é uma coluna que referencia a chave primária de outra tabela e garante que a referência exista.',
      code: 'CREATE TABLE matricula (\n  id INT PRIMARY KEY,\n  aluno_id INT REFERENCES aluno(id)\n);',
    },
    'bd-a5-p4': {
      materialId: 'bd-a5', page: 4, heading: 'Primeira forma normal',
      excerpt: 'Normalizar é organizar as tabelas para evitar redundância e anomalias de atualização. Na primeira forma normal, cada coluna guarda um único valor atômico e não há grupos repetidos.',
    },
    'bd-a7-p10': {
      materialId: 'bd-a7', page: 10, heading: 'INNER JOIN e LEFT JOIN',
      excerpt: 'O INNER JOIN traz apenas as linhas que têm correspondência nas duas tabelas. O LEFT JOIN traz todas as linhas da tabela da esquerda, mesmo sem correspondência na outra.',
      code: 'SELECT a.nome, m.disciplina\nFROM aluno a\nINNER JOIN matricula m ON m.aluno_id = a.id;',
    },
  };

  /* Base de conhecimento do tutor simulado. Cada entrada responde a perguntas com essas palavras-chave.
     "pistas" é a versão usada quando o aluno pede a resposta de um exercício e o modo pistas está ligado. */
  const tutor = {
    ed: [
      {
        keys: ['lista encadeada', 'listas encadeadas', 'lista ligada', 'ponteiro', 'proximo no', 'nos da lista', 'encadead'],
        resposta: 'Uma lista encadeada guarda cada elemento em um nó, e cada nó aponta para o próximo. Por isso os elementos não precisam ficar lado a lado na memória, como no vetor. Inserir ou remover no início custa O(1), mas chegar ao k-ésimo elemento exige percorrer a lista.',
        pistas: 'Antes do código, desenhe três nós com setas. Para inserir no início: crie o novo nó, faça ele apontar para o primeiro atual e só então atualize o início da lista. Se você trocar a ordem dos dois últimos passos, o que acontece com o resto da lista?',
        cite: 'ed-a4-p5',
      },
      {
        keys: ['busca binaria', 'log n', 'logaritm', 'metade do vetor', 'vetor ordenado'],
        resposta: 'A busca binária só funciona em vetor ordenado. A cada comparação com o elemento do meio, ela descarta metade do que falta. Com n elementos, o número de passos é quantas vezes dá para dividir n por 2 até sobrar um, ou seja, log de n na base 2. Com 1.000.000 de elementos, são cerca de 20 comparações.',
        pistas: 'Pense em um vetor com 16 elementos. Depois da primeira comparação, quantos sobram? E depois da segunda? Quantas comparações até sobrar um só? Agora compare esse número com 16.',
        cite: 'ed-a2-p12',
      },
      {
        keys: ['pilha', 'lifo', 'push', 'pop', 'empilha', 'desempilha', 'topo'],
        resposta: 'Pilha é uma estrutura LIFO: o último a entrar é o primeiro a sair. As operações push (empilhar) e pop (desempilhar) acontecem sempre no topo e custam O(1). O botão desfazer de um editor é um bom exemplo.',
        pistas: 'Simule à mão: empilhe 1, 2 e 3 e depois faça dois pops. Quem fica no topo? Agora pense no código: que informação você precisa guardar para saber onde está o topo, e o que fazer quando a pilha estiver vazia?',
        cite: 'ed-a5-p3',
      },
      {
        keys: ['fila', 'filas', 'fifo', 'enfileira', 'desenfileira', 'queue'],
        resposta: 'Fila é FIFO: o primeiro a entrar é o primeiro a sair, como a fila do restaurante universitário. Inserimos no fim e removemos do início. Com uma lista encadeada que guarda ponteiros para o início e o fim, as duas operações custam O(1).',
        pistas: 'Desenhe uma fila com três pessoas e numere a ordem de chegada. Onde entra a quarta? Quem sai primeiro? Agora: quais dois ponteiros a sua estrutura precisa manter para as duas operações serem rápidas?',
        cite: 'ed-a5-p11',
      },
      {
        keys: ['recursao', 'recursiva', 'recursivo', 'caso base', 'fatorial', 'fibonacci', 'chama ela mesma'],
        resposta: 'Uma função recursiva resolve um problema chamando a si mesma em uma versão menor dele. Ela precisa de um caso base, que encerra as chamadas, e de um passo recursivo, que se aproxima do caso base. Sem caso base, as chamadas se acumulam até estourar a pilha de execução.',
        pistas: 'Para o fatorial: qual é o menor n em que você sabe a resposta sem calcular nada? Esse é o caso base. Depois escreva fatorial(n) usando fatorial(n − 1). O que acontece se o caso base faltar?',
        cite: 'ed-a3-p4',
      },
      {
        keys: ['complexidade', 'big o', 'notacao o', 'o(n)', 'o(1)', 'o(n2)', 'assintot', 'eficiencia'],
        resposta: 'A notação O descreve como o tempo de um algoritmo cresce quando a entrada cresce, ignorando constantes. O(1) não depende do tamanho; O(n) cresce junto com a entrada; O(n²) aparece, por exemplo, em dois laços aninhados sobre os mesmos dados.',
        pistas: 'Conte quantas vezes a linha mais interna do seu código executa quando n vale 10. E quando vale 20? Se dobrou, o crescimento é linear; se quadruplicou, é quadrático.',
        cite: 'ed-a1-p9',
      },
      {
        keys: ['arvore', 'arvores', 'binaria', 'percurso', 'em ordem', 'pre ordem', 'pos ordem', 'raiz', 'folha'],
        resposta: 'Uma árvore binária tem nós com no máximo dois filhos. No percurso em ordem, você visita a subárvore esquerda, depois o nó e depois a direita. Em uma árvore binária de busca, esse percurso devolve os valores em ordem crescente.',
        pistas: 'Desenhe uma árvore com a raiz 8, os filhos 3 e 10 e o neto 6 à direita do 3. Faça o percurso em ordem com o dedo: esquerda, nó, direita. Que sequência sai?',
        cite: 'ed-a6-p8',
      },
      {
        keys: ['diferenca entre vetor', 'vetor e lista', 'vetor ou lista', 'array', 'lista ou vetor'],
        resposta: 'No vetor, os elementos ficam lado a lado na memória: acessar a posição i é imediato, mas inserir no meio exige deslocar elementos. Na lista encadeada, inserir e remover é simples, mas acessar a posição i exige percorrer a lista. A escolha depende da operação que o programa mais faz.',
        pistas: 'Liste as operações que o seu programa faz com mais frequência: acessar por posição, inserir no meio ou remover. Para cada uma, qual estrutura sai mais barata?',
        cite: 'ed-a4-p2',
      },
    ],
    bd1: [
      {
        keys: ['chave primaria', 'chave estrangeira', 'primary key', 'foreign key', 'chave'],
        resposta: 'A chave primária identifica cada linha de uma tabela de forma única e não pode ser nula. A chave estrangeira é uma coluna que aponta para a chave primária de outra tabela e garante que a referência exista.',
        pistas: 'Na tabela de matrículas, qual coluna diz de qual aluno é a matrícula? Ela precisa existir na tabela de alunos? Então que tipo de chave ela é?',
        cite: 'bd-a3-p6',
      },
      {
        keys: ['normaliza', '1fn', '2fn', '3fn', 'forma normal', 'redundan'],
        resposta: 'Normalizar é organizar as tabelas para evitar redundância e anomalias de atualização. Na primeira forma normal, cada coluna guarda um único valor atômico e não há grupos repetidos.',
        pistas: 'Olhe para a sua tabela: alguma coluna guarda mais de um valor, como uma lista de telefones? Esse é o primeiro ponto a resolver.',
        cite: 'bd-a5-p4',
      },
      {
        keys: ['join', 'juncao', 'inner join', 'left join'],
        resposta: 'O JOIN combina linhas de duas tabelas a partir de uma condição, em geral a chave estrangeira igual à chave primária. O INNER JOIN traz só as linhas com correspondência nos dois lados; o LEFT JOIN traz todas as da tabela da esquerda, mesmo sem correspondência.',
        pistas: 'Pense em um aluno que ainda não tem matrícula. Ele deve aparecer no resultado? Se sim, qual dos dois JOINs você precisa?',
        cite: 'bd-a7-p10',
      },
    ],
  };

  const sugestoesTutor = {
    ed: ['O que é uma lista encadeada?', 'Por que a busca binária é O(log n)?', 'Me dá a resposta do exercício de pilha', 'Isso cai na prova?'],
    bd1: ['Qual a diferença entre chave primária e estrangeira?', 'Quando usar LEFT JOIN?', 'O que é a primeira forma normal?'],
  };

  /* Cartões da revisão do dia (repetição espaçada). */
  const revisao = [
    { disciplina: 'ed', topico: 'Pilhas e filas', pergunta: 'Qual estrutura segue a regra "o último a entrar é o primeiro a sair"?', opcoes: ['Fila', 'Pilha', 'Lista encadeada', 'Árvore binária'], correta: 1, justificativa: 'Pilha é LIFO: push e pop acontecem sempre no topo.', cite: 'ed-a5-p3' },
    { disciplina: 'ed', topico: 'Busca binária', pergunta: 'Qual a complexidade da busca binária em um vetor ordenado com n elementos?', opcoes: ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], correta: 1, justificativa: 'Cada comparação descarta metade do vetor.', cite: 'ed-a2-p12' },
    { disciplina: 'ed', topico: 'Listas encadeadas', pergunta: 'Em uma lista encadeada simples, qual operação custa O(1)?', opcoes: ['Acessar o k-ésimo elemento', 'Inserir no início', 'Buscar um valor', 'Inserir no fim sem ponteiro para o fim'], correta: 1, justificativa: 'Basta criar o nó, apontá-lo para o primeiro e atualizar o início.', cite: 'ed-a4-p5' },
    { disciplina: 'ed', topico: 'Recursão', pergunta: 'O que acontece com uma função recursiva sem caso base?', opcoes: ['Retorna zero', 'Executa uma única vez', 'Chama a si mesma até estourar a pilha de execução', 'O compilador corrige sozinho'], correta: 2, justificativa: 'Sem caso base, nada encerra as chamadas.', cite: 'ed-a3-p4' },
    { disciplina: 'bd1', topico: 'Chaves', pergunta: 'Qual é a função da chave estrangeira?', opcoes: ['Identificar cada linha de forma única', 'Garantir que a referência a outra tabela exista', 'Ordenar os registros', 'Impedir valores repetidos na coluna'], correta: 1, justificativa: 'Ela referencia a chave primária de outra tabela.', cite: 'bd-a3-p6' },
    { disciplina: 'ed', topico: 'Árvores binárias', pergunta: 'O percurso em ordem de uma árvore binária de busca devolve os valores…', opcoes: ['Na ordem de inserção', 'Em ordem crescente', 'Em ordem decrescente', 'Por nível'], correta: 1, justificativa: 'Esquerda, nó, direita: do menor para o maior.', cite: 'ed-a6-p8' },
    { disciplina: 'ed', topico: 'Complexidade', pergunta: 'Dois laços aninhados percorrendo os mesmos n elementos resultam, em geral, em:', opcoes: ['O(n)', 'O(log n)', 'O(n²)', 'O(2n)'], correta: 2, justificativa: 'São n passos para cada um dos n elementos.', cite: 'ed-a1-p9' },
    { disciplina: 'bd1', topico: 'JOIN', pergunta: 'O INNER JOIN entre Alunos e Matrículas retorna…', opcoes: ['Todos os alunos, mesmo sem matrícula', 'Só alunos com pelo menos uma matrícula', 'Só matrículas sem aluno', 'Todas as combinações possíveis'], correta: 1, justificativa: 'O INNER JOIN só traz linhas com correspondência nos dois lados.', cite: 'bd-a7-p10' },
  ];

  /* Rascunhos de questões gerados pela IA (painel do professor). status: pendente | aprovada | descartada */
  const rascunhos = [
    { id: 'q1', material: 'ed-a5', pergunta: 'Em qual situação uma fila é mais adequada que uma pilha?', opcoes: ['Desfazer a última ação de um editor', 'Atender pedidos de impressão na ordem de chegada', 'Verificar se parênteses estão balanceados', 'Avaliar uma expressão pós-fixa'], correta: 1, justificativa: 'Fila é FIFO: o primeiro pedido que chega é o primeiro atendido.', cite: 'ed-a5-p11', status: 'aprovada' },
    { id: 'q2', material: 'ed-a5', pergunta: 'Depois de push(4), push(7), pop() e push(2), qual elemento está no topo?', opcoes: ['4', '7', '2', 'A pilha está vazia'], correta: 2, justificativa: 'O pop remove o 7; o push seguinte coloca o 2 no topo.', cite: 'ed-a5-p3', status: 'aprovada' },
    { id: 'q3', material: 'ed-a5', pergunta: 'Qual é o custo de inserir no fim de uma fila implementada com lista encadeada que guarda ponteiro para o fim?', opcoes: ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], correta: 0, justificativa: 'Com o ponteiro para o fim, não é preciso percorrer a lista.', cite: 'ed-a5-p11', status: 'pendente' },
    { id: 'q4', material: 'ed-a5', pergunta: 'Qual estrutura controla as chamadas de função durante a execução de um programa?', opcoes: ['Fila', 'Pilha', 'Árvore', 'Tabela hash'], correta: 1, justificativa: 'A última função chamada é a primeira a terminar.', cite: 'ed-a5-p3', status: 'pendente' },
    { id: 'q5', material: 'ed-a5', pergunta: 'Segundo a implementação vista em aula, o que deve acontecer em um pop com a pilha vazia?', opcoes: ['Retornar o último elemento removido', 'Sinalizar erro de pilha vazia', 'Inserir um elemento nulo', 'Reiniciar a pilha'], correta: 1, justificativa: 'O material pede que a operação sinalize erro.', cite: 'ed-a5-p3', status: 'pendente' },
    { id: 'q6', material: 'ed-a5', pergunta: 'Pilhas e filas são:', opcoes: ['Estruturas lineares', 'Bancos de dados', 'Linguagens de programação', 'Sistemas operacionais'], correta: 0, justificativa: 'As duas organizam elementos em sequência.', cite: 'ed-a5-p3', status: 'pendente' },
  ];

  /* Questões que a "IA" pode gerar no protótipo, por aula. */
  const bancoGeracao = {
    'ed-a1': [
      { pergunta: 'Um laço que percorre um vetor de n posições uma única vez tem complexidade:', opcoes: ['O(1)', 'O(n)', 'O(n²)', 'O(log n)'], correta: 1, justificativa: 'Um passo para cada uma das n posições.', cite: 'ed-a1-p9' },
      { pergunta: 'Por que a notação O ignora constantes?', opcoes: ['Porque constantes são sempre zero', 'Porque interessa o crescimento quando a entrada fica grande', 'Porque o compilador remove constantes', 'Porque só vale para vetores'], correta: 1, justificativa: 'Para entradas grandes, o formato do crescimento domina.', cite: 'ed-a1-p9' },
    ],
    'ed-a2': [
      { pergunta: 'Qual pré-condição a busca binária exige?', opcoes: ['Vetor com tamanho par', 'Vetor ordenado', 'Elementos distintos', 'Lista encadeada'], correta: 1, justificativa: 'Sem ordenação, não dá para descartar metade do vetor.', cite: 'ed-a2-p12' },
    ],
    'ed-a3': [
      { pergunta: 'Qual é o caso base da função fatorial(n) vista em aula?', opcoes: ['n == 0 retorna 1', 'n == 1 retorna 0', 'n < 0 retorna n', 'Não há caso base'], correta: 0, justificativa: 'fatorial(0) = 1 encerra as chamadas.', cite: 'ed-a3-p4' },
      { pergunta: 'Quantas chamadas fatorial(4) faz, contando a primeira, até chegar a n == 0?', opcoes: ['3', '4', '5', '24'], correta: 2, justificativa: 'fatorial(4), (3), (2), (1) e (0): cinco chamadas.', cite: 'ed-a3-p4' },
    ],
    'ed-a4': [
      { pergunta: 'Para remover o primeiro nó de uma lista encadeada, o que precisa ser atualizado?', opcoes: ['O ponteiro de início', 'Todos os nós', 'O último nó', 'Nada'], correta: 0, justificativa: 'O início passa a apontar para o segundo nó.', cite: 'ed-a4-p5' },
      { pergunta: 'Por que acessar o 10º elemento de uma lista encadeada custa O(n)?', opcoes: ['Porque é preciso percorrer os nós desde o início', 'Porque os nós ficam ordenados', 'Porque a lista é copiada', 'Porque o vetor é maior'], correta: 0, justificativa: 'Não há acesso direto por posição.', cite: 'ed-a4-p2' },
    ],
    'ed-a5': [
      { pergunta: 'Quais operações de uma pilha acontecem no topo?', opcoes: ['Só push', 'Só pop', 'Push e pop', 'Nenhuma'], correta: 2, justificativa: 'As duas operações trabalham sempre no topo.', cite: 'ed-a5-p3' },
    ],
    'ed-a6': [
      { pergunta: 'Quantos filhos, no máximo, tem um nó de árvore binária?', opcoes: ['1', '2', '3', 'Ilimitados'], correta: 1, justificativa: 'Por definição, no máximo dois: esquerdo e direito.', cite: 'ed-a6-p8' },
    ],
  };

  /* Radar da turma: duas semanas para a troca de período funcionar. */
  const radar = {
    s17: {
      rotulo: 'Semana 17 · 9 a 15/11/2026', ativos: 38, total: 46, perguntas: 214, acerto: 61,
      duvidas: [
        { topico: 'Ponteiros e listas encadeadas', material: 'ed-a4', alunos: 21, exemplos: ['por que a lista perde os nós quando eu insiro no meio?', 'quando eu preciso de ponteiro para o anterior?', 'qual a diferença entre lista e vetor na prática?'] },
        { topico: 'Recursão', material: 'ed-a3', alunos: 17, exemplos: ['como eu sei qual é o caso base?', 'por que meu fatorial dá stack overflow?'] },
        { topico: 'Pilhas e filas', material: 'ed-a5', alunos: 12, exemplos: ['pop em pilha vazia retorna o quê?', 'fila circular é a mesma coisa que fila?'] },
        { topico: 'Complexidade (Big-O)', material: 'ed-a1', alunos: 9, exemplos: ['dois for um dentro do outro é sempre O(n²)?'] },
        { topico: 'Árvores binárias', material: 'ed-a6', alunos: 6, exemplos: ['qual a diferença entre pré-ordem e em ordem?'] },
      ],
      acertoTopicos: [
        { topico: 'Recursão', taxa: 42 },
        { topico: 'Ponteiros e listas encadeadas', taxa: 49 },
        { topico: 'Complexidade (Big-O)', taxa: 63 },
        { topico: 'Pilhas e filas', taxa: 78 },
        { topico: 'Árvores binárias', taxa: 81 },
      ],
    },
    s16: {
      rotulo: 'Semana 16 · 2 a 8/11/2026', ativos: 35, total: 46, perguntas: 176, acerto: 58,
      duvidas: [
        { topico: 'Pilhas e filas', material: 'ed-a5', alunos: 19, exemplos: ['qual a diferença entre pilha e fila?', 'como implementar fila com vetor?'] },
        { topico: 'Recursão', material: 'ed-a3', alunos: 14, exemplos: ['recursão é mais lenta que laço?'] },
        { topico: 'Ponteiros e listas encadeadas', material: 'ed-a4', alunos: 11, exemplos: ['o que é NULL no último nó?'] },
        { topico: 'Busca binária', material: 'ed-a2', alunos: 7, exemplos: ['por que precisa estar ordenado?'] },
      ],
      acertoTopicos: [
        { topico: 'Recursão', taxa: 47 },
        { topico: 'Pilhas e filas', taxa: 52 },
        { topico: 'Ponteiros e listas encadeadas', taxa: 55 },
        { topico: 'Busca binária', taxa: 74 },
      ],
    },
  };

  const duvidasIniciais = [
    { id: 'd1', texto: 'Qual a diferença entre lista duplamente encadeada e lista circular?', quando: 'ontem, 22h15', status: 'aberta' },
    { id: 'd2', texto: 'Vai ter aula de revisão antes da prova?', quando: 'ontem, 21h40', status: 'aberta' },
    { id: 'd3', texto: 'Os slides de árvores AVL já estão disponíveis?', quando: 'hoje, 07h10', status: 'aberta' },
    { id: 'd4', texto: 'Posso implementar a pilha em Python no trabalho?', quando: '10/11, 23h02', status: 'aberta' },
    { id: 'd5', texto: 'O conteúdo de recursão cai na segunda prova?', quando: '10/11, 19h30', status: 'aberta' },
  ];

  const configuracaoInicial = {
    ed: {
      pistas: true,
      prova: false,
      limite: 40,
      resumo: true,
      politica: 'Use o tutor para entender o conteúdo e revisar. Em exercícios avaliativos, ele dá pistas em vez de respostas. Durante as provas, o tutor fica desligado.',
    },
    bd1: { pistas: true, prova: false, limite: 40, resumo: true, politica: 'Use o tutor para tirar dúvidas sobre o material da disciplina.' },
  };

  const novidadesAluno = [
    { icone: 'list-check', texto: 'Prof. Carlos aprovou 2 questões novas da Aula 5 de Estruturas de Dados.', quando: 'hoje, 08h05' },
    { icone: 'file-text', texto: 'Material novo em Banco de Dados I: Aula 7, Consultas com JOIN.', quando: '10/11' },
    { icone: 'cards', texto: 'Sua revisão do dia está pronta: 8 cartões.', quando: 'hoje, 06h00' },
  ];

  F.data = {
    curso,
    pessoas,
    disciplinas,
    materiais,
    citations,
    tutor,
    sugestoesTutor,
    revisao,
    rascunhos,
    bancoGeracao,
    radar,
    duvidasIniciais,
    configuracaoInicial,
    novidadesAluno,
    etapasProcessamento: ['Enviando arquivo', 'Lendo as páginas', 'Dividindo em trechos', 'Gerando a busca semântica', 'Pronto para o tutor'],
    disciplineById: (id) => disciplinas.find((d) => d.id === id),
    materialById: (id) => (F.store ? F.store.state.materials : materiais).find((m) => m.id === id) || materiais.find((m) => m.id === id),
  };
})();
