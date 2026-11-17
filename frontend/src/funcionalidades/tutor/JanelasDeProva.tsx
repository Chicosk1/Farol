import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';

import {
  apagarJanelaDeProva,
  criarJanelaDeProva,
  ErroDaApi,
  listarJanelasDeProva,
  type JanelaDeProva,
} from '../../api/cliente';
import { Botao } from '../../componentes/Botao';

type JanelaNaTela = JanelaDeProva & { ativa: boolean };

const DATA_E_HORA = new Intl.DateTimeFormat('pt-BR', {
  weekday: 'short',
  day: '2-digit',
  month: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
});
const HORA = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' });

function descrever(janela: JanelaDeProva): string {
  const inicio = new Date(janela.inicio);
  if (!janela.fim) return `${DATA_E_HORA.format(inicio)}, sem horário de fim`;
  return `${DATA_E_HORA.format(inicio)} às ${HORA.format(new Date(janela.fim))}`;
}

/** As janelas e, já calculado na chegada, se cada uma está valendo agora. */
async function carregar(disciplinaId: number): Promise<JanelaNaTela[]> {
  const janelas = await listarJanelasDeProva(disciplinaId);
  const agora = Date.now();
  return janelas.map((janela) => ({
    ...janela,
    ativa: new Date(janela.inicio).getTime() <= agora,
  }));
}

function motivo(erro: unknown): string {
  const corpo = erro instanceof ErroDaApi ? (erro.corpo as Record<string, string[]>) : undefined;
  const primeiro = corpo && Object.values(corpo).find((valor) => Array.isArray(valor));
  return primeiro?.[0] ?? 'Não foi possível salvar a janela de prova. Tente de novo.';
}

/** Modo prova na hora e janelas agendadas, com o tutor pausado para os alunos (TUT-RF-07). */
export function JanelasDeProva({ disciplinaId }: { disciplinaId: number }) {
  const clienteDeDados = useQueryClient();
  const chave = ['janelas-prova', disciplinaId];
  const janelas = useQuery({ queryKey: chave, queryFn: () => carregar(disciplinaId) });
  const recarregar = () => clienteDeDados.invalidateQueries({ queryKey: chave });
  const criar = useMutation({
    mutationFn: (dados: { inicio?: string; fim?: string }) =>
      criarJanelaDeProva(disciplinaId, dados),
    onSuccess: recarregar,
  });
  const apagar = useMutation({
    mutationFn: (janelaId: number) => apagarJanelaDeProva(disciplinaId, janelaId),
    onSuccess: recarregar,
  });
  const [dia, setDia] = useState('');
  const [comeca, setComeca] = useState('');
  const [termina, setTermina] = useState('');

  const ativa = janelas.data?.find((janela) => janela.ativa);
  const agendadas = janelas.data?.filter((janela) => !janela.ativa) ?? [];

  function agendar(evento: FormEvent) {
    evento.preventDefault();
    criar.mutate({
      inicio: new Date(`${dia}T${comeca}`).toISOString(),
      fim: new Date(`${dia}T${termina}`).toISOString(),
    });
  }

  return (
    <section
      aria-labelledby="titulo-provas"
      className="flex flex-col gap-4 rounded-lg border border-line bg-surface p-4"
    >
      <h2 id="titulo-provas" className="text-lg font-bold">
        Provas
      </h2>
      <p className="text-ink-muted">
        Durante a prova, o tutor fica pausado para os alunos desta disciplina.
      </p>

      {janelas.data && (
        <div className="flex flex-wrap items-center gap-3">
          <p role="status" className="font-bold">
            {ativa ? 'O tutor está pausado agora.' : 'O tutor está respondendo normalmente.'}
          </p>
          {ativa ? (
            <Botao
              variante="secundario"
              disabled={apagar.isPending}
              onClick={() => apagar.mutate(ativa.id)}
            >
              Desligar o modo prova
            </Botao>
          ) : (
            <Botao disabled={criar.isPending} onClick={() => criar.mutate({})}>
              Pausar o tutor agora
            </Botao>
          )}
        </div>
      )}

      <form onSubmit={agendar} className="flex flex-wrap items-end gap-3">
        <div>
          <label htmlFor="dia-prova" className="block text-sm font-bold">
            Dia da prova
          </label>
          <input
            id="dia-prova"
            type="date"
            required
            value={dia}
            onChange={(evento) => setDia(evento.target.value)}
            className="mt-1 min-h-12 rounded-lg border border-line-control bg-surface px-3 text-ink"
          />
        </div>
        <div>
          <label htmlFor="comeca" className="block text-sm font-bold">
            Começa às
          </label>
          <input
            id="comeca"
            type="time"
            required
            value={comeca}
            onChange={(evento) => setComeca(evento.target.value)}
            className="mt-1 min-h-12 rounded-lg border border-line-control bg-surface px-3 text-ink"
          />
        </div>
        <div>
          <label htmlFor="termina" className="block text-sm font-bold">
            Termina às
          </label>
          <input
            id="termina"
            type="time"
            required
            value={termina}
            onChange={(evento) => setTermina(evento.target.value)}
            className="mt-1 min-h-12 rounded-lg border border-line-control bg-surface px-3 text-ink"
          />
        </div>
        <Botao type="submit" variante="secundario" disabled={criar.isPending}>
          Agendar janela de prova
        </Botao>
      </form>
      {(criar.isError || apagar.isError) && (
        <p role="alert" className="text-danger-text">
          {motivo(criar.error ?? apagar.error)}
        </p>
      )}

      {janelas.data &&
        (agendadas.length === 0 ? (
          <p className="text-ink-muted">Nenhuma prova agendada.</p>
        ) : (
          <ul aria-label="Janelas de prova agendadas" className="flex flex-col gap-2">
            {agendadas.map((janela) => (
              <li
                key={janela.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-line p-3"
              >
                <span>{descrever(janela)}</span>
                <Botao
                  variante="secundario"
                  aria-label={`Apagar a janela de ${descrever(janela)}`}
                  disabled={apagar.isPending}
                  onClick={() => apagar.mutate(janela.id)}
                >
                  Apagar
                </Botao>
              </li>
            ))}
          </ul>
        ))}
    </section>
  );
}
