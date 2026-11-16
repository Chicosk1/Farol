"""Testes de scripts/verificar_specs.py, só com a biblioteca padrão (ACE-T18).

Uso: python3 -m unittest discover -s scripts
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

import verificar_specs as vs

SPEC = """\
# Especificação: Exemplo

| Campo | Valor |
| --- | --- |
| Código | `XYZ` |

## Requisitos

- **XYZ-RF-01**: O sistema DEVE fazer a primeira coisa.
- **XYZ-RF-02**: O sistema DEVE fazer a segunda coisa.
- **XYZ-RNF-01**: O sistema DEVE ser rápido.
"""

PLANO = """\
# Plano técnico: Exemplo

| Requisito | Cobertura | Como o protótipo faz |
| --- | --- | --- |
| XYZ-RF-01 | Coberto | Tela de exemplo |
| XYZ-RF-02 | Não coberto | |
"""

TAREFAS = """\
# Tarefas: Exemplo

- [x] XYZ-T01 Faz a primeira coisa (XYZ-RF-01)
- [ ] XYZ-T02 Faz a segunda coisa (XYZ-RF-02)
- [ ] XYZ-T03 Mede a velocidade (XYZ-RNF-01)
"""

TESTE_DO_BACKEND = '''\
import pytest


@pytest.mark.requisito("XYZ-RF-01")
def test_um():
    pass


@pytest.mark.requisito("XYZ-RF-01", "XYZ-RNF-01")
def test_dois():
    pass
'''


class ArvoreDeExemplo(unittest.TestCase):
    """Monta um repositório mínimo numa pasta temporária e aponta o script para ela."""

    def setUp(self) -> None:
        self._pasta = tempfile.TemporaryDirectory()
        self.raiz = Path(self._pasta.name)
        self.escrever("specs/001-exemplo/spec.md", SPEC)
        self.escrever("specs/001-exemplo/plan.md", PLANO)
        self.escrever("specs/001-exemplo/tasks.md", TAREFAS)
        self.escrever("prototipo/index.html", "<!doctype html>")
        self.escrever("prototipo/js/tela.js", "/* Specs: XYZ-RF-01. */")
        self.escrever("backend/modulo/testes/test_exemplo.py", TESTE_DO_BACKEND)
        vs.usar_raiz(self.raiz)
        vs.erros.clear()

    def tearDown(self) -> None:
        vs.usar_raiz(vs.RAIZ_DO_REPOSITORIO)
        vs.erros.clear()
        self._pasta.cleanup()

    def escrever(self, caminho: str, texto: str) -> None:
        arquivo = self.raiz / caminho
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_text(textwrap.dedent(texto), encoding="utf-8")

    def matriz(self) -> str:
        specs = vs.ler_specs()
        vs.verificar_specs(specs)
        no_codigo = vs.verificar_referencias(specs)
        testes = vs.ler_testes(specs)
        return vs.gerar_matriz(specs, no_codigo, testes)

    def linha_da_matriz(self, requisito: str) -> str:
        linhas = [linha for linha in self.matriz().splitlines() if linha.startswith(f"| `{requisito}`")]
        self.assertEqual(len(linhas), 1, f"a matriz deveria ter uma linha para {requisito}")
        return linhas[0]


class TestColunaTestes(ArvoreDeExemplo):
    def test_cabecalho_da_tabela_tem_a_coluna_testes(self) -> None:
        self.assertIn("| Requisito | Descrição | Protótipo | Código do protótipo | Testes |", self.matriz())

    def test_lista_o_arquivo_de_teste_com_a_quantidade_de_testes_do_requisito(self) -> None:
        linha = self.linha_da_matriz("XYZ-RF-01")

        self.assertIn("[modulo/testes/test_exemplo.py](../backend/modulo/testes/test_exemplo.py) (2)", linha)
        self.assertEqual(vs.erros, [])

    def test_requisito_sem_teste_fica_com_a_coluna_vazia(self) -> None:
        linha = self.linha_da_matriz("XYZ-RF-02")

        self.assertNotIn("test_exemplo.py", linha)

    def test_resumo_conta_os_requisitos_funcionais_com_teste(self) -> None:
        self.assertIn("| Com teste |", self.matriz())
        self.assertIn("| 1 de 2 |", self.matriz())


class TestMarcadoresInvalidos(ArvoreDeExemplo):
    def test_requisito_que_nao_existe_e_erro(self) -> None:
        self.escrever(
            "backend/modulo/testes/test_errado.py",
            '@pytest.mark.requisito("XYZ-RF-09")\ndef test_x():\n    pass\n',
        )

        self.matriz()

        self.assertTrue(any("XYZ-RF-09" in erro and "test_errado.py" in erro for erro in vs.erros), vs.erros)

    def test_marcador_sem_identificador_de_requisito_e_erro(self) -> None:
        self.escrever(
            "backend/modulo/testes/test_vazio.py",
            '@pytest.mark.requisito("primeira coisa")\ndef test_x():\n    pass\n',
        )

        self.matriz()

        self.assertTrue(any("test_vazio.py" in erro for erro in vs.erros), vs.erros)


if __name__ == "__main__":
    unittest.main()
