# 0002. Fazer o protótipo em HTML, CSS e JavaScript puros, sem etapa de build

- **Status:** Aceita
- **Data:** 12/11/2026

## Contexto

Precisávamos de um protótipo clicável para apresentar o Farol em sala e validar as telas com professores e alunos. A apresentação acontece em computadores da faculdade, às vezes sem internet confiável, e qualquer pessoa do grupo deve conseguir editar os dados de exemplo.

## Decisão

O protótipo é uma página única em HTML, CSS e JavaScript puros, sem framework e sem etapa de build. Abre direto do arquivo `index.html`, com fontes e ícones embutidos. As rotas usam o hash da URL, e o estado fica no `localStorage`. O visual usa os tokens e componentes do design system Farol.

## Alternativas consideradas

| Alternativa | Por que não |
| --- | --- |
| React + Vite, a mesma stack do produto | Exige Node.js e etapa de build para abrir; mais difícil para quem só quer editar os dados de exemplo |
| Ferramenta de protótipo (Figma) | Não permite simular o comportamento das duas visões conversando entre si, que é o ponto forte da demonstração |

## Consequências

- O protótipo abre com dois cliques e funciona sem internet.
- O código do protótipo não será reaproveitado no produto. O que se reaproveita são as telas, os textos, os dados de exemplo e os tokens do design system, que servem de especificação visual.
- O tutor do protótipo é simulado por palavras-chave e não representa a qualidade do tutor real.
