"""IA: a porta única para o provedor de IA (ADR 0005 e ADR 0007).

Nenhum outro módulo fala com o provedor: tudo passa por `ia.servicos`. O adaptador usado vem da
configuração FAROL_IA, e nos testes é sempre o adaptador falso, que não acessa a internet.
"""
