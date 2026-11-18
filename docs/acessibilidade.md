# Auditoria de acessibilidade

Auditoria das telas das specs 001 a 004 (ACE-T90, ACE-RNF-01, princípio V da constituição), feita em
2026-11-17. Meta: WCAG 2.2 nível AA.

## O que é verificado automaticamente, a cada commit

| Verificação | Como | Onde |
| --- | --- | --- |
| Regras do axe-core (nomes acessíveis, rótulos, papéis ARIA, hierarquia, listas) | Um teste com `violacoesDeAcessibilidade` em cada tela | `frontend/src/**/*.test.tsx` |
| Contraste de texto (mínimo 4,5:1) nos temas claro e escuro | Fórmula da WCAG sobre os pares de cores do design system | `frontend/src/estilos/contraste.test.ts` |
| Teclado: abas com setas, Home e End; modal com foco preso, Esc e foco devolvido; sino com Esc | Testes de tela | `componentes/Abas`, `tutor.test.tsx`, `sino.test.tsx` |
| Resposta do tutor anunciada só quando termina (`aria-live`) | Teste de tela | `tutor.test.tsx` |
| Respostas mostradas como texto, sem interpretar HTML | Teste de tela | `tutor.test.tsx` |

## Telas auditadas

| Tela | Situação |
| --- | --- |
| Entrada, início, disciplinas (abas, busca, favoritas) | Sem pendências |
| Aviso de privacidade | Sem pendências; bloqueia o resto da página com `inert` |
| Tutor da aluna (conversa, citações, avaliação, política, dúvida) | Corrigido nesta auditoria: o modal da dúvida passou a prender o foco e a devolvê-lo ao botão |
| Trecho citado | Sem pendências; o trecho usa `mark` |
| Materiais (professor e aluna) | Sem pendências; a área de arrastar tem o campo de arquivo rotulado como alternativa |
| Configuração do tutor e provas | Sem pendências |
| Dúvidas do professor | Sem pendências |
| Sino de notificações | Corrigido nesta auditoria: Esc fecha a lista e devolve o foco |
| Meus dados | Sem pendências; apagar pede confirmação |

## O que ainda precisa de pessoas

- Teste com leitores de tela reais: NVDA no Windows, VoiceOver no iPhone e TalkBack no Android.
- Teste com zoom de 200% e com a fonte do celular aumentada.
- Teste com alunos e professores do piloto, inclusive quem usa tecnologia assistiva.
