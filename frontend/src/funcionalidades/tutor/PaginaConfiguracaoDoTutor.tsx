import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { useParams } from 'react-router';

import {
  obterConfiguracaoDoTutor,
  salvarConfiguracaoDoTutor,
  type ConfiguracaoDoTutor,
} from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { Icone } from '../../componentes/Icone';
import { useDisciplina } from '../disciplinas/consultas';
import { JanelasDeProva } from './JanelasDeProva';

const LIMITES = [20, 40, 60] as const;

function Formulario({
  disciplinaId,
  inicial,
}: {
  disciplinaId: number;
  inicial: ConfiguracaoDoTutor;
}) {
  const clienteDeDados = useQueryClient();
  const [modoPistas, setModoPistas] = useState(inicial.modo_pistas ?? true);
  const [limite, setLimite] = useState(inicial.limite_diario ?? 40);
  const [politica, setPolitica] = useState(inicial.politica ?? '');
  const [resumoSemanal, setResumoSemanal] = useState(inicial.resumo_semanal ?? true);
  const salvar = useMutation({
    mutationFn: () =>
      salvarConfiguracaoDoTutor(disciplinaId, {
        modo_pistas: modoPistas,
        limite_diario: limite,
        politica,
        resumo_semanal: resumoSemanal,
      }),
    onSuccess: (salva) => clienteDeDados.setQueryData(['tutor-configuracao', disciplinaId], salva),
  });

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    salvar.mutate();
  }

  return (
    <form onSubmit={aoEnviar} className="stack">
      <section className="panel" aria-labelledby="titulo-tutor">
        <h2 id="titulo-tutor" className="card-heading">
          <Icone nome="message-circle" />
          Tutor
        </h2>
        <div className="switch-row">
          <div className="switch-text">
            <label htmlFor="modo-pistas" className="strong">
              Modo pistas
            </label>
            <p id="modo-pistas-ajuda" className="small muted">
              Em perguntas de exercício, o tutor guia em etapas e não entrega a resposta final.
            </p>
          </div>
          <input
            id="modo-pistas"
            type="checkbox"
            className="switch"
            checked={modoPistas}
            onChange={(evento) => setModoPistas(evento.target.checked)}
            aria-describedby="modo-pistas-ajuda"
          />
        </div>
        <div className="switch-row">
          <div className="switch-text">
            <label htmlFor="limite" className="strong">
              Limite de perguntas por dia
            </label>
            <p id="limite-ajuda" className="small muted">
              Por aluno. Controla o custo e evita abuso; o contador zera à meia-noite.
            </p>
          </div>
          <span className="fr-select-wrap select-inline">
            <select
              id="limite"
              className="fr-select"
              value={limite}
              aria-describedby="limite-ajuda"
              onChange={(evento) =>
                setLimite(Number(evento.target.value) as (typeof LIMITES)[number])
              }
            >
              {LIMITES.map((valor) => (
                <option key={valor} value={valor}>
                  {valor} perguntas
                </option>
              ))}
            </select>
          </span>
        </div>
      </section>

      <section className="panel" aria-labelledby="titulo-radar">
        <h2 id="titulo-radar" className="card-heading">
          <Icone nome="radar" />
          Radar
        </h2>
        <div className="switch-row">
          <div className="switch-text">
            <label htmlFor="resumo-semanal" className="strong">
              Resumo semanal por e-mail
            </label>
            <p id="resumo-semanal-ajuda" className="small muted">
              Toda segunda, às 6h30, com os tópicos de mais dúvida e as dúvidas sem resposta.
            </p>
          </div>
          <input
            id="resumo-semanal"
            type="checkbox"
            className="switch"
            checked={resumoSemanal}
            onChange={(evento) => setResumoSemanal(evento.target.checked)}
            aria-describedby="resumo-semanal-ajuda"
          />
        </div>
      </section>

      <section className="panel" aria-labelledby="titulo-politica">
        <h2 id="titulo-politica" className="card-heading">
          <Icone nome="shield-lock" />
          Política de uso de IA
        </h2>
        <p id="politica-ajuda" className="small muted">
          Os alunos veem este texto no tutor, no link "Política de uso de IA", junto com o resumo
          das regras.
        </p>
        <label htmlFor="politica" className="sr-only">
          Política de uso de IA
        </label>
        <textarea
          id="politica"
          className="fr-input textarea"
          rows={5}
          value={politica}
          onChange={(evento) => setPolitica(evento.target.value)}
          aria-describedby="politica-ajuda"
        />
      </section>

      <div className="row row--end">
        <p role="status" className="bubble-note">
          {salvar.isSuccess ? 'Configuração salva.' : ''}
        </p>
        <Botao type="submit" disabled={salvar.isPending}>
          Salvar configuração
        </Botao>
      </div>
      {salvar.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível salvar a configuração. Tente de novo.
        </p>
      )}
    </form>
  );
}

/**
 * A configuração da disciplina para o professor, como a tela "Disciplina" do protótipo: o tutor
 * (modo pistas e limite), a política de uso de IA e as provas (TUT-RF-06 a 08 e 10).
 */
export function PaginaConfiguracaoDoTutor() {
  const disciplinaId = Number(useParams().id);
  const disciplina = useDisciplina(disciplinaId).data;
  const configuracao = useQuery({
    queryKey: ['tutor-configuracao', disciplinaId],
    queryFn: () => obterConfiguracaoDoTutor(disciplinaId),
  });

  return (
    <div className="page page--narrow">
      <div className="page-head">
        <div>
          <h1 className="page-title">Disciplina</h1>
          <p className="page-sub">
            {disciplina ? `${disciplina.nome} · ${disciplina.turma}` : 'Configuração do tutor'}
          </p>
        </div>
      </div>
      {configuracao.isPending && (
        <p role="status" className="muted">
          Carregando a configuração…
        </p>
      )}
      {configuracao.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível carregar a configuração do tutor. Tente de novo em instantes.
        </p>
      )}
      {configuracao.data && <Formulario disciplinaId={disciplinaId} inicial={configuracao.data} />}
      <JanelasDeProva disciplinaId={disciplinaId} />
    </div>
  );
}
