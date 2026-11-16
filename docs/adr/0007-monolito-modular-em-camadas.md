# 0007. Monólito modular em camadas, com adaptadores nas fronteiras externas

- **Status:** Proposta
- **Data:** 16/11/2026

## Contexto

A idealização escolheu as ferramentas (React, Django, PostgreSQL, Celery), mas não o estilo da arquitetura: como o código se divide, quem pode depender de quem e onde ficam as regras de negócio. Sem isso, cada pessoa organiza o código do seu jeito, e com a equipe mudando a cada semestre o projeto vira um emaranhado.

O que pesa na decisão:

- Equipe pequena e rotativa, com alunos de extensão.
- Um único servidor no piloto (ADR 0006).
- Sete funcionalidades com fronteiras já claras nas specs.
- Regras que precisam ser testadas sem chamar a IA de verdade, e um provedor de IA que precisa poder ser trocado (ADR 0005).
- Pessoas trabalhando em paralelo sem pisar no código umas das outras.

## Decisão

**Um monólito modular:** um único back-end Django, implantado como um processo web mais os workers do Celery, todos com o mesmo código, e um front-end React separado.

### Módulos

O back-end é dividido em apps Django que seguem as specs:

| Módulo | Specs | Responsabilidade |
| --- | --- | --- |
| `nucleo` | todas | Utilidades sem regra de negócio: permissões por disciplina, identificador pseudônimo, filtro de dados pessoais |
| `contas` | 001 | Pessoas, perfis, login, aviso de privacidade |
| `disciplinas` | 001 | Disciplinas, matrículas, favoritos, importação de turmas |
| `materiais` | 002 | Envio e processamento de PDFs, trechos |
| `tutor` | 003 | Conversas, busca nos trechos, configuração do tutor, janelas de prova |
| `duvidas` | 004 | Dúvidas enviadas ao professor |
| `pratica` | 005, 006 | Questões, quizzes, revisão do dia |
| `radar` | 007 | Cálculo e leitura do radar semanal |
| `ia` | 003, 005, 007 | Porta única para o provedor de IA, com um adaptador real e um falso para testes |

### Camadas dentro de cada módulo

```
api/          views, serializers e rotas: só HTTP, nenhuma regra de negócio
servicos.py   casos de uso: as regras das specs; chamado pela API e pelas tarefas
models.py     dados, com o ORM do Django
tarefas.py    tarefas do Celery: finas, só chamam serviços
testes/       testes do módulo
```

### Regras de dependência

1. `api` chama `servicos`; `servicos` usa `models`. Uma view nunca acessa o banco direto para aplicar uma regra.
2. Um módulo usa outro **somente** pelas funções públicas do `servicos.py` dele. A exceção é a chave estrangeira para `Pessoa` e `Disciplina`, que o Django exige.
3. `nucleo` não depende de nenhum outro módulo.
4. Nenhum módulo chama o provedor de IA diretamente: tudo passa por `ia`, que expõe uma interface (porta) e escolhe o adaptador pela configuração.
5. As regras 2, 3 e 4 são verificadas automaticamente no CI com o import-linter.

### Front-end

- Organizado por funcionalidade, espelhando os módulos: `src/funcionalidades/<modulo>/` com telas, componentes e chamadas próprias.
- Os componentes do design system Farol ficam em `src/componentes/`.
- O acesso à API passa só por `src/api/`, com tipos gerados a partir do contrato OpenAPI.
- Os dados do servidor são gerenciados pelo TanStack Query.

### Contrato e autenticação

- A API REST é descrita em OpenAPI, gerado pelo drf-spectacular a partir do código. Os tipos TypeScript do front-end são gerados desse arquivo (openapi-typescript), e o CI falha se o contrato mudou sem regenerar os tipos.
- A autenticação usa sessão do Django (cookie HttpOnly e proteção CSRF). Front-end e API ficam na mesma origem: proxy do Vite em desenvolvimento e Nginx em produção. Sem JWT.

## Alternativas consideradas

| Alternativa | Prós | Por que não |
| --- | --- | --- |
| Microsserviços | Cada parte escala e é implantada sozinha | Rede, filas e transações distribuídas para uma equipe pequena e um único servidor. Nenhum módulo tem carga que justifique |
| Django "tradicional", com regras nas views | Menos arquivos | A mesma regra é usada pela API e pelas tarefas do Celery; nas views, ela seria duplicada e difícil de testar |
| Arquitetura limpa ou hexagonal completa, com entidades e repositórios próprios | Domínio independente do framework | Duplica o que o ORM do Django já faz e aumenta a curva para alunos. Só a IA, os arquivos e o e-mail são realmente trocáveis, então os adaptadores ficam só nessas fronteiras |
| Plataforma gerenciada (Supabase, Firebase) | Login e banco prontos | Regras espalhadas entre banco, funções e front-end, e dependência de plataforma. Ver ADR 0008 |

## Consequências

- Um deploy, uma base de código e transações simples no banco.
- As fronteiras entre módulos permitem extrair um deles no futuro (por exemplo, o radar), se um dia for preciso.
- Os serviços são testados sem HTTP, e a IA falsa deixa os testes rápidos, gratuitos e sem internet.
- Manter as regras exige disciplina, por isso a verificação automática com o import-linter.
- Dependências novas, justificadas por esta decisão: drf-spectacular, import-linter, openapi-typescript e TanStack Query.
