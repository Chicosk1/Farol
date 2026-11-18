"""Regras do radar da turma (spec 007). Só dados agregados e pseudônimos (princípio IV).

Nada aqui identifica alunos: as contagens usam o pseudônimo por disciplina, e um tópico ou uma
taxa só aparece com pelo menos 5 alunos distintos (RAD-RF-04, RAD-RF-06, RAD-RF-07).
"""

import hashlib
import logging
from collections import defaultdict
from datetime import date, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from disciplinas import servicos as disciplinas
from duvidas import servicos as duvidas
from materiais import servicos as materiais
from questoes import servicos as questoes
from tutor import servicos as tutor

from .models import ExemploOculto, RadarSemanal

logger = logging.getLogger(__name__)

MINIMO_DE_ALUNOS = 5  # RAD-RF-04 e RAD-RF-07
MAXIMO_DE_TOPICOS = 5  # RAD-RF-03
MAXIMO_DE_EXEMPLOS = 3
SUGERIDOS = 3  # RAD-RF-08
SEMANAS_NO_SELETOR = 12
ACERTO_PADRAO = 70  # um tópico sem taxa calculada não pesa como "errado" na sugestão


def segunda_da_semana(dia: date) -> date:
    return dia - timedelta(days=dia.weekday())


def semana_atual() -> date:
    return segunda_da_semana(timezone.localdate())


def rotulo_da_semana(segunda: date) -> str:
    domingo = segunda + timedelta(days=6)
    return f"Semana de {segunda:%d/%m} a {domingo:%d/%m}"


def semanas_disponiveis() -> list[dict]:
    """A atual e as anteriores, da mais recente para a mais antiga (RAD-RF-09)."""
    atual = semana_atual()
    return [
        {
            "semana": atual - timedelta(weeks=i),
            "rotulo": rotulo_da_semana(atual - timedelta(weeks=i)),
            "atual": i == 0,
        }
        for i in range(SEMANAS_NO_SELETOR)
    ]


def _hash(texto: str) -> str:
    return hashlib.sha256(" ".join(texto.lower().split()).encode()).hexdigest()


def ocultar_exemplo(disciplina_id: int, professor, texto: str) -> None:
    """O professor esconde uma pergunta de exemplo, e ela não volta (RAD-RF-05)."""
    ExemploOculto.objects.get_or_create(
        disciplina_id=disciplina_id, hash_texto=_hash(texto), defaults={"ocultado_por": professor}
    )
    RadarSemanal.objects.filter(disciplina_id=disciplina_id).delete()  # recalcula sem ele


def _nome_da_aula(aula) -> str:
    return f"Aula {aula.aula_numero} · {aula.aula_titulo}"


def calcular(disciplina_id: int, segunda: date) -> dict:
    """O radar de uma semana, a partir dos registros pseudônimos (RAD-RNF-02)."""
    domingo = segunda + timedelta(days=6)
    registros = tutor.registros_de_uso(disciplina_id, segunda, domingo)
    respostas = questoes.respostas_do_periodo(disciplina_id, segunda, domingo)
    ativos = {r["pseudonimo"] for r in registros} | {r["pseudonimo"] for r in respostas}
    abertas = duvidas.duvidas_para_o_professor(disciplina_id)
    respondentes = {r["pseudonimo"] for r in respostas}
    acerto_medio = (
        round(100 * sum(r["acerto"] for r in respostas) / len(respostas))
        if len(respondentes) >= MINIMO_DE_ALUNOS
        else None
    )
    indicadores = {
        "alunos_ativos": len(ativos),
        "matriculados": disciplinas.matriculados(disciplina_id),
        "perguntas": len(registros),
        "acerto_medio": acerto_medio,
        "duvidas_sem_resposta": len(abertas),
    }
    pouco_uso = len(ativos) < MINIMO_DE_ALUNOS
    dados = {
        "semana": segunda.isoformat(),
        "rotulo": rotulo_da_semana(segunda),
        "indicadores": indicadores,
        "pouco_uso": pouco_uso,
        "topicos": [],
        "acertos": [],
        "questoes_com_menor_acerto": [],
        "sugestao": [],
    }
    if pouco_uso:
        return dados

    # Tópicos com mais dúvidas: as perguntas agrupadas pela aula do trecho que as respondeu.
    trechos = {r["trechos"][0] for r in registros if r["trechos"]}
    aulas = materiais.aulas_dos_trechos(trechos)
    ocultos = set(
        ExemploOculto.objects.filter(disciplina_id=disciplina_id).values_list(
            "hash_texto", flat=True
        )
    )
    grupos: dict[int, dict] = {}
    for registro in registros:
        if not registro["trechos"] or registro["trechos"][0] not in aulas:
            continue
        aula = aulas[registro["trechos"][0]]
        grupo = grupos.setdefault(aula.id, {"aula": aula, "alunos": set(), "exemplos": []})
        grupo["alunos"].add(registro["pseudonimo"])
        texto = registro["pergunta"].strip()
        if (
            texto
            and _hash(texto) not in ocultos
            and texto not in grupo["exemplos"]
            and len(grupo["exemplos"]) < MAXIMO_DE_EXEMPLOS
        ):
            grupo["exemplos"].append(texto)
    topicos = sorted(
        (g for g in grupos.values() if len(g["alunos"]) >= MINIMO_DE_ALUNOS),
        key=lambda g: (-len(g["alunos"]), g["aula"].aula_numero),
    )[:MAXIMO_DE_TOPICOS]
    dados["topicos"] = [
        {
            "nome": _nome_da_aula(g["aula"]),
            "alunos": len(g["alunos"]),
            "exemplos": g["exemplos"],
            "material": g["aula"].id,
        }
        for g in topicos
    ]

    # Acerto por tópico e por questão, só com 5 alunos ou mais (RAD-RF-07).
    por_topico: dict[str, dict] = defaultdict(
        lambda: {"alunos": set(), "acertos": 0, "total": 0, "materiais": set()}
    )
    por_questao: dict[int, dict] = defaultdict(lambda: {"alunos": set(), "acertos": 0, "total": 0})
    for r in respostas:
        for grupo in (por_topico[r["topico"]], por_questao[r["questao"]]):
            grupo["alunos"].add(r["pseudonimo"])
            grupo["acertos"] += r["acerto"]
            grupo["total"] += 1
        por_topico[r["topico"]]["materiais"].add(r["material"])
        por_questao[r["questao"]]["enunciado"] = r["enunciado"]
    dados["acertos"] = sorted(
        (
            {
                "topico": topico,
                "taxa": round(100 * g["acertos"] / g["total"]),
                "alunos": len(g["alunos"]),
                "material": min(g["materiais"]),
            }
            for topico, g in por_topico.items()
            if len(g["alunos"]) >= MINIMO_DE_ALUNOS
        ),
        key=lambda a: (a["taxa"], a["topico"]),
    )
    dados["questoes_com_menor_acerto"] = sorted(
        (
            {"enunciado": g["enunciado"], "taxa": round(100 * g["acertos"] / g["total"])}
            for g in por_questao.values()
            if len(g["alunos"]) >= MINIMO_DE_ALUNOS
        ),
        key=lambda q: q["taxa"],
    )[:5]

    # Sugestão: as aulas com mais dúvidas e menor acerto (RAD-RF-08).
    taxa_da_aula: dict[int, list[int]] = defaultdict(list)
    for a in dados["acertos"]:
        taxa_da_aula[a["material"]].append(a["taxa"])
    candidatos: dict[int, dict] = {}
    for t in dados["topicos"]:
        candidatos[t["material"]] = {
            "nome": t["nome"],
            "material": t["material"],
            "alunos": t["alunos"],
        }
    nomes = materiais.aulas_dos_materiais(set(taxa_da_aula) - set(candidatos))
    for material_id, aula in nomes.items():
        candidatos[material_id] = {
            "nome": _nome_da_aula(aula),
            "material": material_id,
            "alunos": 0,
        }
    maximo = max([c["alunos"] for c in candidatos.values()] + [1])

    def pontos(c: dict) -> float:
        taxas = taxa_da_aula.get(c["material"])
        taxa = sum(taxas) / len(taxas) if taxas else ACERTO_PADRAO
        return c["alunos"] / maximo + (100 - taxa) / 100

    dados["sugestao"] = [
        {"nome": c["nome"], "material": c["material"]}
        for c in sorted(candidatos.values(), key=lambda c: (-pontos(c), c["nome"]))[:SUGERIDOS]
    ]
    return dados


def radar(disciplina_id: int, segunda: date) -> dict:
    """O radar da semana. A semana atual é recalculada na hora, porque ainda está mudando; as
    anteriores ficam guardadas depois do primeiro cálculo."""
    segunda = segunda_da_semana(segunda)
    guardado = RadarSemanal.objects.filter(disciplina_id=disciplina_id, semana=segunda).first()
    if guardado and segunda < semana_atual():
        return guardado.dados
    dados = calcular(disciplina_id, segunda)
    RadarSemanal.objects.update_or_create(
        disciplina_id=disciplina_id,
        semana=segunda,
        defaults={"dados": dados, "calculado_em": timezone.now()},
    )
    return dados


def calcular_todos() -> int:
    """Tarefa da madrugada: o radar da semana corrente de cada disciplina (RAD-RF-01)."""
    segunda = semana_atual()
    total = 0
    for disciplina_id in disciplinas.ids_de_todas():
        radar(disciplina_id, segunda)
        total += 1
    return total


def enviar_resumos() -> int:
    """Segunda de manhã: o resumo da semana anterior a cada professor com o resumo ligado
    (RAD-RF-10). Semana sem uso não gera e-mail."""
    segunda = semana_atual() - timedelta(weeks=1)
    enviados = 0
    desligadas = tutor.resumo_semanal_desligado()
    for disciplina_id in (d for d in disciplinas.ids_de_todas() if d not in desligadas):
        dados = calcular(disciplina_id, segunda)
        indicadores = dados["indicadores"]
        if not indicadores["alunos_ativos"]:
            continue
        nome, professor = disciplinas.disciplina_e_professor(disciplina_id)
        if not professor or not professor.email:
            continue
        linhas = [f"Radar de {nome}: {dados['rotulo']}.", ""]
        if dados["sugestao"]:
            linhas.append(
                "Sugestão para a próxima aula: "
                + ", ".join(s["nome"] for s in dados["sugestao"])
                + "."
            )
        if dados["topicos"]:
            linhas.append("Tópicos com mais dúvidas:")
            linhas += [f"- {t['nome']} ({t['alunos']} alunos)" for t in dados["topicos"]]
        linhas.append(f"Dúvidas sem resposta: {indicadores['duvidas_sem_resposta']}.")
        linhas += [
            "",
            f"Abra o radar: {settings.FAROL_ENDERECO_PUBLICO}/disciplinas/{disciplina_id}/radar",
        ]
        send_mail(f"Radar da semana: {nome}", "\n".join(linhas), None, [professor.email])
        enviados += 1
    return enviados
