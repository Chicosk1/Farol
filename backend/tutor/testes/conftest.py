import pytest

from tutor import contador


@pytest.fixture(autouse=True)
def contador_zerado():
    """Cada teste começa sem perguntas contadas. Os testes usam um banco separado do Redis."""
    contador.cliente().flushdb()
    yield
    contador.cliente().flushdb()
