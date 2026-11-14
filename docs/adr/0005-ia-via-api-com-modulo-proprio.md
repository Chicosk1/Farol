# 0005. Usar IA via API de provedor, com módulo próprio e sem framework de orquestração

- **Status:** Proposta
- **Data:** 12/11/2026

## Contexto

O tutor, o gerador de questões e o radar usam um modelo de linguagem e um modelo de embeddings. A instituição não tem GPU nem equipe de MLOps, e o custo precisa ficar abaixo de R$ 2 por aluno por mês.

## Decisão

1. Modelos de linguagem e de embeddings de um provedor de mercado, contratados via API, em plano empresarial com retenção zero e sem uso dos dados para treino.
2. Todo acesso ao provedor passa por um único módulo do back-end (`ia/`), com uma interface própria. Trocar de provedor significa mudar esse módulo.
3. Sem LangChain ou LlamaIndex: o fluxo é curto (buscar trechos, montar o prompt, chamar o modelo) e é escrito com o SDK oficial do provedor.

## Alternativas consideradas

| Alternativa | Prós | Contras |
| --- | --- | --- |
| Modelo aberto em GPU própria (Llama, Qwen) | Dados não saem da instituição | Custo fixo alto, manutenção de GPU, qualidade menor nos modelos que cabem no orçamento |
| LangChain ou LlamaIndex | Utilitários prontos | Mais camadas, depuração mais difícil, mudanças frequentes de API |

## Consequências

- Qualidade alta sem manter infraestrutura de IA, pagando por uso (estimativa de R$ 0,14 a R$ 1,43 por aluno por mês).
- Dados saem da instituição: só a pergunta sem identificação e trechos do material didático. A base legal precisa ser validada com o DPO na fase 0.
- O conjunto de 100 perguntas de teste roda periodicamente com um segundo provedor, para manter a troca viável.
