# Plano técnico: Materiais da disciplina

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `002-materiais-da-disciplina` |
| Status | Em revisão |
| Atualizado em | 2026-11-13 |

## Resumo

O front-end envia o PDF ao armazenamento S3 por uma URL assinada, o Django cria o registro do material e enfileira uma tarefa no Celery. A tarefa extrai o texto com pypdf, divide em trechos de cerca de 500 tokens com sobreposição, gera os vetores pelo módulo `ia/` e grava tudo no PostgreSQL com pgvector. O status de cada etapa é gravado no banco e lido pelo front-end.

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | Python 3.12, TypeScript 5 |
| Dependências principais | pypdf, django-storages, Celery, pgvector (extensão e pacote Python) |
| Armazenamento | S3 para arquivos, PostgreSQL com pgvector para trechos |
| Testes | pytest com PDFs de exemplo (texto, escaneado, misto, protegido) |
| Metas de desempenho | 40 páginas em até 2 minutos (MAT-RNF-01) |
| Restrições | Arquivos e banco na região de São Paulo |

## Verificação da constituição

| Princípio | Atende? | Como |
| --- | --- | --- |
| I. O professor é o dono do conteúdo | Sim | Só o professor publica e retira; só material pronto alimenta o tutor |
| II. Toda resposta mostra a fonte | Sim | Cada trecho guarda aula, arquivo e página, que viram a citação |
| III. Ensinar, não entregar respostas | N.A. | |
| IV. Privacidade por padrão | Sim | O material didático não tem dado pessoal de aluno |
| V. Acessível e pensado para o celular | Sim | Envio por arrastar ou por botão; status anunciado para leitores de tela |
| VI. Simplicidade e ferramentas populares | Sim | pypdf e Celery, sem serviço extra de OCR |
| VII. Especificação antes do código | Sim | |
| VIII. Qualidade verificável | Sim | PDFs de exemplo no conjunto de testes |

## Modelo de dados

| Entidade | Campos | Observações |
| --- | --- | --- |
| `Material` | `disciplina`, `aula_numero`, `aula_titulo`, `arquivo` (chave no S3), `paginas`, `status` (processando, pronto, atencao, erro, retirado), `etapa`, `versao`, `substitui` (FK Material, opcional), `paginas_sem_texto` (lista) | Índice por `disciplina` + `status` |
| `Trecho` | `material`, `pagina`, `ordem`, `texto`, `inicio`, `fim`, `vetor` (vector) | Índice HNSW no `vetor`; filtro por disciplina via `material` |

## Contratos

| Método e caminho | Entrada | Saída | Erros |
| --- | --- | --- | --- |
| `POST /api/disciplinas/{id}/materiais` | `{ aula_numero, aula_titulo, nome_arquivo, tamanho }` | `{ material_id, url_envio }` (URL assinada do S3) | 400 se não for PDF ou passar do limite, 403 |
| `POST /api/materiais/{id}/enviado` | | 202; enfileira o processamento | 409 se já processado |
| `GET /api/disciplinas/{id}/materiais` | | Lista com status e etapa (professor vê todos; aluno só os prontos) | 403 |
| `GET /api/materiais/{id}/arquivo?pagina=N` | | URL temporária do PDF e posição do trecho a destacar | 403, 404 |
| `DELETE /api/materiais/{id}` | | 204; status passa a retirado | 403 |

Tarefa assíncrona `materiais.processar(material_id)`: atualiza `etapa` ao fim de cada passo, grava `Trecho`s numa transação e, no fim, cria a notificação para o professor.

## Como o protótipo implementa

| Requisito | Cobertura | Como o protótipo faz |
| --- | --- | --- |
| MAT-RF-01 | Coberto | `js/screens/prof-materiais.js` confere o tipo do arquivo e mostra a mensagem |
| MAT-RF-02 | Parcial | A aula é deduzida pelo próximo número livre; o título vem do nome do arquivo |
| MAT-RF-03 | Simulado | As etapas avançam por temporizador, com os textos de `etapasProcessamento` em `js/data.js` |
| MAT-RF-04 | Simulado | Os trechos citáveis são fixos em `citations`, em `js/data.js` |
| MAT-RF-05 | Não coberto | |
| MAT-RF-06 | Simulado | Um aviso aparece quando o processamento simulado termina |
| MAT-RF-07 | Simulado | O material novo aparece para a aluna só depois de "Pronto para o tutor" (`js/screens/aluno-disciplina.js`) |
| MAT-RF-08 | Coberto | Lista de materiais por aula em `js/screens/aluno-disciplina.js` |
| MAT-RF-09 | Simulado | `F.openCitation` em `js/ui.js` mostra uma página de papel com o trecho destacado, no lugar do PDF real |
| MAT-RF-10 | Não coberto | |
| MAT-RF-11 | Não coberto | |

## Decisões e pesquisa

- **pypdf** e não PyMuPDF: licença permissiva (PyMuPDF é AGPL) e extração página a página, suficiente para PDFs com texto.
- **Envio direto ao S3 por URL assinada:** o arquivo não passa pelo Django, o que evita travar o servidor com arquivos grandes.
- **Trechos de cerca de 500 tokens com sobreposição de 50:** valor inicial; o conjunto de 100 perguntas de teste (spec 003) decide o ajuste.
- **Detecção de página sem texto:** página com menos de 20 caracteres extraídos conta como sem texto. Mais da metade das páginas assim marca o material como "Precisa de atenção".

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| Nenhum | | |
