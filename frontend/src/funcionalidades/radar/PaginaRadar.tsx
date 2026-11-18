import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Link, useParams } from 'react-router';

import { listarSemanasDoRadar, obterRadar, ocultarExemploDoRadar } from '../../api/cliente';
import { classesDoBotao } from '../../componentes/classes';
import { Icone } from '../../componentes/Icone';
import { useDisciplina } from '../disciplinas/consultas';

function classeDaTaxa(taxa: number): string {
  if (taxa < 50) return 'fr-rate--low';
  if (taxa <= 70) return 'fr-rate--mid';
  return 'fr-rate--high';
}

function juntar(itens: string[]): string {
  if (itens.length <= 1) return itens.join('');
  return `${itens.slice(0, -1).join(', ')} e ${itens.at(-1)}`;
}

/**
 * O radar da turma, como no protótipo: os indicadores, a sugestão para a próxima aula, os
 * tópicos com mais dúvidas e o acerto nos quizzes. Nada aqui identifica alunos (RAD-RF-02 a 11).
 */
export function PaginaRadar() {
  const disciplinaId = Number(useParams().id);
  const disciplina = useDisciplina(disciplinaId).data;
  const clienteDeDados = useQueryClient();
  const [semana, setSemana] = useState<string | undefined>(undefined);
  const [aberto, setAberto] = useState<string | null>(null);
  const semanas = useQuery({
    queryKey: ['radar-semanas', disciplinaId],
    queryFn: () => listarSemanasDoRadar(disciplinaId),
  });
  const radar = useQuery({
    queryKey: ['radar', disciplinaId, semana ?? 'atual'],
    queryFn: () => obterRadar(disciplinaId, semana),
  });
  const ocultar = useMutation({
    mutationFn: (texto: string) => ocultarExemploDoRadar(disciplinaId, texto),
    onSuccess: () => clienteDeDados.invalidateQueries({ queryKey: ['radar', disciplinaId] }),
  });
  const dados = radar.data;
  const indicadores = dados?.indicadores;
  const maximo = Math.max(1, ...(dados?.topicos.map((t) => t.alunos) ?? []));
  const sugerida = dados?.sugestao[0];

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Radar da turma</h1>
          <p className="page-sub">
            {disciplina ? `${disciplina.nome} · ${disciplina.turma} · ` : ''}
            {dados?.rotulo ?? ''}
          </p>
        </div>
        <div className="fr-field radar-week">
          <label className="fr-label" htmlFor="radar-semana">
            Período
          </label>
          <span className="fr-select-wrap">
            <select
              id="radar-semana"
              className="fr-select"
              value={semana ?? semanas.data?.[0]?.semana ?? ''}
              onChange={(e) => setSemana(e.target.value)}
            >
              {(semanas.data ?? []).map((s) => (
                <option key={s.semana} value={s.semana}>
                  {s.rotulo}
                  {s.atual ? ' (atual)' : ''}
                </option>
              ))}
            </select>
          </span>
        </div>
      </div>

      {radar.isPending && (
        <p role="status" className="muted">
          Calculando o radar…
        </p>
      )}
      {radar.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível carregar o radar. Tente de novo em instantes.
        </p>
      )}

      {dados && indicadores && (
        <>
          <div className="metrics">
            <div className="fr-metric">
              <div className="fr-metric-label">Alunos ativos</div>
              <div className="fr-metric-value">
                {indicadores.alunos_ativos} <small>de {indicadores.matriculados}</small>
              </div>
            </div>
            <div className="fr-metric">
              <div className="fr-metric-label">Perguntas ao tutor</div>
              <div className="fr-metric-value">{indicadores.perguntas}</div>
            </div>
            <div className="fr-metric">
              <div className="fr-metric-label">Acerto nos quizzes</div>
              <div className="fr-metric-value">
                {indicadores.acerto_medio === null || indicadores.acerto_medio === undefined
                  ? '—'
                  : `${indicadores.acerto_medio}%`}
              </div>
            </div>
            <div className="fr-metric">
              <div className="fr-metric-label">Dúvidas sem resposta</div>
              <div className="fr-metric-value">{indicadores.duvidas_sem_resposta}</div>
            </div>
          </div>

          {dados.pouco_uso ? (
            <p className="notice">
              <Icone nome="info-circle" />
              Menos de 5 alunos usaram o Farol nesta semana. Para não identificar ninguém, o radar
              mostra só os indicadores.
            </p>
          ) : (
            <>
              {dados.sugestao.length > 0 && (
                <section className="panel suggestion" aria-labelledby="titulo-sugestao">
                  <div className="suggestion-text">
                    <h2 id="titulo-sugestao" className="card-heading">
                      <Icone nome="target" />
                      Sugestão para a próxima aula
                    </h2>
                    <p>
                      Comece retomando <strong>{juntar(dados.sugestao.map((s) => s.nome))}</strong>:
                      são as aulas com mais dúvidas e menor acerto nesta semana.
                    </p>
                  </div>
                  <div className="row">
                    {sugerida && (
                      <Link
                        className={classesDoBotao('primario', true)}
                        to={`/disciplinas/${disciplinaId}/questoes?aula=${sugerida.material}&quantidade=5`}
                      >
                        <Icone nome="sparkles" />
                        Gerar 5 questões de revisão
                      </Link>
                    )}
                    <Link
                      className={classesDoBotao('fantasma', true)}
                      to={`/disciplinas/${disciplinaId}/duvidas`}
                    >
                      Ver dúvidas sem resposta
                    </Link>
                  </div>
                </section>
              )}
              <div className="cols-2">
                <section className="panel" aria-labelledby="titulo-topicos">
                  <div className="panel-head">
                    <h2 id="titulo-topicos" className="card-heading">
                      Tópicos com mais dúvidas
                    </h2>
                    <span className="small muted">Toque para ver exemplos</span>
                  </div>
                  {dados.topicos.length === 0 ? (
                    <p className="small muted">Nenhum tópico com 5 alunos ou mais nesta semana.</p>
                  ) : (
                    <div className="topic-list">
                      {dados.topicos.map((t) => {
                        const estaAberto = aberto === t.nome;
                        return (
                          <div key={t.nome} className="topic-item">
                            <button
                              type="button"
                              className="topic-toggle"
                              aria-expanded={estaAberto}
                              onClick={() => setAberto(estaAberto ? null : t.nome)}
                            >
                              <span className="fr-topic">
                                <span>{t.nome}</span>
                                <span className="fr-topic-bar">
                                  <span
                                    style={{ width: `${Math.round((t.alunos / maximo) * 100)}%` }}
                                  />
                                </span>
                                <span className="fr-topic-count">{t.alunos} alunos</span>
                              </span>
                              <Icone nome={estaAberto ? 'chevron-down' : 'chevron-right'} />
                            </button>
                            {estaAberto && (
                              <div className="topic-examples">
                                <ul>
                                  {t.exemplos.map((exemplo) => (
                                    <li key={exemplo}>
                                      <span className="texto-entre-aspas">{exemplo}</span>{' '}
                                      <button
                                        type="button"
                                        className="link-inline"
                                        disabled={ocultar.isPending}
                                        onClick={() => ocultar.mutate(exemplo)}
                                        aria-label={`Ocultar o exemplo: ${exemplo}`}
                                      >
                                        Ocultar
                                      </button>
                                    </li>
                                  ))}
                                </ul>
                                <Link
                                  className="link-btn"
                                  to={`/disciplinas/${disciplinaId}/materiais`}
                                >
                                  <Icone nome="file-text" />
                                  Ver o material da aula
                                </Link>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </section>
                <section className="panel" aria-labelledby="titulo-acertos">
                  <div className="panel-head">
                    <h2 id="titulo-acertos" className="card-heading">
                      Acerto nos quizzes por tópico
                    </h2>
                  </div>
                  {dados.acertos.length === 0 ? (
                    <p className="small muted">
                      Ainda não há tópicos respondidos por 5 alunos ou mais nesta semana.
                    </p>
                  ) : (
                    <>
                      <div className="fr-topics">
                        {dados.acertos.map((a) => (
                          <div key={a.topico} className="fr-topic">
                            <span>{a.topico}</span>
                            <span className="fr-topic-bar">
                              <span style={{ width: `${a.taxa}%` }} />
                            </span>
                            <span className={`fr-topic-count ${classeDaTaxa(a.taxa)}`}>
                              {a.taxa}%
                            </span>
                          </div>
                        ))}
                      </div>
                      <p className="small muted legend">
                        <span className="fr-rate--low">abaixo de 50%</span> ·{' '}
                        <span className="fr-rate--mid">50% a 70%</span> ·{' '}
                        <span className="fr-rate--high">acima de 70%</span>
                      </p>
                    </>
                  )}
                </section>
              </div>
            </>
          )}
          <p className="privacy-note">
            <Icone nome="shield-lock" />O radar não mostra nomes. Tópicos e taxas com menos de 5
            alunos não aparecem, e o texto das perguntas passa por remoção de dados pessoais.
          </p>
        </>
      )}
    </div>
  );
}
