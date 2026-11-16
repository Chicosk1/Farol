"""Importação de turmas e matrículas por CSV (ACE-T40, ACE-T41).

Cenários de aceite da História 3 da spec 001: relatório de linhas aceitas e rejeitadas, importar
de novo sem duplicar e perder o acesso quando o aluno sai do arquivo. Todos os dados são
fictícios (domínio exemplo.edu.br).
"""

import time

import pytest

from contas.models import Perfil, Pessoa
from disciplinas import servicos
from disciplinas.models import Disciplina, Importacao, Matricula

CABECALHO = "ra,nome,email,codigo_disciplina,nome_disciplina,turma,semestre,email_professor"
ED = "SINF201,Estruturas de Dados,SINF2NA,2026/2,carlos.mendes@exemplo.edu.br"
BD = "SINF202,Banco de Dados I,SINF2NA,2026/2,marta.ribeiro@exemplo.edu.br"


@pytest.fixture(autouse=True)
def arquivos_temporarios(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


def linha(numero: int, disciplina: str = ED, nome: str | None = None) -> str:
    return f"{numero:06d},{nome or f'Aluno {numero}'},aluno{numero}@exemplo.edu.br,{disciplina}"


def csv(*linhas: str, cabecalho: str = CABECALHO) -> str:
    return "\n".join([cabecalho, *linhas]) + "\n"


def importar(admin, texto: str | bytes) -> Importacao:
    conteudo = texto if isinstance(texto, bytes) else texto.encode("utf-8")
    importacao = servicos.criar_importacao(conteudo, "turmas.csv", admin)
    return servicos.processar_importacao(importacao.id)


def ativas(disciplina_codigo: str) -> set[str]:
    return set(
        Matricula.objects.filter(
            disciplina__codigo=disciplina_codigo, situacao=Matricula.Situacao.ATIVA
        ).values_list("aluno__email", flat=True)
    )


@pytest.mark.requisito("ACE-RF-06")
def test_csv_com_60_alunos_e_2_disciplinas_cria_as_matriculas_certas(admin):
    linhas = [linha(n, ED) for n in range(1, 61)] + [linha(n, BD) for n in range(1, 61)]

    importacao = importar(admin, csv(*linhas))

    assert importacao.status == Importacao.Status.CONCLUIDA
    assert importacao.aceitas == 120
    assert importacao.rejeitadas == []
    assert Pessoa.objects.filter(perfis__contains=[Perfil.ALUNO]).count() == 60
    assert Disciplina.objects.count() == 2
    assert Matricula.objects.count() == 120
    estruturas = Disciplina.objects.get(codigo="SINF201")
    assert estruturas.professor.email == "carlos.mendes@exemplo.edu.br"
    assert estruturas.professor.perfis == [Perfil.PROFESSOR]
    assert (estruturas.turma, estruturas.semestre) == ("SINF2NA", "2026/2")


@pytest.mark.requisito("ACE-RF-06")
def test_relatorio_lista_as_linhas_rejeitadas_com_o_motivo(admin):
    texto = csv(
        linha(1),
        f"000002,Aluno 2,email-sem-arroba,{ED}",  # linha 3 do arquivo
        f"000003,,aluno3@exemplo.edu.br,{ED}",  # linha 4: sem nome
        "000004,Aluno 4,aluno4@exemplo.edu.br,SINF201,Estruturas de Dados,SINF2NA,26-2,"
        "carlos.mendes@exemplo.edu.br",  # linha 5: semestre fora do formato AAAA/N
        linha(5),
    )

    importacao = importar(admin, texto)

    assert importacao.status == Importacao.Status.CONCLUIDA
    assert importacao.aceitas == 2
    assert [r["linha"] for r in importacao.rejeitadas] == [3, 4, 5]
    motivos = {r["linha"]: r["motivo"] for r in importacao.rejeitadas}
    assert "e-mail" in motivos[3]
    assert "nome" in motivos[4]
    assert ativas("SINF201") == {"aluno1@exemplo.edu.br", "aluno5@exemplo.edu.br"}


@pytest.mark.requisito("ACE-RF-06")
def test_linha_repetida_e_professor_diferente_na_mesma_disciplina_sao_rejeitados(admin):
    outro_professor = linha(
        3, "SINF201,Estruturas de Dados,SINF2NA,2026/2,joao.pereira@exemplo.edu.br"
    )
    texto = csv(linha(1), linha(1), linha(2), outro_professor)

    importacao = importar(admin, texto)

    assert importacao.aceitas == 2
    motivos = {r["linha"]: r["motivo"] for r in importacao.rejeitadas}
    assert "repetida" in motivos[3].lower()
    assert "professor" in motivos[5].lower()


@pytest.mark.requisito("ACE-RF-07")
def test_importar_o_mesmo_arquivo_duas_vezes_nao_duplica_nada(admin):
    texto = csv(*[linha(n, ED) for n in range(1, 11)], *[linha(n, BD) for n in range(1, 6)])
    importar(admin, texto)
    contagens = (Pessoa.objects.count(), Disciplina.objects.count(), Matricula.objects.count())

    segunda = importar(admin, texto)

    assert segunda.aceitas == 15
    assert (
        Pessoa.objects.count(),
        Disciplina.objects.count(),
        Matricula.objects.count(),
    ) == contagens


@pytest.mark.requisito("ACE-RF-07")
def test_aluno_que_saiu_da_turma_perde_o_acesso_e_volta_se_reaparecer(admin):
    importar(admin, csv(linha(1), linha(2), linha(3)))
    assert len(ativas("SINF201")) == 3

    atualizada = importar(admin, csv(linha(1), linha(3)))

    assert ativas("SINF201") == {"aluno1@exemplo.edu.br", "aluno3@exemplo.edu.br"}
    assert atualizada.matriculas_encerradas == 1
    encerrada = Matricula.objects.get(aluno__email="aluno2@exemplo.edu.br")
    assert encerrada.situacao == Matricula.Situacao.ENCERRADA  # o histórico continua no banco

    importar(admin, csv(linha(1), linha(2), linha(3)))
    assert len(ativas("SINF201")) == 3


@pytest.mark.requisito("ACE-RF-07")
def test_so_as_disciplinas_do_arquivo_perdem_matriculas(admin):
    importar(admin, csv(linha(1, ED), linha(1, BD)))

    importar(admin, csv(linha(2, ED)))  # o arquivo novo só traz Estruturas de Dados

    assert ativas("SINF201") == {"aluno2@exemplo.edu.br"}
    assert ativas("SINF202") == {"aluno1@exemplo.edu.br"}  # Banco de Dados I não foi tocada


@pytest.mark.requisito("ACE-RF-07")
def test_com_linhas_rejeitadas_nenhuma_matricula_e_encerrada_e_o_relatorio_avisa(admin):
    importar(admin, csv(linha(1), linha(2)))

    importacao = importar(admin, csv(linha(1), "000002,Aluno 2,quebrado,SINF201,x,y,z,w"))

    assert importacao.matriculas_encerradas == 0
    assert len(ativas("SINF201")) == 2
    assert "encerrad" in importacao.aviso.lower()


@pytest.mark.requisito("ACE-RF-06")
@pytest.mark.parametrize(
    ("conteudo", "trecho_do_erro"),
    [
        (
            "ra,nome,email,codigo_disciplina,nome_disciplina,turma,semestre\n1,A,a@x.edu.br,S,N,T,2026/2\n",
            "email_professor",
        ),
        (
            "ra;nome;email;codigo_disciplina;nome_disciplina;turma;semestre;email_professor\n",
            "vírgula",
        ),
        (
            f"{CABECALHO}\n".encode("latin-1")
            + "1,José,j@exemplo.edu.br,S,N,T,2026/2,p@exemplo.edu.br".encode("latin-1"),
            "UTF-8",
        ),
        ("", "vazio"),
        (f"{CABECALHO}\n", "linhas de dados"),
    ],
    ids=["coluna faltando", "ponto e vírgula", "codificação", "vazio", "só o cabeçalho"],
)
def test_arquivo_com_problema_de_estrutura_e_recusado_sem_importar_nada(
    admin, conteudo, trecho_do_erro
):
    importacao = importar(admin, conteudo)

    assert importacao.status == Importacao.Status.RECUSADA
    assert trecho_do_erro in importacao.erro
    assert importacao.aceitas == 0
    assert Pessoa.objects.filter(perfis__contains=[Perfil.ALUNO]).count() == 0
    assert Disciplina.objects.count() == 0
    assert Matricula.objects.count() == 0


@pytest.mark.requisito("ACE-RF-06")
def test_aceita_bom_de_utf8_e_acentos_e_ignora_linhas_em_branco(admin):
    texto = "﻿" + csv("", linha(1, nome="José Antônio"), "")

    importacao = importar(admin, texto)

    assert importacao.status == Importacao.Status.CONCLUIDA
    assert importacao.aceitas == 1
    assert Pessoa.objects.get(email="aluno1@exemplo.edu.br").nome == "José Antônio"


@pytest.mark.requisito("ACE-RF-06")
def test_colunas_em_outra_ordem_e_com_maiusculas_no_cabecalho_funcionam(admin):
    cabecalho = "Email,Nome,RA,Turma,Semestre,Codigo_Disciplina,Nome_Disciplina,Email_Professor"
    corpo = (
        "ana@exemplo.edu.br,Ana Souza,1,SINF2NA,2026/2,SINF201,Estruturas de Dados,"
        "carlos.mendes@exemplo.edu.br"
    )

    importacao = importar(admin, csv(corpo, cabecalho=cabecalho))

    assert importacao.aceitas == 1
    assert ativas("SINF201") == {"ana@exemplo.edu.br"}


@pytest.mark.requisito("ACE-RF-03")
def test_a_importacao_acrescenta_perfis_sem_apagar_os_que_a_pessoa_ja_tem(admin):
    mestre = Pessoa.objects.create_user(
        email="carlos.mendes@exemplo.edu.br", nome="Carlos Mendes", perfis=[Perfil.PROFESSOR]
    )
    # O professor também é aluno de uma pós-graduação: aparece como aluno no arquivo.
    texto = csv(f"1,Carlos Mendes,carlos.mendes@exemplo.edu.br,{BD}")

    importar(admin, texto)

    mestre.refresh_from_db()
    assert set(mestre.perfis) == {Perfil.PROFESSOR, Perfil.ALUNO}


@pytest.mark.requisito("ACE-RF-02")
def test_pessoas_criadas_pela_importacao_nao_tem_senha(admin):
    importar(admin, csv(linha(1)))

    assert not Pessoa.objects.get(email="aluno1@exemplo.edu.br").has_usable_password()
    assert not Pessoa.objects.get(email="carlos.mendes@exemplo.edu.br").has_usable_password()


def test_o_relatorio_fica_guardado_e_o_arquivo_tambem(admin):
    importacao = importar(admin, csv(linha(1), "x,y,z,w,v,u,t,s"))

    importacao.refresh_from_db()
    assert importacao.enviada_por == admin
    assert importacao.aceitas == 1
    assert len(importacao.rejeitadas) == 1
    assert importacao.arquivo.read().decode("utf-8").startswith(CABECALHO)


@pytest.mark.requisito("ACE-CS-02")
def test_uma_planilha_com_1000_matriculas_termina_em_menos_de_1_minuto(admin):
    linhas = [linha(n, ED) for n in range(1, 501)] + [linha(n, BD) for n in range(1, 501)]

    inicio = time.monotonic()
    importacao = importar(admin, csv(*linhas))
    duracao = time.monotonic() - inicio

    assert importacao.aceitas == 1000
    assert Matricula.objects.count() == 1000
    assert duracao < 60
