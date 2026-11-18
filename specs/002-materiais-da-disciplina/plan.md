# Plano técnico: Materiais da disciplina

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Branch | `002-materiais-da-disciplina` |
| Status | Aprovada |
| Atualizado em | 2026-11-16 |

## Resumo

O front-end envia o PDF ao Django (upload multipart), que grava o arquivo pela API de armazenamento, cria o registro do material e enfileira uma tarefa no Celery ([ADR 0008](../../docs/adr/0008-ambiente-local-em-docker.md)). A tarefa extrai o texto com pypdf, divide em trechos de cerca de 500 tokens com sobreposição, gera os vetores pelo módulo `ia/` e grava tudo no PostgreSQL com pgvector. O status de cada etapa é gravado no banco e lido pelo front-end.

## Contexto técnico

| Item | Valor |
| --- | --- |
| Linguagens | Python 3.13, TypeScript 5 |
| Dependências principais | pypdf, Celery, pgvector (extensão e pacote Python); django-storages só se a produção usar S3 |
| Armazenamento | Arquivos pela API de armazenamento do Django (volume em desenvolvimento; disco ou S3 em produção), PostgreSQL com pgvector para trechos |
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
| `Material` | `disciplina`, `aula_numero`, `aula_titulo`, `arquivo` (FileField), `paginas`, `status` (processando, pronto, atencao, erro, retirado), `etapa`, `versao`, `substitui` (FK Material, opcional), `paginas_sem_texto` (lista) | Índice por `disciplina` + `status` |
| `Trecho` | `material`, `pagina`, `ordem`, `texto`, `inicio`, `fim`, `vetor` (vector) | Índice HNSW no `vetor`; filtro por disciplina via `material` |

## Contratos

| Método e caminho | Entrada | Saída | Erros |
| --- | --- | --- | --- |
| `POST /api/disciplinas/{id}/materiais` | Multipart: `arquivo`, `aula_numero`, `aula_titulo` | `{ material_id, status }` (202); enfileira o processamento | 400 se não for PDF ou passar do limite, 403 |
| `GET /api/disciplinas/{id}/materiais` | | Lista com status e etapa (professor vê todos; aluno só os prontos) | 403 |
| `GET /api/materiais/{id}/arquivo?pagina=N` | | O PDF, servido pelo Django só para quem tem acesso à disciplina, e a posição do trecho a destacar | 403, 404 |
| `GET /api/trechos/{id}` | | Texto da página citada, com o início e o fim do trecho para destacar, e se o material foi substituído | 403, 404 |

Visualizador do trecho (MAT-RF-09): a página citada é mostrada como texto, extraído do PDF, com o trecho destacado, e um link abre o PDF original na mesma página. Destacar dentro do próprio PDF (pdf.js, dependência nova) fica como evolução futura: o dono do produto confirmou a página de texto em 2026-11-18.
| `DELETE /api/materiais/{id}` | | 204; status passa a retirado | 403 |

Tarefa assíncrona `materiais.processar(material_id)`: atualiza `etapa` ao fim de cada passo, grava `Trecho`s numa transação e, no fim, cria a notificação para o professor.

## Como o protótipo implementa

| Requisito | Cobertura | Como o protótipo faz |
| --- | --- | --- |
| MAT-RF-01 | Coberto | `prototipo/js/screens/prof-materiais.js` confere o tipo do arquivo e mostra a mensagem |
| MAT-RF-02 | Parcial | A aula é deduzida pelo próximo número livre; o título vem do nome do arquivo |
| MAT-RF-03 | Simulado | As etapas avançam por temporizador, com os textos de `etapasProcessamento` em `prototipo/js/data.js` |
| MAT-RF-04 | Simulado | Os trechos citáveis são fixos em `citations`, em `prototipo/js/data.js` |
| MAT-RF-05 | Não coberto | |
| MAT-RF-06 | Simulado | Um aviso aparece quando o processamento simulado termina |
| MAT-RF-07 | Simulado | O material novo aparece para a aluna só depois de "Pronto para o tutor" (`prototipo/js/screens/aluno-disciplina.js`) |
| MAT-RF-08 | Coberto | Lista de materiais por aula em `prototipo/js/screens/aluno-disciplina.js` |
| MAT-RF-09 | Simulado | `F.openCitation` em `prototipo/js/ui.js` mostra uma página de papel com o trecho destacado, no lugar do PDF real |
| MAT-RF-10 | Não coberto | |
| MAT-RF-11 | Não coberto | |

## Decisões e pesquisa

- **pypdf** e não PyMuPDF: licença permissiva (PyMuPDF é AGPL) e extração página a página, suficiente para PDFs com texto.
- **Envio pelo Django, e não por URL assinada no S3:** funciona igual em desenvolvimento e em produção, sem serviço extra ([ADR 0008](../../docs/adr/0008-ambiente-local-em-docker.md)). O limite de tamanho fica no Nginx e no Django. Se a produção usar S3 e os arquivos crescerem, a URL assinada pode voltar sem mudar a spec.
- **Trechos de cerca de 500 tokens com sobreposição de 50:** valor inicial; o conjunto de 100 perguntas de teste (spec 003) decide o ajuste.
- **Detecção de página sem texto:** página com menos de 20 caracteres extraídos conta como sem texto. Mais da metade das páginas assim marca o material como "Precisa de atenção".

## Complexidade justificada

| Desvio | Por que é necessário | Alternativa mais simples descartada porque |
| --- | --- | --- |
| Nenhum | | |
