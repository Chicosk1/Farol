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
import { Icone } from '../../componentes/Icone';
import { Selo } from '../../componentes/Selo';
import { useDisciplina } from '../disciplinas/consultas';

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
  const disciplina = useDisciplina(disciplinaId).data;
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
      <div className="page-head">
        <div>
          <h1 className="page-title">Dúvidas que o material não respondeu</h1>
          <p className="page-sub">
            {disciplina ? `${disciplina.nome} · ${disciplina.turma} · ` : ''}Trate delas em aula e
            marque como respondidas.
          </p>
        </div>
        {aba === 'aberta' && duvidas.data && (
          <Selo pilula>
            {duvidas.data.length} {duvidas.data.length === 1 ? 'pendente' : 'pendentes'}
          </Selo>
        )}
      </div>
      <Abas rotulo="Situação das dúvidas" abas={ABAS} ativa={aba} aoMudar={setAba}>
        {duvidas.isPending && (
          <p role="status" className="muted">
            Carregando as dúvidas…
          </p>
        )}
        {(duvidas.isError || mudar.isError) && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível atualizar as dúvidas. Tente de novo em instantes.
          </p>
        )}
        {duvidas.data &&
          (duvidas.data.length === 0 ? (
            <ul className="panel list">
              <li className="list-row muted">
                {aba === 'aberta' ? 'Nenhuma dúvida aberta.' : 'Nenhuma dúvida respondida ainda.'}
              </li>
            </ul>
          ) : (
            <ul aria-label="Dúvidas" className="panel list">
              {duvidas.data.map((duvida) => (
                <li key={duvida.id} className={aba === 'aberta' ? 'list-row' : 'list-row is-done'}>
                  {aba === 'aberta' ? (
                    <span className="file-icon">
                      <Icone nome="message-question" />
                    </span>
                  ) : (
                    <Icone nome="circle-check" />
                  )}
                  <span className="list-row-main">
                    <span className="trecho-texto texto-entre-aspas">{duvida.texto}</span>
                    <span className="small muted">
                      {duvida.quando} · enviada pelo tutor
                      {duvida.nova && (
                        <>
                          {' · '}
                          <Selo tom="destaque" pilula>
                            Nova
                          </Selo>
                        </>
                      )}
                    </span>
                  </span>
                  <span className="row">
                    {aba === 'aberta' && (
                      <Botao
                        variante="contorno"
                        pequeno
                        icone="check"
                        disabled={mudar.isPending}
                        onClick={() => mudar.mutate({ id: duvida.id, status: 'respondida' })}
                      >
                        Respondida em aula
                      </Botao>
                    )}
                    <button
                      type="button"
                      className="fr-icon-btn fr-icon-btn--sm"
                      aria-label={`Ocultar a dúvida: ${duvida.texto}`}
                      title="Ocultar a dúvida (por exemplo, se for ofensiva)"
                      disabled={mudar.isPending}
                      onClick={() => mudar.mutate({ id: duvida.id, status: 'oculta' })}
                    >
                      <Icone nome="x" />
                    </button>
                  </span>
                </li>
              ))}
            </ul>
          ))}
      </Abas>
      <p className="privacy-note">
        <Icone nome="shield-lock" />
        As dúvidas chegam sem o nome dos alunos, sem o e-mail e sem o horário do envio.
      </p>
    </div>
  );
}
