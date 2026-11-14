# Especificação: [NOME DA FUNCIONALIDADE]

| Campo | Valor |
| --- | --- |
| Código | `[XXX]` (prefixo dos identificadores desta spec, por exemplo `TUT`) |
| Branch | `[NNN-nome-curto]` |
| Status | Rascunho · Em revisão · Aprovada · Implementada no protótipo · Implementada no produto |
| Criada em | [AAAA-MM-DD] |
| Issue | #[número] |

<!--
Esta spec descreve O QUE o sistema faz e POR QUÊ, do ponto de vista de quem usa.
Não cite tecnologia aqui (framework, banco, biblioteca): isso vai no plan.md.
Marque toda dúvida em aberto com [PRECISA ESCLARECER: pergunta]. Uma spec só é aprovada sem marcações pendentes,
ou com cada uma registrada em "Questões em aberto" com dono e prazo.
-->

## Contexto

[Qual problema esta funcionalidade resolve, para quem, e como ela se liga à visão do produto (docs/visao-do-produto.md).]

## Histórias de usuário e testes de aceite

<!--
Ordene por prioridade. Cada história precisa poder ser implementada e testada sozinha,
entregando valor mesmo que as outras não existam ainda.
P1 = sem ela a funcionalidade não faz sentido; P2 = importante; P3 = desejável.
-->

### História 1: [título curto] (Prioridade: P1)

[Como (perfil), quero (ação) para (benefício).]

**Por que esta prioridade:** [justificativa]

**Teste independente:** [como verificar esta história sozinha]

**Cenários de aceite:**

1. **Dado** [estado inicial], **quando** [ação], **então** [resultado esperado].
2. **Dado** [estado inicial], **quando** [ação], **então** [resultado esperado].

### História 2: [título curto] (Prioridade: P2)

[...]

### Casos de borda

- O que acontece quando [condição de limite]?
- Como o sistema trata [cenário de erro]?

## Requisitos

### Requisitos funcionais

<!-- Use "O sistema DEVE" para obrigações e "O sistema PODE" para opções. Um requisito por linha, testável. -->

- **[XXX]-RF-01**: O sistema DEVE [capacidade].
- **[XXX]-RF-02**: O sistema DEVE [capacidade]. [PRECISA ESCLARECER: ...]

### Requisitos não funcionais

- **[XXX]-RNF-01**: [desempenho, segurança, privacidade, acessibilidade, custo]

### Entidades principais

- **[Entidade]**: [o que representa, atributos principais em linguagem de negócio, relações]

## Critérios de sucesso

<!-- Mensuráveis e independentes de tecnologia. -->

- **[XXX]-CS-01**: [métrica com número, prazo ou proporção]

## Fora do escopo

- [O que esta funcionalidade deliberadamente não faz.]

## Questões em aberto

| Questão | Dono | Prazo |
| --- | --- | --- |
| [pergunta] | [pessoa] | [data] |

## Histórico

| Data | Mudança |
| --- | --- |
| [AAAA-MM-DD] | Criação da spec |
