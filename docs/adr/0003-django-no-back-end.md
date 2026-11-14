# 0003. Usar Python com Django e Django REST Framework no back-end

- **Status:** Proposta
- **Data:** 12/11/2026

## Contexto

O back-end precisa de login institucional, controle de permissões por disciplina, cadastro de turmas, uma API para o front-end e integração com bibliotecas de IA e de leitura de PDF. A equipe é pequena e pode incluir alunos de extensão.

## Decisão

Python com Django na versão LTS e Django REST Framework para a API. O painel administrativo do Django serve de tela de gestão para a TI.

## Alternativas consideradas

| Alternativa | Prós | Contras |
| --- | --- | --- |
| FastAPI | Mais leve e rápido, tipagem forte | Login, ORM, migrações e painel administrativo precisam ser montados à parte |
| Node.js com NestJS | Mesma linguagem do front-end | Ecossistema de IA e de PDF mais fraco que o de Python |

## Consequências

- Login, ORM, migrações e painel administrativo prontos, sem código extra.
- Python é a linguagem padrão de IA e de leitura de PDF.
- O projeto passa a ter duas linguagens (TypeScript e Python).
- Django é mais opinativo e pesado que FastAPI, o que é aceitável para o volume esperado.
