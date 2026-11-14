# Constituição do Farol

Versão 1.0.0 · Ratificada em 13/11/2026 · Última emenda: nenhuma

Esta constituição reúne as regras que não mudam de uma funcionalidade para outra. Toda especificação, todo plano técnico e todo pull request do Farol precisam respeitá-la. Quando um plano precisa quebrar um princípio, a exceção é escrita e justificada na seção "Verificação da constituição" do `plan.md`, e só vale depois de aprovada na revisão.

## Princípios

### I. O professor é o dono do conteúdo

O tutor e o gerador de questões usam apenas os materiais que o professor publicou na disciplina. Nenhuma questão gerada por IA chega ao aluno sem aprovação explícita do professor. O professor pode retirar um material ou uma questão a qualquer momento, e o efeito vale para a turma inteira.

*Por quê:* o professor só adota uma ferramenta em que confia, e confiança vem de controle sobre o que é ensinado.

### II. Toda resposta mostra a fonte

Toda afirmação do tutor vem acompanhada de pelo menos uma citação do material (aula e página ou slide) que abre o trecho original. Quando o material não tem base para responder, o tutor diz isso claramente e oferece enviar a dúvida ao professor. O tutor nunca completa a resposta com conhecimento de fora do material.

*Por quê:* resposta inventada é o maior risco do produto. Citação permite ao aluno conferir e ao professor auditar.

### III. Ensinar, não entregar respostas

Em exercícios, o tutor guia por pistas em etapas em vez de entregar o resultado, quando o modo pistas está ligado. Durante as janelas de avaliação definidas pelo professor, o tutor fica indisponível na disciplina. Cada disciplina exibe ao aluno a política de uso de IA definida pelo professor.

*Por quê:* o Farol existe para melhorar a aprendizagem, não para facilitar a cola.

### IV. Privacidade por padrão (LGPD)

- O professor vê padrões da turma, nunca quem perguntou o quê.
- Um tópico só aparece no radar se vier de pelo menos 5 alunos diferentes.
- O texto das perguntas passa por remoção de dados pessoais (nome, e-mail, CPF, telefone) antes de ser exibido ou enviado ao provedor de IA.
- O prompt enviado ao provedor nunca leva nome, RA, e-mail ou turma do aluno.
- Coletamos só o necessário, dizemos ao aluno o que é registrado e para quê, e ele pode ver e apagar o próprio histórico.

*Por quê:* dúvida é algo íntimo. Sem anonimato, o aluno não pergunta, e sem conformidade com a LGPD, a instituição não adota.

### V. Acessível e pensado para o celular

Toda tela atende à WCAG 2.1 nível AA: navegação por teclado com foco visível, contraste mínimo de 4,5:1 para texto, rótulos para leitores de tela e respeito à preferência de reduzir animações. As telas são desenhadas primeiro para o celular e usam o design system Farol (tokens e componentes com prefixo `fr-`).

*Por quê:* o aluno que trabalha estuda no ônibus e à noite, pelo celular. E acessibilidade não é opcional em uma instituição de ensino.

### VI. Simplicidade e ferramentas populares

Usamos ferramentas de mercado, com muitos desenvolvedores disponíveis e versões de suporte longo (LTS) sempre que existirem. Uma nova dependência, serviço ou camada de abstração precisa de justificativa escrita no plano (seção "Complexidade justificada") ou de um registro de decisão em `docs/adr/`.

*Por quê:* o projeto precisa sobreviver à troca de equipe, inclusive a alunos de extensão que entram e saem a cada semestre.

### VII. Especificação antes do código

- Nenhuma mudança de comportamento entra no código sem uma especificação aprovada em `specs/`.
- A ordem é sempre: especificação (`spec.md`), plano técnico (`plan.md`), tarefas (`tasks.md`) e, só então, implementação.
- Especificação, plano, tarefas e código mudam juntos, no mesmo pull request. Se o código diverge da especificação, um dos dois está errado e precisa ser corrigido antes do merge.
- Todo requisito tem um identificador (por exemplo, `TUT-RF-03`) que aparece nas tarefas, no código que o implementa e nos testes que o verificam.

*Por quê:* a especificação é a fonte da verdade sobre o que o Farol faz. É ela que o professor orientador, a equipe e as ferramentas de IA leem primeiro.

### VIII. Qualidade verificável

- Todo requisito funcional tem pelo menos um cenário de aceite escrito como Dado / Quando / Então, que pode ser testado.
- Todo critério de sucesso é mensurável (número, prazo ou proporção).
- No produto, o tutor tem um conjunto fixo de 100 perguntas por disciplina piloto que roda a cada mudança de prompt ou de modelo. Se a taxa de citação correta cair abaixo de 90%, a mudança não vai para produção.
- A integração contínua (GitHub Actions) verifica a estrutura das especificações e a rastreabilidade dos requisitos em todo pull request.

## Restrições do projeto

| Tema | Regra |
| --- | --- |
| Custo de IA | Limite diário de perguntas por aluno (padrão 40) e teto de orçamento mensal no provedor. Meta: até R$ 2 por aluno por mês. |
| Localização dos dados | Banco e arquivos na região de São Paulo. Só saem para o provedor de IA a pergunta sem identificação e trechos do material didático. |
| Segredos | Chaves de API em variáveis de ambiente, nunca no repositório. |
| Escopo | O Farol não é um AVA, não corrige provas e não toca em matrícula, notas ou financeiro. |
| Dados de demonstração | O protótipo usa apenas dados fictícios. Nenhum dado real de aluno entra no repositório. |

## Governança

- Esta constituição prevalece sobre qualquer outra prática do projeto.
- Emendas são feitas por pull request com o rótulo `constituicao`, aprovadas pelo dono do produto e pelo professor orientador. O PR explica o motivo e lista as especificações afetadas.
- A versão segue versionamento semântico: MAIOR quando um princípio é removido ou redefinido, MENOR quando um princípio ou seção é acrescentado, CORREÇÃO para ajustes de redação.
- Toda revisão de pull request confere a conformidade com esta constituição. O checklist do template de PR inclui essa verificação.
