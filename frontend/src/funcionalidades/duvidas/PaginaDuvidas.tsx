import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useParams } from 'react-router';

import {
  listarDuvidasDaDisciplina,
  mudarStatusDaDuvida,
  type DuvidaDoProfessor,
} from '../../api/cliente';
import { Abas } from '../../componentes/Abas';
import { Botao } from '../../componentes/Botao';
import { useDisciplinas } from '../disciplinas/consultas';

type Aba = 'aberta' | 'respondida';
type DuvidaNaTela = DuvidaDoProfessor & { quando: string };

const ABAS = [
  { id: 'aberta', rotulo: 'Abertas' },
  { id: 'respondida', rotulo: 'Respondidas em aula' },
] as const satisfies readonly { id: Aba; rotulo: string }[];

const UM_DIA_EM_MS = 24 * 60 * 60 * 1000;

/** "hoje", "ontem" ou "há N dias": só o dia, nunca a hora do envio (DUV-RF-03). */
function haQuantoTempo(data: string, hoje: Date): string {
  const enviada = new Date(`${data}T00:00:00`); // meia-noite no fuso do navegador
  const inicioDeHoje = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate());
  const dias = Math.round((inicioDeHoje.getTime() - enviada.getTime()) / UM_DIA_EM_MS);
  if (dias <= 0) return 'Enviada hoje';
  if (dias === 1) return 'Enviada ontem';
  return `Enviada há ${dias} dias`;
}

/** As dúvidas e, já calculado na chegada, há quanto tempo cada uma foi enviada. */
async function carregar(disciplinaId: number, aba: Aba): Promise<DuvidaNaTela[]> {
  const duvidas = await listarDuvidasDaDisciplina(disciplinaId, aba);
  const hoje = new Date();
  return duvidas.map((duvida) => ({ ...duvida, quando: haQuantoTempo(duvida.data, hoje) }));
}

/** As dúvidas que o material não respondeu, sem dados dos alunos (DUV-RF-05 e DUV-RF-07). */
export function PaginaDuvidas() {
  const disciplinaId = Number(useParams().id);
  const disciplina = useDisciplinas('').data?.find((d) => d.id === disciplinaId);
  const [aba, setAba] = useState<Aba>('aberta');
  const clienteDeDados = useQueryClient();
  const duvidas = useQuery({
    queryKey: ['duvidas', disciplinaId, aba],
    queryFn: () => carregar(disciplinaId, aba),
  });
  const mudar = useMutation({
    mutationFn: ({ id, status }: { id: number; status: 'respondida' | 'oculta' }) =>
      mudarStatusDaDuvida(disciplinaId, id, status),
    onSuccess: () => clienteDeDados.invalidateQueries({ queryKey: ['duvidas', disciplinaId] }),
  });

  return (
    <div className="page">
      <div>
        <h1 className="text-2xl font-extrabold">Dúvidas que o material não respondeu</h1>
        {disciplina && <p className="text-ink-muted">{disciplina.nome}</p>}
        <p className="text-sm text-ink-muted">
          As dúvidas chegam sem o nome dos alunos. Trate delas em aula e marque como respondidas.
        </p>
      </div>
      <Abas rotulo="Situação das dúvidas" abas={ABAS} ativa={aba} aoMudar={setAba}>
        {duvidas.isPending && (
          <p role="status" className="mt-4 text-ink-muted">
            Carregando as dúvidas…
          </p>
        )}
        {(duvidas.isError || mudar.isError) && (
          <p role="alert" className="mt-4 text-danger-text">
            Não foi possível atualizar as dúvidas. Tente de novo em instantes.
          </p>
        )}
        {duvidas.data &&
          (duvidas.data.length === 0 ? (
            <p className="mt-4 text-ink-muted">
              {aba === 'aberta' ? 'Nenhuma dúvida aberta.' : 'Nenhuma dúvida respondida ainda.'}
            </p>
          ) : (
            <ul aria-label="Dúvidas" className="mt-4 flex flex-col gap-2">
              {duvidas.data.map((duvida) => (
                <li key={duvida.id} className="rounded-lg border border-line bg-surface p-4">
                  <div className="flex flex-wrap items-center gap-2 text-sm text-ink-muted">
                    {duvida.nova && (
                      <span className="rounded-full bg-brand-yellow px-2 font-bold text-on-yellow">
                        Nova
                      </span>
                    )}
                    <span>{duvida.quando}</span>
                  </div>
                  <p className="mt-1 whitespace-pre-wrap">{duvida.texto}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {aba === 'aberta' && (
                      <Botao
                        disabled={mudar.isPending}
                        onClick={() => mudar.mutate({ id: duvida.id, status: 'respondida' })}
                      >
                        Respondida em aula
                      </Botao>
                    )}
                    <Botao
                      variante="secundario"
                      aria-label={`Ocultar a dúvida: ${duvida.texto}`}
                      disabled={mudar.isPending}
                      onClick={() => mudar.mutate({ id: duvida.id, status: 'oculta' })}
                    >
                      Ocultar
                    </Botao>
                  </div>
                </li>
              ))}
            </ul>
          ))}
      </Abas>
    </div>
  );
}
