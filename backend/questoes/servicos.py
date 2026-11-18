"""Regras do módulo questoes (spec 005). Chamado pela API, pelas tarefas e por outros módulos."""

import logging

from celery import current_app
from django.db import models, transaction
from django.utils import timezone

from contas.servicos import Perfil
from disciplinas import servicos as disciplinas
from ia import servicos as ia
from ia.servicos import TrechoNumerado
from materiais import servicos as materiais
from nucleo.pseudonimo import pseudonimo_do_aluno
from tutor import servicos as tutor

from .esquema import ler_questoes, validar_edicao
from .models import (
    QUANTIDADE_MAXIMA,
    QUANTIDADE_MINIMA,
    PedidoGeracao,
    ProgressoQuiz,
    Questao,
    RespostaQuiz,
)

logger = logging.getLogger(__name__)

TRECHOS_POR_PEDIDO = 30  # cabe no contexto do modelo e cobre a aula toda
TAMANHO_MINIMO_DO_TRECHO = 40  # títulos e rodapés soltos não rendem questão

# Instruções fixas do modelo: o professor não as edita, e o servidor confere o resultado.
REGRAS_DAS_QUESTOES = """Você cria questões de múltipla escolha para alunos de graduação, só com o \
conteúdo dos trechos numerados do material de uma aula.

Regras:
1. Cada questão tem um enunciado, exatamente 4 alternativas, uma só correta, uma justificativa \
curta e o tópico (de 2 a 5 palavras).
2. Use só o que está nos trechos. Não invente fatos nem use conhecimento de fora.
3. Em "trecho", ponha o número do trecho de onde saiu a resposta correta.
4. As alternativas erradas devem ser plausíveis, mas erradas segundo o material.
5. Em "correta", ponha a posição da alternativa correta, de 0 a 3, variando entre as questões.
6. Escreva em português do Brasil.

Responda só com um JSON neste formato:
{"questoes": [{"enunciado": "...", "alternativas": ["...", "...", "...", "..."], \
"correta": 0, "justificativa": "...", "topico": "...", "trecho": 1}]}"""


class NaoEncontrado(LookupError):
    """A aula ou o pedido não existe."""


class SemAcesso(PermissionError):
    """Só o professor da disciplina cuida das questões dela."""


class AulaNaoPronta(Exception):
    """A aula ainda está em processamento, deu erro ou foi retirada (QUE-RF-01)."""


class QuantidadeInvalida(ValueError):
    """O professor pede de 5 a 20 questões por vez (QUE-RF-01)."""


def _cuida_da_disciplina(pessoa, perfil: str | None, disciplina_id: int) -> bool:
    return perfil == Perfil.PROFESSOR and disciplinas.tem_acesso(pessoa, perfil, disciplina_id)


def enfileirar_geracao(pedido_id: int) -> None:
    """Põe a geração na fila do Celery, pelo nome: a camada de serviços não importa a de tarefas."""
    current_app.signature("questoes.gerar", args=(pedido_id,)).apply_async()


def pedir_geracao(pessoa, perfil: str | None, material_id: int, quantidade: int) -> PedidoGeracao:
    """Cria o pedido de rascunhos de uma aula pronta. Quem chama põe a geração na fila.

    Se já há um pedido em andamento para a aula, devolve esse: tocar duas vezes em "Gerar
    rascunhos" não gera o dobro.
    """
    try:
        aula = materiais.resumo_do_material(material_id)
    except materiais.MaterialNaoEncontrado:
        raise NaoEncontrado(material_id) from None
    if not _cuida_da_disciplina(pessoa, perfil, aula.disciplina_id):
        raise SemAcesso(material_id)
    if not QUANTIDADE_MINIMA <= quantidade <= QUANTIDADE_MAXIMA:
        raise QuantidadeInvalida(quantidade)
    if not aula.pronto:
        raise AulaNaoPronta(material_id)
    em_andamento = PedidoGeracao.objects.filter(
        material_id=material_id, status=PedidoGeracao.Status.PROCESSANDO
    ).first()
    if em_andamento:
        return em_andamento
    return PedidoGeracao.objects.create(
        material_id=material_id, quantidade=quantidade, pedido_por=pessoa
    )


def pedido_para_ver(pessoa, perfil: str | None, pedido_id: int) -> PedidoGeracao:
    """O pedido, para o professor da disciplina acompanhar a geração."""
    try:
        pedido = PedidoGeracao.objects.select_related("material").get(pk=pedido_id)
    except PedidoGeracao.DoesNotExist:
        raise NaoEncontrado(pedido_id) from None
    if not _cuida_da_disciplina(pessoa, perfil, pedido.material.disciplina_id):
        raise SemAcesso(pedido_id)
    return pedido


class QuestaoInvalida(ValueError):
    def __init__(self, erros: dict[str, str]):
        super().__init__(erros)
        self.erros = erros


class MudancaNaoPermitida(Exception):
    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


StatusDaQuestao = Questao.Status
# Para onde cada status pode ir (QUE-RF-05). Publicar só a partir de pendente: o que foi
# descartado volta para pendentes e é revisto antes.
MUDANCAS = {
    StatusDaQuestao.PENDENTE: {StatusDaQuestao.PUBLICADA, StatusDaQuestao.DESCARTADA},
    StatusDaQuestao.PUBLICADA: {StatusDaQuestao.PENDENTE},
    StatusDaQuestao.DESCARTADA: {StatusDaQuestao.PENDENTE},
}
CAMPOS_EDITAVEIS = ("enunciado", "alternativas", "correta", "justificativa", "topico")
MATERIAL_RETIRADO = "retirado"


def questoes_da_disciplina(disciplina_id: int, status: str, material_id: int | None = None):
    """As questões de um status, com a aula e o trecho, e a contagem de cada status (QUE-RF-06).

    Só para o professor: a rota confere o acesso. A mais nova vem primeiro.
    """
    todas = Questao.objects.filter(material__disciplina_id=disciplina_id)
    if material_id is not None:
        todas = todas.filter(material_id=material_id)
    contagens = {s: 0 for s in StatusDaQuestao.values}
    for linha in todas.values("status").annotate(total=models.Count("id")):
        contagens[linha["status"]] = linha["total"]
    lista = (
        todas.filter(status=status)
        .select_related("material", "trecho")
        .order_by("-criada_em", "-id")
    )
    return contagens, lista


def origem_retirada(questao: Questao) -> bool:
    """O material de origem foi retirado: o professor decide o que fazer com a questão."""
    return questao.material.status == MATERIAL_RETIRADO


def _questao_do_professor(pessoa, perfil: str | None, questao_id: int) -> Questao:
    try:
        questao = Questao.objects.select_related("material", "trecho").get(pk=questao_id)
    except Questao.DoesNotExist:
        raise NaoEncontrado(questao_id) from None
    if not _cuida_da_disciplina(pessoa, perfil, questao.material.disciplina_id):
        raise SemAcesso(questao_id)
    return questao


def mudar_questao(pessoa, perfil: str | None, questao_id: int, dados: dict) -> Questao:
    """Edita o conteúdo e, ou, muda o status de uma questão (QUE-RF-05).

    A edição só vale em pendentes: uma questão publicada volta para pendentes antes de ser
    editada, para nada mudar para a turma sem nova aprovação (decisão da spec 005). Uma questão
    cujo material foi retirado não pode ser publicada.
    """
    questao = _questao_do_professor(pessoa, perfil, questao_id)
    edicao = {campo: dados[campo] for campo in CAMPOS_EDITAVEIS if campo in dados}
    novo_status = dados.get("status")
    if edicao:
        if questao.status != StatusDaQuestao.PENDENTE:
            raise MudancaNaoPermitida(
                "Volte a questão para pendentes antes de editar: assim nada muda para a turma "
                "sem uma nova aprovação."
            )
        atual = {campo: getattr(questao, campo) for campo in CAMPOS_EDITAVEIS}
        conteudo, erros = validar_edicao(atual | edicao)
        if erros:
            raise QuestaoInvalida(erros)
        mudou = False
        for campo, valor in conteudo.model_dump().items():
            if getattr(questao, campo) != valor:
                setattr(questao, campo, valor)
                mudou = True
        questao.editada = questao.editada or mudou
    if novo_status and novo_status != questao.status:
        if novo_status not in MUDANCAS[questao.status]:
            raise MudancaNaoPermitida("Esta mudança de status não é permitida.")
        if novo_status == StatusDaQuestao.PUBLICADA and origem_retirada(questao):
            raise MudancaNaoPermitida(
                "O material desta questão foi retirado: ela não pode ser publicada."
            )
        questao.status = novo_status
    questao.nova = False  # o professor já mexeu: deixa de ser "novo rascunho"
    questao.save()
    return questao


def _terminar(pedido: PedidoGeracao, status: str, geradas: int = 0, descartadas: int = 0) -> None:
    pedido.status = status
    pedido.geradas = geradas
    pedido.descartadas = descartadas
    pedido.terminado_em = timezone.now()
    pedido.save(update_fields=["status", "geradas", "descartadas", "terminado_em"])


def processar_pedido(pedido_id: int) -> PedidoGeracao:
    """Gera os rascunhos do pedido e guarda só os que passam na validação (QUE-RF-02 e 03).

    Os rascunhos entram todos de uma vez, ou nenhum: o professor nunca vê um lote pela metade.
    Sem nenhum rascunho válido, o pedido termina com erro e o professor pode tentar de novo.
    """
    pedido = PedidoGeracao.objects.get(pk=pedido_id)
    if pedido.status != PedidoGeracao.Status.PROCESSANDO:
        return pedido  # já processado: a tarefa pode ser entregue duas vezes
    trechos = [
        trecho
        for trecho in materiais.trechos_da_aula(pedido.material_id, TRECHOS_POR_PEDIDO * 2)
        if len(trecho.texto.strip()) >= TAMANHO_MINIMO_DO_TRECHO
    ][:TRECHOS_POR_PEDIDO]
    if not trechos:
        _terminar(pedido, PedidoGeracao.Status.ERRO)
        return pedido
    por_numero = {numero: trecho for numero, trecho in enumerate(trechos, start=1)}
    numerados = [TrechoNumerado(numero, t.texto) for numero, t in por_numero.items()]
    try:
        texto = ia.gerar_questoes(REGRAS_DAS_QUESTOES, numerados, pedido.quantidade)
    except Exception:  # provedor fora do ar ou com erro: o professor tenta de novo
        logger.exception("Falha ao gerar as questões do pedido %s", pedido.id)
        _terminar(pedido, PedidoGeracao.Status.ERRO)
        return pedido
    leitura = ler_questoes(texto, set(por_numero), pedido.quantidade)
    with transaction.atomic():
        Questao.objects.bulk_create(
            Questao(
                material_id=pedido.material_id,
                pedido=pedido,
                enunciado=gerada.enunciado,
                alternativas=gerada.alternativas,
                correta=gerada.correta,
                justificativa=gerada.justificativa,
                topico=gerada.topico,
                trecho_id=por_numero[gerada.trecho].id,
            )
            for gerada in leitura.aceitas
        )
        status = PedidoGeracao.Status.PRONTO if leitura.aceitas else PedidoGeracao.Status.ERRO
        _terminar(pedido, status, len(leitura.aceitas), leitura.descartadas)
    return pedido


# --- Quiz do aluno (história 3) ---


class QuizPausado(Exception):
    """O tutor da disciplina está em modo prova: o quiz também fica pausado (spec 006)."""


def _aula_do_aluno(pessoa, perfil: str | None, material_id: int):
    try:
        aula = materiais.resumo_do_material(material_id)
    except materiais.MaterialNaoEncontrado:
        raise NaoEncontrado(material_id) from None
    if perfil != Perfil.ALUNO or not disciplinas.tem_acesso(pessoa, perfil, aula.disciplina_id):
        raise SemAcesso(material_id)
    if not aula.pronto:
        raise NaoEncontrado(material_id)
    return aula


def publicadas_da_aula(material_id: int):
    """Só as publicadas: rascunhos e descartadas nunca chegam ao aluno (QUE-RF-04)."""
    return (
        Questao.objects.filter(material_id=material_id, status=StatusDaQuestao.PUBLICADA)
        .select_related("material", "trecho")
        .order_by("id")
    )


def retorno_da_questao(questao: Questao, alternativa: int) -> dict:
    """O que o aluno vê ao responder: acerto, gabarito, justificativa e trecho (QUE-RF-08)."""
    return {
        "questao": questao.id,
        "alternativa": alternativa,
        "acerto": alternativa == questao.correta,
        "correta": questao.correta,
        "justificativa": questao.justificativa,
        "topico": questao.topico,
        "trecho": {
            "id": questao.trecho_id,
            "rotulo": f"Aula {questao.material.aula_numero}, p. {questao.trecho.pagina}",
        },
    }


def registrar_resposta(questao: Questao, aluno, alternativa: int, contexto: str) -> None:
    """Guarda a resposta só com o pseudônimo por disciplina e o dia (QUE-RF-11)."""
    RespostaQuiz.objects.create(
        questao=questao,
        aluno_pseudonimo=pseudonimo_do_aluno(aluno.id, questao.material.disciplina_id),
        alternativa=alternativa,
        acerto=alternativa == questao.correta,
        contexto=contexto,
    )


def quiz_da_aula(pessoa, perfil: str | None, material_id: int) -> dict:
    """As questões publicadas da aula, sem o gabarito das que faltam, e onde o aluno parou."""
    aula = _aula_do_aluno(pessoa, perfil, material_id)
    pausado = tutor.tutor_pausado(aula.disciplina_id)
    questoes = [] if pausado else list(publicadas_da_aula(material_id))
    progresso = ProgressoQuiz.objects.filter(aluno=pessoa, material_id=material_id).first()
    ids = {q.id for q in questoes}
    respostas = [r for r in (progresso.respostas if progresso else []) if r["questao"] in ids]
    por_id = {q.id: q for q in questoes}
    retornos = [retorno_da_questao(por_id[r["questao"]], r["alternativa"]) for r in respostas]
    return {
        "material": aula.id,
        "disciplina": aula.disciplina_id,
        "aula_numero": aula.aula_numero,
        "aula_titulo": aula.aula_titulo,
        "pausado": pausado,
        "questoes": [
            {
                "id": q.id,
                "enunciado": q.enunciado,
                "alternativas": q.alternativas,
                "topico": q.topico,
            }
            for q in questoes
        ],
        "respostas": retornos,
        "concluido": bool(questoes) and len(retornos) == len(questoes),
    }


def responder_questao(pessoa, perfil: str | None, questao_id: int, alternativa: int) -> dict:
    """Corrige a resposta, registra com pseudônimo e avança o progresso do aluno no quiz.

    Responder de novo a mesma questão na mesma tentativa devolve o mesmo retorno, sem registrar
    outra resposta.
    """
    try:
        questao = Questao.objects.select_related("material", "trecho").get(
            pk=questao_id, status=StatusDaQuestao.PUBLICADA
        )
    except Questao.DoesNotExist:
        raise NaoEncontrado(questao_id) from None
    _aula_do_aluno(pessoa, perfil, questao.material_id)
    if tutor.tutor_pausado(questao.material.disciplina_id):
        raise QuizPausado(questao_id)
    if not 0 <= alternativa <= 3:
        raise QuestaoInvalida({"alternativa": "Escolha uma das 4 alternativas."})
    with transaction.atomic():
        progresso, _ = ProgressoQuiz.objects.select_for_update().get_or_create(
            aluno=pessoa, material_id=questao.material_id
        )
        anterior = next((r for r in progresso.respostas if r["questao"] == questao.id), None)
        if anterior:
            return retorno_da_questao(questao, anterior["alternativa"])
        registrar_resposta(questao, pessoa, alternativa, RespostaQuiz.Contexto.QUIZ)
        progresso.respostas = [
            *progresso.respostas,
            {
                "questao": questao.id,
                "alternativa": alternativa,
                "acerto": alternativa == questao.correta,
            },
        ]
        progresso.indice_atual = len(progresso.respostas)
        progresso.save()
    return retorno_da_questao(questao, alternativa)


def reiniciar_quiz(pessoa, perfil: str | None, material_id: int) -> None:
    """Começa o quiz de novo. As respostas já registradas para o radar ficam."""
    _aula_do_aluno(pessoa, perfil, material_id)
    ProgressoQuiz.objects.filter(aluno=pessoa, material_id=material_id).delete()


def quizzes_da_disciplina(pessoa, disciplina_id: int) -> list[dict]:
    """As aulas prontas com questões publicadas e o andamento do aluno em cada uma."""
    if tutor.tutor_pausado(disciplina_id):
        return []
    linhas = (
        Questao.objects.filter(
            material__disciplina_id=disciplina_id,
            material__status="pronto",
            status=StatusDaQuestao.PUBLICADA,
        )
        .values("material_id", "material__aula_numero", "material__aula_titulo")
        .annotate(total=models.Count("id"))
        .order_by("material__aula_numero", "material_id")
    )
    progressos = {
        p.material_id: p.respostas
        for p in ProgressoQuiz.objects.filter(aluno=pessoa, material__disciplina_id=disciplina_id)
    }
    publicadas = set(
        Questao.objects.filter(
            material__disciplina_id=disciplina_id, status=StatusDaQuestao.PUBLICADA
        ).values_list("id", flat=True)
    )
    resultado = []
    for linha in linhas:
        respostas = [
            r for r in progressos.get(linha["material_id"], []) if r["questao"] in publicadas
        ]
        resultado.append(
            {
                "material": linha["material_id"],
                "aula_numero": linha["material__aula_numero"],
                "aula_titulo": linha["material__aula_titulo"],
                "questoes": linha["total"],
                "respondidas": len(respostas),
                "acertos": sum(1 for r in respostas if r["acerto"]),
            }
        )
    return resultado
