# 0004. Guardar dados e vetores no PostgreSQL com pgvector

- **Status:** Proposta
- **Data:** 12/11/2026

## Contexto

O tutor faz busca semântica nos trechos do material (RAG), o que exige guardar e consultar vetores. Além disso, o sistema guarda usuários, turmas, materiais, questões, dúvidas e registros de uso. O volume estimado é pequeno: na casa de 100 mil trechos.

## Decisão

PostgreSQL com a extensão pgvector guarda os dados da aplicação e os vetores no mesmo banco.

## Alternativas consideradas

| Alternativa | Prós | Contras |
| --- | --- | --- |
| Banco vetorial dedicado (Pinecone, Qdrant, Weaviate) | Mais rápido e com mais recursos em grande escala | Mais um serviço, outro backup e consistência entre dois bancos |
| MySQL | Popular | Sem suporte maduro a vetores |

## Consequências

- Um backup, uma conexão e transações consistentes: um trecho e seu vetor nunca ficam fora de sincronia.
- A busca filtra por disciplina na mesma consulta, o que garante que o tutor só use o material da disciplina certa.
- Com dezenas de milhões de vetores, seria preciso reavaliar. Não é o caso do piloto nem da instituição inteira.
