# Tarefas: Materiais da disciplina

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-16 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] MAT-T01 [H1] Tela de materiais com área de arrastar e soltar e validação de PDF em `prototipo/js/screens/prof-materiais.js` (MAT-RF-01, MAT-RF-02)
- [x] MAT-T02 [H1] Etapas de processamento simuladas e aviso de material pronto em `prototipo/js/screens/prof-materiais.js` (MAT-RF-03, MAT-RF-06)
- [x] MAT-T03 [H2] Lista de materiais da disciplina para a aluna em `prototipo/js/screens/aluno-disciplina.js` (MAT-RF-07, MAT-RF-08)
- [x] MAT-T04 [H2] Página do material com trecho destacado em `prototipo/js/ui.js` e trechos em `prototipo/js/data.js` (MAT-RF-04, MAT-RF-09)

## Produto: fundação

- [x] MAT-T10 Habilitar a extensão pgvector e criar os modelos `Material` e `Trecho` com migrações
- [x] MAT-T11 [P] Configurar o armazenamento de arquivos pela API do Django: pasta indicada por variável de ambiente, em volume do Docker compartilhado pelo `backend` e pelo `worker`; S3 opcional em produção fica para a fase 0
- [x] MAT-T12 [P] Gerar por código os PDFs de exemplo (texto, escaneado, misto, protegido e grande) em `backend/materiais/testes/pdfs.py`, sem binários no repositório
- [x] MAT-T13 Módulo `ia` com `gerar_embedding` e o adaptador falso, que devolve vetores previsíveis para os testes (parte da TUT-T10, usada pelo processamento dos PDFs)

## Produto: História 1, publicar o PDF de uma aula (P1)

- [x] MAT-T20 [H1] Testes de envio, validação e etapas, entregues junto das MAT-T21 e MAT-T22 (MAT-RF-01, MAT-RF-02, MAT-RF-03)
- [x] MAT-T21 [H1] Rota de envio do PDF (multipart), com validação de tipo e tamanho (MAT-RF-01, MAT-RF-02)
- [x] MAT-T22 [H1] Tarefa `materiais.processar`: extração por página, divisão em trechos e vetores (MAT-RF-03, MAT-RF-04)
- [x] MAT-T23 [H1] Módulo `notificacoes` com o modelo `Notificacao`, o serviço `notificar` e as rotas `GET /api/notificacoes` e `POST /api/notificacoes/{id}/lida`; a tarefa de processamento avisa o professor quando o material fica pronto ou falha (MAT-RF-06)
- [x] MAT-T25 [H1] Sino de notificações no cabeçalho do front-end (MAT-RF-06)
- [x] MAT-T24 [H1] Tela de materiais do professor com status ao vivo (MAT-RF-03)

## Produto: História 2, consultar os materiais (P1)

- [x] MAT-T30 [H2] Testes de visibilidade: aluno só vê material pronto, entregues junto da MAT-T31 (MAT-RF-07)
- [x] MAT-T31 [H2] Lista de materiais do aluno e visualizador de PDF com página inicial (MAT-RF-08, MAT-RF-09)
- [x] MAT-T33 [H2] Tela de materiais da disciplina para a aluna no front-end, com a lista por aula e o PDF aberto na primeira página; a MAT-T31 entregou só o back-end (MAT-RF-08, MAT-RF-09)
- [ ] MAT-T32 [H2] Destaque do trecho citado no visualizador (MAT-RF-09)

## Produto: História 3, avisar PDF sem texto (P2)

- [x] MAT-T40 [H3] Detecção de páginas sem texto e status "Precisa de atenção" (MAT-RF-05), entregue junto da MAT-T22

## Produto: História 4, retirar ou substituir (P2)

- [x] MAT-T50 [H4] Teste: material retirado não é usado na pergunta seguinte, entregue junto da MAT-T51 e completado pela spec 003 (MAT-RF-10, MAT-CS-03)
- [x] MAT-T51 [H4] Retirada de material e marcação das questões de origem (MAT-RF-10)
- [ ] MAT-T52 [H4] Envio de nova versão com troca atômica ao ficar pronta (MAT-RF-11)

## Produto: acabamento

- [ ] MAT-T90 Medir o tempo de processamento de um PDF de 40 páginas (MAT-RNF-01)
- [ ] MAT-T91 Teste de permissão de envio e retirada (MAT-RNF-02)

## Dependências

Depende das Histórias 1 e 2 da spec 001. A História 1 desta spec bloqueia as specs 003 e 005.
