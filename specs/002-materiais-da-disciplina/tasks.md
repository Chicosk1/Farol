# Tarefas: Materiais da disciplina

| Campo | Valor |
| --- | --- |
| Spec | [spec.md](./spec.md) |
| Plano | [plan.md](./plan.md) |
| Atualizado em | 2026-11-13 |

Formato: `ID [P] [história] descrição (requisitos)`. `[P]` indica que a tarefa pode ser feita em paralelo com outras `[P]` do mesmo bloco.

## Protótipo navegável

- [x] MAT-T01 [H1] Tela de materiais com área de arrastar e soltar e validação de PDF em `js/screens/prof-materiais.js` (MAT-RF-01, MAT-RF-02)
- [x] MAT-T02 [H1] Etapas de processamento simuladas e aviso de material pronto em `js/screens/prof-materiais.js` (MAT-RF-03, MAT-RF-06)
- [x] MAT-T03 [H2] Lista de materiais da disciplina para a aluna em `js/screens/aluno-disciplina.js` (MAT-RF-07, MAT-RF-08)
- [x] MAT-T04 [H2] Página do material com trecho destacado em `js/ui.js` e trechos em `js/data.js` (MAT-RF-04, MAT-RF-09)

## Produto: fundação

- [ ] MAT-T10 Habilitar a extensão pgvector e criar os modelos `Material` e `Trecho` com migrações
- [ ] MAT-T11 [P] Configurar django-storages com S3 e URLs assinadas
- [ ] MAT-T12 [P] Reunir PDFs de exemplo (texto, escaneado, misto, protegido) em `backend/materiais/tests/arquivos/`

## Produto: História 1, publicar o PDF de uma aula (P1)

- [ ] MAT-T20 [P] [H1] Testes de envio, validação e etapas (MAT-RF-01, MAT-RF-02, MAT-RF-03)
- [ ] MAT-T21 [H1] Rotas de criação de material e confirmação de envio (MAT-RF-01, MAT-RF-02)
- [ ] MAT-T22 [H1] Tarefa `materiais.processar`: extração por página, divisão em trechos e vetores (MAT-RF-03, MAT-RF-04)
- [ ] MAT-T23 [H1] Notificação ao professor quando o material fica pronto ou falha (MAT-RF-06)
- [ ] MAT-T24 [H1] Tela de materiais do professor com status ao vivo (MAT-RF-03)

## Produto: História 2, consultar os materiais (P1)

- [ ] MAT-T30 [P] [H2] Testes de visibilidade: aluno só vê material pronto (MAT-RF-07)
- [ ] MAT-T31 [H2] Lista de materiais do aluno e visualizador de PDF com página inicial (MAT-RF-08, MAT-RF-09)
- [ ] MAT-T32 [H2] Destaque do trecho citado no visualizador (MAT-RF-09)

## Produto: História 3, avisar PDF sem texto (P2)

- [ ] MAT-T40 [H3] Detecção de páginas sem texto e status "Precisa de atenção" (MAT-RF-05)

## Produto: História 4, retirar ou substituir (P2)

- [ ] MAT-T50 [P] [H4] Teste: material retirado não é usado na pergunta seguinte (MAT-RF-10, MAT-CS-03)
- [ ] MAT-T51 [H4] Retirada de material e marcação das questões de origem (MAT-RF-10)
- [ ] MAT-T52 [H4] Envio de nova versão com troca atômica ao ficar pronta (MAT-RF-11)

## Produto: acabamento

- [ ] MAT-T90 Medir o tempo de processamento de um PDF de 40 páginas (MAT-RNF-01)
- [ ] MAT-T91 Teste de permissão de envio e retirada (MAT-RNF-02)

## Dependências

Depende das Histórias 1 e 2 da spec 001. A História 1 desta spec bloqueia as specs 003 e 005.
