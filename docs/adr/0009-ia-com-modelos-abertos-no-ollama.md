# 0009. Usar modelos abertos no Ollama, por uma API compatível com a da OpenAI

- **Status:** Aceita
- **Data:** 18/11/2026
- **Substitui em parte:** [ADR 0005](0005-ia-via-api-com-modulo-proprio.md), no item 1 (provedor de mercado contratado) e no uso do SDK oficial. Continuam valendo o módulo próprio `ia/` e a ausência de framework de orquestração.

## Contexto

O Farol é um projeto acadêmico, e o dono do produto pediu custo zero com IA. A ADR 0005 previa um provedor de mercado em plano empresarial, pago por uso.

Opções gratuitas consideradas:

- **Assinatura do Claude Code do desenvolvedor:** não serve. É uma licença de uso pessoal e não pode alimentar um sistema usado por outras pessoas. A API da Anthropic é cobrada à parte.
- **Planos gratuitos de APIs de mercado** (Gemini, Groq e outros): têm limites por minuto e por dia. Em alguns deles, os dados enviados podem ser usados para treinar os modelos, o que contraria a exigência de retenção zero (princípio IV da constituição).

## Decisão

1. **Modelos abertos rodando no Ollama**, como um serviço do próprio Docker Compose ([ADR 0008](0008-ambiente-local-em-docker.md)), no perfil `ia`:
   - `gemma3:4b` para as respostas: multilíngue, bom em português e cabe em CPU.
   - `embeddinggemma` para os vetores de busca: multilíngue, com 768 dimensões que podem ser reduzidas a 256 sem treino novo (Matryoshka), o tamanho que o banco já usa.
2. **Um adaptador só, `ia.adaptadores.compativel_openai.ProvedorCompativelOpenAI`**, que fala as rotas `/v1/chat/completions` (com streaming) e `/v1/embeddings`. Endereço, modelos e chave vêm de variáveis de ambiente. O Ollama implementa essas rotas, e os provedores de mercado também. Trocar o Ollama por um provedor pago, se um dia houver orçamento, é só configuração.
3. **Sem SDK e sem dependência nova:** o adaptador usa o `urllib` da biblioteca padrão do Python.

## Alternativas consideradas

| Alternativa | Prós | Contras |
| --- | --- | --- |
| Provedor de mercado pago (ADR 0005) | Melhor qualidade, respostas rápidas | Custo por uso; projeto sem orçamento |
| Plano gratuito do Gemini ou do Groq | Qualidade alta, sem servidor de IA | Limites de uso. Dados podem servir para treino e saem da instituição |
| Assinatura do Claude Code | Já existe | Os termos de uso não permitem usá-la como back-end de um sistema |
| Modelo maior no Ollama (7B ou mais) | Respostas melhores | Lento demais em CPU e exige mais de 8 GB de memória só para o modelo |

## Consequências

- Custo zero com IA, e nenhum dado sai do servidor: nem a pergunta nem o material. O preço por token fica em zero, e o alerta de orçamento não dispara.
- A qualidade das respostas é menor que a de um modelo de mercado. O conjunto de avaliação (TUT-T12 e TUT-T13) mede a taxa de citação correta e diz se ela basta para o piloto.
- Em CPU, o tempo até a primeira palavra é maior. O comando `medir_tutor` mede esse tempo no servidor do piloto, e uma GPU modesta resolve, se for preciso.
- O servidor precisa de cerca de 6 GB de memória a mais para o Ollama e os dois modelos.
- A similaridade mínima do tutor precisa ser recalibrada para o `embeddinggemma`.
- Nos testes, continua valendo o adaptador falso. O adaptador real é testado contra um servidor HTTP falso, sem internet.
