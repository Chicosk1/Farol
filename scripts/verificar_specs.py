#!/usr/bin/env python3
"""Verifica as especificações do Farol e gera a matriz de rastreabilidade.

Uso:
    python3 scripts/verificar_specs.py           verifica tudo (é o que o GitHub Actions roda)
    python3 scripts/verificar_specs.py --gerar   regrava docs/rastreabilidade.md e depois verifica

O que é verificado:
    1. Cada pasta specs/NNN-nome tem spec.md, plan.md e tasks.md.
    2. Cada spec declara um código de três letras, único no projeto.
    3. Os identificadores de requisito (XXX-RF-01, XXX-RNF-01, XXX-CS-01) e de tarefa (XXX-T01)
       são únicos e usam o código da spec.
    4. Todo requisito funcional aparece na tabela de cobertura do plan.md e em pelo menos uma tarefa.
    5. Todo identificador citado em documentos ou no código existe em alguma spec.
    6. Os links relativos dos arquivos Markdown apontam para arquivos e títulos que existem.
    7. docs/rastreabilidade.md está atualizada.
    8. Os marcadores @pytest.mark.requisito("XXX-RF-01") dos testes do back-end citam requisitos
       que existem. A matriz mostra, para cada requisito, os testes que o verificam.

Só usa a biblioteca padrão do Python 3. Os testes deste script estão em scripts/test_verificar_specs.py.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parent.parent
ARQUIVOS_DA_SPEC = ("spec.md", "plan.md", "tasks.md")
COBERTURAS = ("Coberto", "Simulado", "Parcial", "Não coberto")
# Pastas que nunca são lidas: dependências, caches e builds.
PASTAS_IGNORADAS = {".git", "node_modules", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__", "dist", "build"}

# Caminhos do repositório verificado. São definidos por usar_raiz(), no fim deste bloco.
RAIZ = RAIZ_DO_REPOSITORIO
PASTA_SPECS = MATRIZ = PROTOTIPO = PASTA_BACKEND = RAIZ
PASTAS_DE_CODIGO: tuple[Path, ...] = ()


def usar_raiz(raiz: Path) -> None:
    """Aponta o script para um repositório. Os testes do script usam uma pasta temporária."""
    global RAIZ, PASTA_SPECS, MATRIZ, PROTOTIPO, PASTAS_DE_CODIGO, PASTA_BACKEND
    RAIZ = raiz
    PASTA_SPECS = raiz / "specs"
    MATRIZ = raiz / "docs" / "rastreabilidade.md"
    PROTOTIPO = raiz / "prototipo"
    PASTAS_DE_CODIGO = (PROTOTIPO / "js",)
    PASTA_BACKEND = raiz / "backend"


usar_raiz(RAIZ_DO_REPOSITORIO)

RE_PASTA = re.compile(r"^(\d{3})-[a-z0-9-]+$")
RE_CODIGO = re.compile(r"^\| Código \| `([A-Z]{3})` ", re.M)
RE_TITULO = re.compile(r"^# Especificação: (.+)$", re.M)
RE_REQUISITO = re.compile(r"^- \*\*([A-Z]{3}-(?:RF|RNF|CS)-\d{2})\*\*: (.+)$", re.M)
RE_REQUISITO_RETIRADO = re.compile(r"^- ~~\*\*([A-Z]{3}-(?:RF|RNF|CS)-\d{2})\*\*", re.M)
RE_TAREFA = re.compile(r"^- \[( |x)\] ([A-Z]{3}-T\d{2}) (.+)$", re.M)
RE_COBERTURA = re.compile(r"^\| ([A-Z]{3}-RF-\d{2}) \|([^|]*)\|(.*)\|$", re.M)
RE_ID = re.compile(r"\b[A-Z]{3}-(?:RF|RNF|CS)-\d{2}\b|\b[A-Z]{3}-T\d{2}\b")
RE_ID_REQUISITO = re.compile(r"\b[A-Z]{3}-(?:RF|RNF|CS)-\d{2}\b")
RE_MARCADOR_REQUISITO = re.compile(r"pytest\.mark\.requisito\(([^)]*)\)")
RE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)|<img [^>]*src=\"([^\"]+)\"")
RE_ESCLARECER = re.compile(r"\[PRECISA ESCLARECER")
RE_TITULO_MD = re.compile(r"^(#{1,6}) (.+?)\s*$", re.M)


@dataclass
class Spec:
    pasta: Path
    numero: str
    codigo: str = ""
    titulo: str = ""
    requisitos: dict[str, str] = field(default_factory=dict)
    retirados: set[str] = field(default_factory=set)
    cobertura: dict[str, tuple[str, str]] = field(default_factory=dict)
    tarefas: dict[str, tuple[bool, str]] = field(default_factory=dict)
    pendencias_prototipo: list[str] = field(default_factory=list)
    esclarecer: int = 0


erros: list[str] = []


def erro(mensagem: str) -> None:
    erros.append(mensagem)


def rel(caminho: Path) -> str:
    return caminho.relative_to(RAIZ).as_posix()


def ler_specs() -> list[Spec]:
    specs: list[Spec] = []
    for pasta in sorted(p for p in PASTA_SPECS.iterdir() if p.is_dir()):
        nome = RE_PASTA.match(pasta.name)
        if not nome:
            erro(f"{rel(pasta)}: o nome da pasta deve seguir o formato NNN-nome-curto")
            continue
        faltando = [a for a in ARQUIVOS_DA_SPEC if not (pasta / a).is_file()]
        if faltando:
            erro(f"{rel(pasta)}: faltam {', '.join(faltando)}")
            continue
        spec = Spec(pasta=pasta, numero=nome.group(1))
        texto_spec = (pasta / "spec.md").read_text(encoding="utf-8")
        texto_plano = (pasta / "plan.md").read_text(encoding="utf-8")
        texto_tarefas = (pasta / "tasks.md").read_text(encoding="utf-8")

        codigo = RE_CODIGO.search(texto_spec)
        titulo = RE_TITULO.search(texto_spec)
        if not codigo:
            erro(f"{rel(pasta)}/spec.md: falta a linha | Código | `XXX` | na tabela do topo")
            continue
        spec.codigo = codigo.group(1)
        spec.titulo = titulo.group(1).strip() if titulo else pasta.name
        spec.esclarecer = len(RE_ESCLARECER.findall(texto_spec))

        for ident, texto in RE_REQUISITO.findall(texto_spec):
            if ident in spec.requisitos:
                erro(f"{rel(pasta)}/spec.md: {ident} declarado duas vezes")
            if not ident.startswith(spec.codigo + "-"):
                erro(f"{rel(pasta)}/spec.md: {ident} não usa o código {spec.codigo}")
            spec.requisitos[ident] = texto.strip()
        spec.retirados.update(RE_REQUISITO_RETIRADO.findall(texto_spec))

        for ident, cobertura, como in RE_COBERTURA.findall(texto_plano):
            cobertura = cobertura.strip()
            if cobertura not in COBERTURAS:
                erro(f"{rel(pasta)}/plan.md: cobertura '{cobertura}' de {ident} deve ser uma de: {', '.join(COBERTURAS)}")
            spec.cobertura[ident] = (cobertura, como.strip())

        secao = ""
        for linha in texto_tarefas.splitlines():
            if linha.startswith("#"):
                secao = linha.lstrip("# ").strip()
            tarefa = RE_TAREFA.match(linha)
            if not tarefa:
                continue
            feita, ident, texto = tarefa.group(1) == "x", tarefa.group(2), tarefa.group(3)
            if ident in spec.tarefas:
                erro(f"{rel(pasta)}/tasks.md: {ident} aparece duas vezes")
            if not ident.startswith(spec.codigo + "-"):
                erro(f"{rel(pasta)}/tasks.md: {ident} não usa o código {spec.codigo}")
            spec.tarefas[ident] = (feita, texto)
            if secao == "Pendências do protótipo" and not feita:
                spec.pendencias_prototipo.append(ident)
        specs.append(spec)
    return specs


def verificar_specs(specs: list[Spec]) -> None:
    vistos: dict[str, str] = {}
    for spec in specs:
        if spec.codigo in vistos:
            erro(f"{rel(spec.pasta)}: o código {spec.codigo} já é usado por {vistos[spec.codigo]}")
        vistos[spec.codigo] = rel(spec.pasta)
        funcionais = [r for r in spec.requisitos if "-RF-" in r]
        if not funcionais:
            erro(f"{rel(spec.pasta)}/spec.md: nenhum requisito funcional declarado")
        for ident in funcionais:
            if ident not in spec.cobertura:
                erro(f"{rel(spec.pasta)}/plan.md: {ident} não está na tabela 'Como o protótipo implementa'")
            if not any(ident in texto for _, texto in spec.tarefas.values()):
                erro(f"{rel(spec.pasta)}/tasks.md: nenhuma tarefa cita {ident}")
        for ident in spec.cobertura:
            if ident not in spec.requisitos:
                erro(f"{rel(spec.pasta)}/plan.md: {ident} está na cobertura mas não existe na spec")


def arquivos_markdown() -> list[Path]:
    return sorted(
        p for p in RAIZ.rglob("*.md")
        if not PASTAS_IGNORADAS.intersection(p.relative_to(RAIZ).parts) and "templates" not in p.parts
    )


def arquivos_de_teste() -> list[Path]:
    """Testes do back-end: backend/<modulo>/testes/test_*.py."""
    if not PASTA_BACKEND.is_dir():
        return []
    return sorted(
        p for p in PASTA_BACKEND.rglob("test_*.py")
        if "testes" in p.relative_to(PASTA_BACKEND).parts
        and not PASTAS_IGNORADAS.intersection(p.relative_to(RAIZ).parts)
    )


def ler_testes(specs: list[Spec]) -> dict[str, dict[str, int]]:
    """Lê os marcadores @pytest.mark.requisito(...) dos testes do back-end.

    Devolve, para cada requisito, quantos testes de cada arquivo o verificam.
    """
    requisitos: set[str] = set()
    retirados: set[str] = set()
    for spec in specs:
        requisitos.update(spec.requisitos)
        retirados.update(spec.retirados)
    testes: dict[str, dict[str, int]] = {}
    for arquivo in arquivos_de_teste():
        for argumentos in RE_MARCADOR_REQUISITO.findall(arquivo.read_text(encoding="utf-8")):
            idents = RE_ID_REQUISITO.findall(argumentos)
            if not idents:
                erro(f"{rel(arquivo)}: o marcador requisito({argumentos}) não cita nenhum requisito (XXX-RF-01)")
            for ident in idents:
                if ident in retirados:
                    erro(f"{rel(arquivo)}: o marcador requisito cita {ident}, que foi retirado da spec")
                elif ident not in requisitos:
                    erro(f"{rel(arquivo)}: o marcador requisito cita {ident}, que não existe em nenhuma spec")
                else:
                    por_arquivo = testes.setdefault(ident, {})
                    por_arquivo[rel(arquivo)] = por_arquivo.get(rel(arquivo), 0) + 1
    return testes


def arquivos_de_codigo() -> list[Path]:
    """Arquivos do protótipo em que o script procura os comentários `Specs:`."""
    pagina = PROTOTIPO / "index.html"
    if not pagina.is_file():
        erro(f"{rel(pagina)} não existe: o protótipo deve ficar na pasta {rel(PROTOTIPO)}/")
    arquivos = [pagina]
    for pasta in PASTAS_DE_CODIGO:
        if not pasta.is_dir():
            erro(f"{rel(pasta)}/ não existe: o código do protótipo deve ficar em {rel(PROTOTIPO)}/")
            continue
        arquivos.extend(sorted(pasta.rglob("*.js")))
    return [a for a in arquivos if a.is_file()]


def ids_conhecidos(specs: list[Spec]) -> set[str]:
    conhecidos: set[str] = set()
    for spec in specs:
        conhecidos.update(spec.requisitos)
        conhecidos.update(spec.retirados)
        conhecidos.update(spec.tarefas)
    return conhecidos


def verificar_referencias(specs: list[Spec]) -> dict[str, list[str]]:
    """Confere se todo identificador citado existe. Devolve, para cada requisito, os arquivos de código que o citam."""
    conhecidos = ids_conhecidos(specs)
    no_codigo: dict[str, list[str]] = {}
    for arquivo in arquivos_markdown() + arquivos_de_codigo():
        if arquivo == MATRIZ:
            continue
        texto = arquivo.read_text(encoding="utf-8")
        for ident in sorted(set(RE_ID.findall(texto))):
            if ident not in conhecidos:
                erro(f"{rel(arquivo)}: cita {ident}, que não existe em nenhuma spec")
            elif arquivo.suffix in (".js", ".html"):
                no_codigo.setdefault(ident, []).append(rel(arquivo))
    return no_codigo


def ancora_github(titulo: str) -> str:
    titulo = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", titulo)
    titulo = titulo.replace("`", "").strip().lower()
    titulo = re.sub(r"[^\w\- ]", "", titulo)
    return titulo.replace(" ", "-")


def ancoras(arquivo: Path) -> set[str]:
    texto = arquivo.read_text(encoding="utf-8")
    texto = re.sub(r"```.*?```", "", texto, flags=re.S)
    contagem: dict[str, int] = {}
    resultado: set[str] = set()
    for _, titulo in RE_TITULO_MD.findall(texto):
        base = ancora_github(titulo)
        n = contagem.get(base, 0)
        resultado.add(base if n == 0 else f"{base}-{n}")
        contagem[base] = n + 1
    return resultado


def verificar_links() -> None:
    for arquivo in arquivos_markdown():
        texto = arquivo.read_text(encoding="utf-8")
        texto = re.sub(r"```.*?```", "", texto, flags=re.S)
        for grupo in RE_LINK.findall(texto):
            destino = grupo[0] or grupo[1]
            if re.match(r"^[a-z]+:", destino):
                continue
            caminho, _, ancora = destino.partition("#")
            alvo = (arquivo.parent / caminho).resolve() if caminho else arquivo
            if not alvo.exists():
                erro(f"{rel(arquivo)}: link quebrado para {destino}")
            elif ancora and alvo.suffix == ".md" and ancora not in ancoras(alvo):
                erro(f"{rel(arquivo)}: o título #{ancora} não existe em {rel(alvo)}")


def celula(texto: str) -> str:
    """Prepara um texto da spec para uma célula da matriz: tira links relativos e escapa barras verticais."""
    texto = re.sub(r"\[([^\]]*)\]\((?![a-z]+:)[^)]*\)", r"\1", texto)
    return texto.replace("|", "\\|")


def celula_de_testes(arquivos: dict[str, int]) -> str:
    """Links para os arquivos de teste de um requisito, com a quantidade de testes de cada um."""
    return ", ".join(
        f"[{caminho.removeprefix('backend/')}](../{caminho}) ({quantidade})"
        for caminho, quantidade in sorted(arquivos.items())
    )


def gerar_matriz(specs: list[Spec], no_codigo: dict[str, list[str]], testes: dict[str, dict[str, int]]) -> str:
    linhas = [
        "# Matriz de rastreabilidade",
        "",
        "Gerada por `scripts/verificar_specs.py --gerar` a partir das specs, dos planos, das tarefas, dos comentários `Specs:` no código do protótipo e dos marcadores `requisito` nos testes do back-end. Não edite à mão: mude a fonte e rode o script de novo.",
        "",
        "Legenda da coluna Protótipo: **Coberto** funciona como no produto, com dados fictícios; **Simulado** a tela existe, mas o comportamento por trás é encenado com dados fixos; **Parcial** cobre parte do requisito; **Não coberto** ainda não existe no protótipo.",
        "",
        "A coluna Testes mostra os testes do produto que citam o requisito com `@pytest.mark.requisito`, e quantos são em cada arquivo ([qualidade e testes](qualidade-e-testes.md)).",
        "",
        "## Resumo",
        "",
        "| Spec | Requisitos funcionais | Com teste | Coberto | Simulado | Parcial | Não coberto | Tarefas feitas | Pontos a esclarecer |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for spec in specs:
        funcionais = [r for r in spec.requisitos if "-RF-" in r]
        contagem = {c: sum(1 for r in funcionais if spec.cobertura.get(r, ("",))[0] == c) for c in COBERTURAS}
        com_teste = sum(1 for r in funcionais if r in testes)
        feitas = sum(1 for feita, _ in spec.tarefas.values() if feita)
        link = f"[{spec.numero} {spec.titulo}](../specs/{spec.pasta.name}/spec.md)"
        linhas.append(
            f"| {link} | {len(funcionais)} | {com_teste} de {len(funcionais)} | {contagem['Coberto']} "
            f"| {contagem['Simulado']} | {contagem['Parcial']} "
            f"| {contagem['Não coberto']} | {feitas} de {len(spec.tarefas)} | {spec.esclarecer} |"
        )

    pendencias = [(spec, ident) for spec in specs for ident in spec.pendencias_prototipo]
    if pendencias:
        linhas += ["", "## Pendências do protótipo", "", "Tarefas já especificadas que aproximam o protótipo do comportamento descrito nas specs:", ""]
        for spec, ident in pendencias:
            texto = spec.tarefas[ident][1]
            linhas.append(f"- `{ident}` {texto} ([tarefas](../specs/{spec.pasta.name}/tasks.md))")

    for spec in specs:
        linhas += [
            "",
            f"## {spec.numero} {spec.titulo}",
            "",
            "| Requisito | Descrição | Protótipo | Código do protótipo | Testes | Tarefas feitas | Tarefas pendentes |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for ident, texto in spec.requisitos.items():
            if "-RF-" not in ident:
                continue
            cobertura = spec.cobertura.get(ident, ("?", ""))[0]
            codigo = ", ".join(f"[{Path(a).name}](../{a})" for a in no_codigo.get(ident, [])) or ""
            de_teste = celula_de_testes(testes.get(ident, {}))
            feitas = ", ".join(t for t, (f, d) in spec.tarefas.items() if f and ident in d)
            pendentes = ", ".join(t for t, (f, d) in spec.tarefas.items() if not f and ident in d)
            linhas.append(
                f"| `{ident}` | {celula(texto)} | {cobertura} | {codigo} | {de_teste} | {feitas} | {pendentes} |"
            )
    return "\n".join(linhas) + "\n"


def main() -> int:
    gerar = "--gerar" in sys.argv[1:]
    specs = ler_specs()
    verificar_specs(specs)
    no_codigo = verificar_referencias(specs)
    testes = ler_testes(specs)

    matriz = gerar_matriz(specs, no_codigo, testes)
    if gerar:
        MATRIZ.write_text(matriz, encoding="utf-8")
        print(f"Matriz gravada em {rel(MATRIZ)}.")
    elif not MATRIZ.is_file() or MATRIZ.read_text(encoding="utf-8") != matriz:
        erro(f"{rel(MATRIZ)} está desatualizada. Rode: python3 scripts/verificar_specs.py --gerar")
    verificar_links()

    total_req = sum(len(s.requisitos) for s in specs)
    total_tarefas = sum(len(s.tarefas) for s in specs)
    esclarecer = sum(s.esclarecer for s in specs)
    print(f"{len(specs)} specs, {total_req} requisitos, {total_tarefas} tarefas, {esclarecer} pontos a esclarecer.")
    if erros:
        print(f"\n{len(erros)} problema(s):")
        for mensagem in erros:
            print(f"  - {mensagem}")
        return 1
    print("Tudo certo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
