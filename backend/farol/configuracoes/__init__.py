"""Configurações por ambiente.

- `base`: o que vale em todos os ambientes.
- `desenvolvimento`: Docker Compose na máquina de quem desenvolve (padrão do manage.py).
- `teste`: pytest, localmente e no GitHub Actions.
- `producao`: servidor; toda configuração sensível vem de variáveis de ambiente obrigatórias.
"""
