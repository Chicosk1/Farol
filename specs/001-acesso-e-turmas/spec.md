# Especificação: Acesso e turmas

| Campo | Valor |
| --- | --- |
| Código | `ACE` |
| Branch | `001-acesso-e-turmas` |
| Status | Em revisão |
| Criada em | 2026-11-13 |
| Origem | Documento de idealização, seção "Base comum" |

## Contexto

Antes de qualquer funcionalidade de estudo, cada pessoa precisa entrar com a conta que já tem na instituição e ver só as disciplinas que são dela. Esta spec cobre a base comum do Farol: login, perfis, turmas e a transparência sobre os dados do aluno. Ela vem primeiro porque todas as outras dependem dela.

## Histórias de usuário e testes de aceite

### História 1: Entrar com a conta institucional (Prioridade: P1)

Como aluno ou professor, quero entrar com a minha conta da instituição, sem criar uma senha nova, para começar a usar o Farol em segundos.

**Por que esta prioridade:** sem login não há como saber quais disciplinas mostrar nem aplicar as regras de privacidade.

**Teste independente:** uma conta institucional de teste entra e chega à tela inicial do seu perfil.

**Cenários de aceite:**

1. **Dado** um aluno com conta institucional ativa e matrícula importada, **quando** ele escolhe "Entrar com a conta institucional" e autoriza, **então** chega à tela inicial do aluno.
2. **Dado** uma pessoa com conta de fora da instituição, **quando** tenta entrar, **então** vê a mensagem "Use a sua conta institucional" e não acessa nada.
3. **Dado** uma conta institucional sem nenhuma matrícula ou disciplina, **quando** entra, **então** vê uma tela explicando que ainda não há disciplinas e como pedir ajuda.

### História 2: Ver só as minhas disciplinas (Prioridade: P1)

Como aluno, quero ver as disciplinas em que estou matriculado, encontrar uma rapidamente e marcar as favoritas.

**Por que esta prioridade:** é a porta de entrada para o tutor, os materiais e os quizzes.

**Teste independente:** um aluno matriculado em 6 disciplinas vê exatamente essas 6.

**Cenários de aceite:**

1. **Dado** um aluno matriculado em 6 disciplinas, **quando** abre "Disciplinas", **então** vê as 6 e nenhuma outra.
2. **Dado** a lista de disciplinas, **quando** o aluno digita parte do nome na busca, **então** a lista mostra só as que contêm o texto, sem diferenciar acentos e maiúsculas.
3. **Dado** a lista, **quando** o aluno marca uma disciplina como favorita, **então** ela aparece na aba "Favoritas" e no topo da tela inicial.
4. **Dado** a lista, **quando** o aluno escolhe a aba "Com tutor", **então** vê só as disciplinas que têm material pronto para o tutor.
5. **Dado** um professor, **quando** entra, **então** vê só as disciplinas que leciona.

### História 3: Importar turmas por planilha (Prioridade: P2)

Como administrador, quero importar turmas e matrículas a partir de uma planilha exportada do sistema acadêmico, para não cadastrar ninguém à mão.

**Por que esta prioridade:** no piloto, poucas turmas poderiam ser cadastradas à mão; a importação passa a ser essencial ao crescer.

**Teste independente:** importar um CSV de exemplo com 60 alunos e 2 disciplinas cria as matrículas certas.

**Cenários de aceite:**

1. **Dado** um CSV no formato combinado, **quando** o administrador o importa, **então** vê um relatório com o número de linhas aceitas e a lista das rejeitadas com o motivo.
2. **Dado** um CSV já importado, **quando** é importado de novo, **então** nenhum registro é duplicado.
3. **Dado** um aluno que saiu da turma no sistema acadêmico, **quando** o CSV atualizado é importado, **então** o aluno perde o acesso àquela disciplina.

### História 4: Saber o que é registrado sobre mim (Prioridade: P2)

Como aluno, quero saber o que o Farol registra sobre mim e poder apagar o meu histórico.

**Por que esta prioridade:** é exigência da LGPD e condição para o aluno confiar no tutor.

**Teste independente:** um aluno novo vê o aviso na primeira entrada, e um aluno com histórico consegue apagá-lo.

**Cenários de aceite:**

1. **Dado** um aluno que entra pela primeira vez, **quando** chega à tela inicial, **então** vê um aviso curto sobre o que é registrado, para quê e por quanto tempo, e só continua depois de confirmar que leu.
2. **Dado** um aluno com conversas no tutor, **quando** escolhe "Apagar meu histórico" e confirma, **então** as conversas deixam de aparecer para ele e são excluídas do banco.
3. **Dado** que o texto do aviso mudou, **quando** o aluno entra, **então** vê o aviso novo uma vez.

### História 5: Usar como app no celular (Prioridade: P3)

Como aluno, quero instalar o Farol na tela inicial do celular, para abrir como um app.

**Teste independente:** no Chrome do Android, a opção "Instalar app" aparece e o Farol abre em tela cheia.

**Cenários de aceite:**

1. **Dado** um celular Android com Chrome, **quando** o aluno escolhe "Instalar", **então** o Farol aparece na tela inicial e abre sem a barra do navegador.

### Casos de borda

- Pessoa com mais de um perfil (por exemplo, professor que também é aluno de pós-graduação): escolhe o perfil depois de entrar e pode trocar sem sair.
- Aluno sem conta institucional ativa: [PRECISA ESCLARECER: oferecer entrada por link mágico enviado ao e-mail cadastrado, como plano B, ou encaminhar para a TI?]
- CSV com coluna faltando, codificação diferente de UTF-8 ou separador ponto e vírgula: o relatório explica o problema e nada é importado pela metade.
- Sessão expirada no meio de uma ação: a pessoa entra de novo e volta para a mesma tela.

## Requisitos

### Requisitos funcionais

- **ACE-RF-01**: O sistema DEVE permitir a entrada somente com conta institucional, via OpenID Connect. [PRECISA ESCLARECER: Google Workspace ou Microsoft 365]
- **ACE-RF-02**: O sistema NÃO DEVE criar nem guardar senhas próprias.
- **ACE-RF-03**: O sistema DEVE atribuir a cada pessoa um ou mais perfis entre aluno, professor, coordenação e administrador, e permitir trocar de perfil sem sair.
- **ACE-RF-04**: O sistema DEVE mostrar ao aluno só as disciplinas em que está matriculado e ao professor só as que leciona.
- **ACE-RF-05**: O sistema DEVE verificar no servidor, em toda operação, se a pessoa tem permissão na disciplina envolvida.
- **ACE-RF-06**: O sistema DEVE importar disciplinas, turmas e matrículas de um CSV exportado do sistema acadêmico e mostrar um relatório de linhas aceitas e rejeitadas. [PRECISA ESCLARECER: a importação é feita só pela TI ou cada professor também pode importar a própria turma?]
- **ACE-RF-07**: A importação DEVE ser idempotente: importar o mesmo arquivo duas vezes não duplica registros, e matrículas ausentes no arquivo novo são encerradas.
- **ACE-RF-08**: Na primeira entrada e a cada nova versão do aviso, o sistema DEVE mostrar ao aluno o que é registrado, para quê e por quanto tempo, e guardar a data da ciência.
- **ACE-RF-09**: O aluno DEVE poder ver e apagar o próprio histórico de conversas com o tutor.
- **ACE-RF-10**: A lista de disciplinas DEVE permitir buscar por nome, filtrar por Todas, Favoritas e Com tutor, marcar favoritas e alternar entre grade e lista.
- **ACE-RF-11**: A interface DEVE poder ser instalada na tela inicial do celular como aplicativo web (PWA).

### Requisitos não funcionais

- **ACE-RNF-01**: Todas as telas desta spec atendem à WCAG 2.1 nível AA.
- **ACE-RNF-02**: Toda comunicação usa HTTPS, e a sessão expira após um período sem uso definido com a TI (sugestão inicial: 12 horas).

### Entidades principais

- **Pessoa**: quem usa o Farol. Nome, e-mail institucional, perfis.
- **Disciplina**: código, nome, turma, semestre, professor responsável.
- **Matrícula**: liga um aluno a uma disciplina, com situação ativa ou encerrada.
- **Favorito**: disciplina marcada por um aluno.
- **Ciência do aviso de privacidade**: pessoa, versão do aviso e data.

## Critérios de sucesso

- **ACE-CS-01**: 95% dos alunos do piloto entram na primeira tentativa, sem pedir ajuda.
- **ACE-CS-02**: A importação de uma planilha com 1.000 matrículas termina em menos de 1 minuto.
- **ACE-CS-03**: Nenhum acesso indevido a disciplina nos testes automáticos de permissão, que cobrem todas as rotas da API.

## Fora do escopo

- Integração automática com o sistema acadêmico (fica a importação por CSV).
- Abrir o Farol de dentro do AVA (LTI 1.3), previsto para a expansão.
- Notas, frequência e qualquer dado financeiro.

## Questões em aberto

| Questão | Dono | Prazo |
| --- | --- | --- |
| Google Workspace ou Microsoft 365 | TI da UNIMATER | Fim da fase 0 |
| Plano B para quem não tem conta institucional ativa | TI da UNIMATER | Fim da fase 0 |
| Quem faz a importação de turmas | Coordenação | Fim da fase 0 |
| Formato exato do CSV exportado pelo sistema acadêmico | TI da UNIMATER | Fim da fase 0 |

## Histórico

| Data | Mudança |
| --- | --- |
| 2026-11-13 | Criação da spec a partir da idealização e do protótipo |
