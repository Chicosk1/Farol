# Registros de decisão de arquitetura (ADR)

Um ADR registra uma decisão técnica que afeta o projeto inteiro: o contexto, a escolha, as alternativas e as consequências. Decisões que só afetam uma funcionalidade ficam na seção "Decisões e pesquisa" do `plan.md` da spec.

ADRs não são apagados. Quando uma decisão muda, um ADR novo substitui o antigo, e o antigo passa a ter o status "Substituída por 00NN".

| Nº | Decisão | Status |
| --- | --- | --- |
| [0001](0001-adotar-sdd-com-spec-kit.md) | Adotar desenvolvimento orientado por especificação, com a convenção do GitHub Spec Kit | Aceita |
| [0002](0002-prototipo-sem-framework.md) | Fazer o protótipo em HTML, CSS e JavaScript puros, sem etapa de build | Aceita |
| [0003](0003-django-no-back-end.md) | Usar Python com Django e Django REST Framework no back-end | Proposta |
| [0004](0004-postgresql-com-pgvector.md) | Guardar dados e vetores no PostgreSQL com pgvector | Proposta |
| [0005](0005-ia-via-api-com-modulo-proprio.md) | Usar IA via API de provedor, com módulo próprio e sem framework de orquestração | Proposta |
| [0006](0006-docker-compose-em-um-servidor.md) | Rodar tudo com Docker Compose em um servidor em São Paulo | Proposta |

"Proposta" significa que a decisão vem da idealização e será confirmada no fim da fase 0, com a TI e o professor orientador.

## Como escrever um ADR

1. Copie o ADR mais recente e use o próximo número.
2. Preencha Contexto, Decisão, Alternativas consideradas e Consequências. Seja curto: uma página basta.
3. Abra um pull request. O ADR entra como "Proposta" e passa a "Aceita" quando o PR é aprovado.
