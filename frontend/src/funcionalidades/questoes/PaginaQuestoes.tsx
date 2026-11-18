import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router';

import {
  ErroDaApi,
  listarMateriaisDoProfessor,
  listarQuestoes,
  mudarQuestao,
  obterGeracao,
  pedirGeracao,
  type Geracao,
  type MudancaDeQuestao,
  type QuestaoDoProfessor,
  type StatusDaQuestao,
} from '../../api/cliente';
import { Abas } from '../../componentes/Abas';
import { Botao } from '../../componentes/Botao';
import { useAvisos } from '../../componentes/contextoDosAvisos';
import { EstadoVazio } from '../../componentes/EstadoVazio';
import { Icone } from '../../componentes/Icone';
import { Selo } from '../../componentes/Selo';
import { useDisciplina } from '../disciplinas/consultas';
import { LETRAS } from './textos';

const QUANTIDADES = [5, 10, 15, 20] as const;
const ESPERA_ENTRE_CONSULTAS_MS = 2000;

const VAZIO: Record<StatusDaQuestao, string> = {
  pendente: 'Nenhum rascunho pendente. Gere questões a partir de uma aula.',
  publicada: 'Nenhuma questão publicada ainda.',
  descartada: 'Nenhuma questão descartada.',
};

const MENSAGEM_DA_MUDANCA: Record<StatusDaQuestao, string> = {
  publicada: 'Questão publicada no quiz da turma.',
  descartada: 'Questão descartada.',
  pendente: 'Questão voltou para pendentes.',
};

function esperar(ms: number) {
  return new Promise((resolver) => setTimeout(resolver, ms));
}

/** Pede os rascunhos e acompanha o pedido até a geração terminar (QUE-RF-01). */
async function gerarRascunhos(materialId: number, quantidade: number): Promise<Geracao> {
  let pedido = await pedirGeracao(materialId, quantidade);
  while (pedido.status === 'processando') {
    await esperar(ESPERA_ENTRE_CONSULTAS_MS);
    pedido = await obterGeracao(pedido.id);
  }
  return pedido;
}

function motivoDoErro(erro: unknown): string {
  if (erro instanceof ErroDaApi && erro.corpo && typeof erro.corpo === 'object') {
    const corpo = erro.corpo as Record<string, unknown>;
    if (typeof corpo.detail === 'string') return corpo.detail;
    const mensagens = Object.values(corpo)
      .flat()
      .filter((m) => typeof m === 'string');
    if (mensagens.length) return mensagens.join(' ');
  }
  return 'Não foi possível salvar. Tente de novo.';
}

function Gerador({ disciplinaId }: { disciplinaId: number }) {
  const clienteDeDados = useQueryClient();
  const avisar = useAvisos();
  const materiais = useQuery({
    queryKey: ['materiais-do-professor', disciplinaId],
    queryFn: () => listarMateriaisDoProfessor(disciplinaId),
  });
  const prontos = (materiais.data ?? []).filter((m) => m.status === 'pronto');
  const [escolhida, setEscolhida] = useState<number | null>(null);
  const [quantidade, setQuantidade] = useState<number>(5);
  const aula = escolhida ?? prontos[0]?.id ?? null;
  const gerar = useMutation({
    mutationFn: () => gerarRascunhos(aula!, quantidade),
    onSuccess: (pedido) => {
      void clienteDeDados.invalidateQueries({ queryKey: ['questoes', disciplinaId] });
      if (pedido.status === 'pronto') {
        const texto = pedido.geradas === 1 ? 'rascunho gerado' : 'rascunhos gerados';
        avisar(`${pedido.geradas} ${texto}. Revise antes de publicar.`, 'sparkles');
      }
    },
  });
  const falhou = gerar.isError || gerar.data?.status === 'erro';

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    if (aula !== null) gerar.mutate();
  }

  if (materiais.data && prontos.length === 0) {
    return (
      <p className="notice">
        <Icone nome="info-circle" />
        Publique o PDF de uma aula em Materiais para gerar questões a partir dele.
      </p>
    );
  }

  return (
    <div className="stack">
      <form className="panel generator" onSubmit={aoEnviar} aria-label="Gerar rascunhos">
        <div className="fr-field generator-aula">
          <label className="fr-label" htmlFor="gerar-aula">
            Aula
          </label>
          <span className="fr-select-wrap">
            <select
              id="gerar-aula"
              className="fr-select"
              value={aula ?? ''}
              onChange={(evento) => setEscolhida(Number(evento.target.value))}
            >
              {prontos.map((m) => (
                <option key={m.id} value={m.id}>
                  Aula {m.aula_numero} · {m.aula_titulo}
                </option>
              ))}
            </select>
          </span>
        </div>
        <div className="fr-field generator-qtd">
          <label className="fr-label" htmlFor="gerar-quantidade">
            Quantidade
          </label>
          <span className="fr-select-wrap">
            <select
              id="gerar-quantidade"
              className="fr-select"
              value={quantidade}
              onChange={(evento) => setQuantidade(Number(evento.target.value))}
            >
              {QUANTIDADES.map((q) => (
                <option key={q} value={q}>
                  {q}
                </option>
              ))}
            </select>
          </span>
        </div>
        <Botao
          type="submit"
          icone={gerar.isPending ? 'loader-2' : 'sparkles'}
          disabled={gerar.isPending || aula === null}
        >
          {gerar.isPending ? 'Gerando…' : 'Gerar rascunhos'}
        </Botao>
      </form>
      <p role="status" className="small muted">
        {gerar.isPending
          ? `Gerando ${quantidade} rascunhos. Isso pode levar alguns minutos; você pode continuar revisando.`
          : ''}
      </p>
      {falhou && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          {gerar.isError
            ? motivoDoErro(gerar.error)
            : 'Não foi possível gerar agora. Tente de novo.'}
        </p>
      )}
    </div>
  );
}

function Edicao({
  questao,
  aoSalvar,
  aoCancelar,
  salvando,
}: {
  questao: QuestaoDoProfessor;
  aoSalvar: (dados: MudancaDeQuestao) => void;
  aoCancelar: () => void;
  salvando: boolean;
}) {
  const [enunciado, setEnunciado] = useState(questao.enunciado);
  const [alternativas, setAlternativas] = useState([...questao.alternativas]);
  const [correta, setCorreta] = useState(questao.correta);
  const [justificativa, setJustificativa] = useState(questao.justificativa);
  const [topico, setTopico] = useState(questao.topico);
  const base = `edicao-${questao.id}`;

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    aoSalvar({ enunciado, alternativas, correta, justificativa, topico });
  }

  return (
    <form className="stack" onSubmit={aoEnviar} aria-label="Editar a questão">
      <div className="fr-field">
        <label className="fr-label" htmlFor={`${base}-enunciado`}>
          Enunciado
        </label>
        <textarea
          id={`${base}-enunciado`}
          className="fr-input textarea"
          rows={3}
          value={enunciado}
          onChange={(e) => setEnunciado(e.target.value)}
        />
      </div>
      <fieldset className="stack">
        <legend className="fr-label">Alternativas (marque a correta)</legend>
        {alternativas.map((texto, i) => (
          <div key={i} className="row">
            <input
              type="radio"
              name={`${base}-correta`}
              id={`${base}-correta-${i}`}
              checked={correta === i}
              onChange={() => setCorreta(i)}
              aria-label={`Alternativa ${LETRAS[i]} é a correta`}
            />
            <label className="sr-only" htmlFor={`${base}-alternativa-${i}`}>
              Alternativa {LETRAS[i]}
            </label>
            <input
              id={`${base}-alternativa-${i}`}
              className="fr-input"
              value={texto}
              onChange={(e) =>
                setAlternativas(alternativas.map((a, j) => (j === i ? e.target.value : a)))
              }
            />
          </div>
        ))}
      </fieldset>
      <div className="fr-field">
        <label className="fr-label" htmlFor={`${base}-justificativa`}>
          Justificativa
        </label>
        <textarea
          id={`${base}-justificativa`}
          className="fr-input textarea"
          rows={2}
          value={justificativa}
          onChange={(e) => setJustificativa(e.target.value)}
        />
      </div>
      <div className="fr-field">
        <label className="fr-label" htmlFor={`${base}-topico`}>
          Tópico
        </label>
        <input
          id={`${base}-topico`}
          className="fr-input"
          value={topico}
          onChange={(e) => setTopico(e.target.value)}
        />
      </div>
      <div className="draft-actions">
        <Botao type="submit" pequeno disabled={salvando}>
          Salvar
        </Botao>
        <Botao type="button" variante="fantasma" pequeno onClick={aoCancelar}>
          Cancelar
        </Botao>
      </div>
    </form>
  );
}

function CartaoDaQuestao({
  questao,
  disciplinaId,
}: {
  questao: QuestaoDoProfessor;
  disciplinaId: number;
}) {
  const clienteDeDados = useQueryClient();
  const avisar = useAvisos();
  const [editando, setEditando] = useState(false);
  const mudar = useMutation({
    mutationFn: (dados: MudancaDeQuestao) => mudarQuestao(questao.id, dados),
    onSuccess: (_, dados) => {
      setEditando(false);
      void clienteDeDados.invalidateQueries({ queryKey: ['questoes', disciplinaId] });
      avisar(
        dados.status ? MENSAGEM_DA_MUDANCA[dados.status] : 'Questão atualizada.',
        'circle-check',
      );
    },
  });
  const rotuloDaCitacao = `Aula ${questao.aula_numero}, p. ${questao.trecho.pagina}`;
  const selo = {
    pendente: questao.nova ? (
      <Selo tom="destaque" pilula>
        Novo rascunho
      </Selo>
    ) : (
      <Selo pilula>Pendente</Selo>
    ),
    publicada: (
      <Selo tom="sucesso" icone="circle-check">
        Publicada para a turma
      </Selo>
    ),
    descartada: <Selo>Descartada</Selo>,
  }[questao.status];

  return (
    <article
      className={questao.status === 'descartada' ? 'panel draft is-muted' : 'panel draft'}
      aria-label={questao.enunciado}
    >
      <div className="draft-head">
        <span className="small muted">
          Aula {questao.aula_numero} · {questao.aula_titulo} · {questao.topico}
          {questao.editada ? ' · editada' : ''}
        </span>
        <div className="row">
          {selo}
          <Link to={`/trechos/${questao.trecho.id}`} className="fr-cite">
            {rotuloDaCitacao}
          </Link>
        </div>
      </div>
      {questao.origem_retirada && (
        <p className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Origem retirada: o material desta questão foi retirado.
        </p>
      )}
      {editando ? (
        <Edicao
          questao={questao}
          salvando={mudar.isPending}
          aoSalvar={(dados) => mudar.mutate(dados)}
          aoCancelar={() => setEditando(false)}
        />
      ) : (
        <>
          <h2 className="fr-card-title">{questao.enunciado}</h2>
          <ol className="draft-options" aria-label="Alternativas">
            {questao.alternativas.map((texto, i) => (
              <li
                key={i}
                className={i === questao.correta ? 'draft-option is-correct' : 'draft-option'}
              >
                <span className="fr-option-key">{LETRAS[i]}</span>
                <span>{texto}</span>
                {i === questao.correta && (
                  <Selo tom="sucesso" icone="check">
                    Correta
                  </Selo>
                )}
              </li>
            ))}
          </ol>
          <p className="small">
            <span className="strong">Justificativa:</span> {questao.justificativa}
          </p>
          <div className="draft-actions">
            {questao.status === 'pendente' ? (
              <>
                <Botao
                  pequeno
                  icone="check"
                  disabled={mudar.isPending || questao.origem_retirada}
                  onClick={() => mudar.mutate({ status: 'publicada' })}
                  aria-label={`Aprovar: ${questao.enunciado}`}
                >
                  Aprovar
                </Botao>
                <Botao
                  variante="contorno"
                  pequeno
                  icone="pencil"
                  onClick={() => setEditando(true)}
                  aria-label={`Editar: ${questao.enunciado}`}
                >
                  Editar
                </Botao>
                <Botao
                  variante="fantasma"
                  pequeno
                  icone="trash"
                  disabled={mudar.isPending}
                  onClick={() => mudar.mutate({ status: 'descartada' })}
                  aria-label={`Descartar: ${questao.enunciado}`}
                >
                  Descartar
                </Botao>
              </>
            ) : (
              <Botao
                variante="fantasma"
                pequeno
                icone="arrow-left"
                disabled={mudar.isPending}
                onClick={() => mudar.mutate({ status: 'pendente' })}
                aria-label={`Voltar para pendentes: ${questao.enunciado}`}
              >
                Voltar para pendentes
              </Botao>
            )}
          </div>
        </>
      )}
      {mudar.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          {motivoDoErro(mudar.error)}
        </p>
      )}
    </article>
  );
}

/**
 * Questões da disciplina para o professor, como no protótipo: o gerador de rascunhos e a
 * revisão por abas. Nada chega aos alunos sem aprovação (QUE-RF-01, QUE-RF-05, QUE-RF-06).
 */
export function PaginaQuestoes() {
  const disciplinaId = Number(useParams().id);
  const disciplina = useDisciplina(disciplinaId).data;
  const [aba, setAba] = useState<StatusDaQuestao>('pendente');
  const questoes = useQuery({
    queryKey: ['questoes', disciplinaId, aba],
    queryFn: () => listarQuestoes(disciplinaId, aba),
  });
  const contagens = questoes.data?.contagens;
  const abas = [
    { id: 'pendente', rotulo: `Pendentes (${contagens?.pendente ?? 0})` },
    { id: 'publicada', rotulo: `Publicadas (${contagens?.publicada ?? 0})` },
    { id: 'descartada', rotulo: `Descartadas (${contagens?.descartada ?? 0})` },
  ] as const;

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Questões</h1>
          <p className="page-sub">
            {disciplina ? `${disciplina.nome} · ${disciplina.turma} · ` : ''}A IA gera rascunhos a
            partir dos seus materiais. Nada chega aos alunos sem a sua aprovação.
          </p>
        </div>
      </div>
      <Gerador disciplinaId={disciplinaId} />
      <Abas rotulo="Filtrar questões" abas={abas} ativa={aba} aoMudar={setAba}>
        {questoes.isPending && (
          <p role="status" className="muted">
            Carregando as questões…
          </p>
        )}
        {questoes.isError && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível carregar as questões. Tente de novo em instantes.
          </p>
        )}
        {questoes.data &&
          (questoes.data.questoes.length === 0 ? (
            <EstadoVazio icone="list-check" titulo="Nada por aqui" texto={VAZIO[aba]} />
          ) : (
            <div className="stack">
              {questoes.data.questoes.map((q) => (
                <CartaoDaQuestao key={q.id} questao={q} disciplinaId={disciplinaId} />
              ))}
            </div>
          ))}
      </Abas>
    </div>
  );
}
