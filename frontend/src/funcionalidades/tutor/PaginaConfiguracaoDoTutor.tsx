import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { useParams } from 'react-router';

import {
  obterConfiguracaoDoTutor,
  salvarConfiguracaoDoTutor,
  type ConfiguracaoDoTutor,
} from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { useDisciplinas } from '../disciplinas/consultas';

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
  const salvar = useMutation({
    mutationFn: () =>
      salvarConfiguracaoDoTutor(disciplinaId, {
        modo_pistas: modoPistas,
        limite_diario: limite,
        politica,
      }),
    onSuccess: (salva) => clienteDeDados.setQueryData(['tutor-configuracao', disciplinaId], salva),
  });

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    salvar.mutate();
  }

  return (
    <form
      onSubmit={aoEnviar}
      className="flex flex-col gap-4 rounded-lg border border-line bg-surface p-4"
    >
      <h2 className="text-lg font-bold">Configuração</h2>
      <div className="flex items-start gap-3">
        <input
          id="modo-pistas"
          type="checkbox"
          checked={modoPistas}
          onChange={(evento) => setModoPistas(evento.target.checked)}
          aria-describedby="modo-pistas-ajuda"
          className="mt-1 h-6 w-6"
        />
        <div>
          <label htmlFor="modo-pistas" className="font-bold">
            Modo pistas
          </label>
          <p id="modo-pistas-ajuda" className="text-sm text-ink-muted">
            Em exercícios, o tutor dá pistas em etapas em vez da resposta pronta.
          </p>
        </div>
      </div>

      <div>
        <label htmlFor="limite" className="block font-bold">
          Limite de perguntas por dia
        </label>
        <select
          id="limite"
          value={limite}
          onChange={(evento) => setLimite(Number(evento.target.value) as (typeof LIMITES)[number])}
          className="mt-1 min-h-12 rounded-lg border border-line-control bg-surface px-3 text-ink"
        >
          {LIMITES.map((valor) => (
            <option key={valor} value={valor}>
              {valor} perguntas por aluno
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="politica" className="block font-bold">
          Política de uso de IA
        </label>
        <textarea
          id="politica"
          value={politica}
          onChange={(evento) => setPolitica(evento.target.value)}
          rows={5}
          aria-describedby="politica-ajuda"
          className="mt-1 w-full rounded-lg border border-line-control bg-surface p-3 text-ink"
        />
        <p id="politica-ajuda" className="text-sm text-ink-muted">
          Os alunos veem este texto no tutor, junto com o resumo das regras.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Botao type="submit" disabled={salvar.isPending}>
          Salvar configuração
        </Botao>
        <p role="status" className="text-success-text">
          {salvar.isSuccess ? 'Configuração salva.' : ''}
        </p>
      </div>
      {salvar.isError && (
        <p role="alert" className="text-danger-text">
          Não foi possível salvar a configuração. Tente de novo.
        </p>
      )}
    </form>
  );
}

/** O tutor da disciplina para o professor: configuração e, depois, as janelas de prova. */
export function PaginaConfiguracaoDoTutor() {
  const disciplinaId = Number(useParams().id);
  const disciplina = useDisciplinas('').data?.find((d) => d.id === disciplinaId);
  const configuracao = useQuery({
    queryKey: ['tutor-configuracao', disciplinaId],
    queryFn: () => obterConfiguracaoDoTutor(disciplinaId),
  });

  return (
    <main id="conteudo" className="mx-auto flex max-w-3xl flex-col gap-4 p-4 text-ink">
      <h1 className="text-2xl font-extrabold">
        {disciplina ? `Tutor de ${disciplina.nome}` : 'Tutor da disciplina'}
      </h1>
      {configuracao.isPending && (
        <p role="status" className="text-ink-muted">
          Carregando a configuração…
        </p>
      )}
      {configuracao.isError && (
        <p role="alert" className="text-danger-text">
          Não foi possível carregar a configuração do tutor. Tente de novo em instantes.
        </p>
      )}
      {configuracao.data && <Formulario disciplinaId={disciplinaId} inicial={configuracao.data} />}
    </main>
  );
}
