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
import { Icone } from '../../componentes/Icone';

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
    <section className="panel" aria-labelledby="titulo-provas">
      <h2 id="titulo-provas" className="card-heading">
        <Icone nome="lock" />
        Provas
      </h2>
      {janelas.data && (
        <div className="switch-row">
          <div className="switch-text">
            <p role="status" className="strong">
              {ativa ? 'O tutor está pausado agora.' : 'O tutor está respondendo normalmente.'}
            </p>
            <p className="small muted">
              Durante a prova, o tutor fica pausado para os alunos desta disciplina.
            </p>
            {ativa && (
              <p className="notice notice--danger">
                <Icone nome="lock" />O tutor está pausado para a turma. Desligue quando a prova
                terminar.
              </p>
            )}
          </div>
          {ativa ? (
            <Botao
              variante="contorno"
              pequeno
              disabled={apagar.isPending}
              onClick={() => apagar.mutate(ativa.id)}
            >
              Desligar o modo prova
            </Botao>
          ) : (
            <Botao pequeno icone="lock" disabled={criar.isPending} onClick={() => criar.mutate({})}>
              Pausar o tutor agora
            </Botao>
          )}
        </div>
      )}

      <form onSubmit={agendar} className="generator switch-row">
        <div className="fr-field">
          <label htmlFor="dia-prova" className="fr-label">
            Dia da prova
          </label>
          <input
            id="dia-prova"
            type="date"
            required
            className="fr-input"
            value={dia}
            onChange={(evento) => setDia(evento.target.value)}
          />
        </div>
        <div className="fr-field">
          <label htmlFor="comeca" className="fr-label">
            Começa às
          </label>
          <input
            id="comeca"
            type="time"
            required
            className="fr-input"
            value={comeca}
            onChange={(evento) => setComeca(evento.target.value)}
          />
        </div>
        <div className="fr-field">
          <label htmlFor="termina" className="fr-label">
            Termina às
          </label>
          <input
            id="termina"
            type="time"
            required
            className="fr-input"
            value={termina}
            onChange={(evento) => setTermina(evento.target.value)}
          />
        </div>
        <Botao type="submit" variante="contorno" icone="calendar" disabled={criar.isPending}>
          Agendar janela de prova
        </Botao>
      </form>
      {(criar.isError || apagar.isError) && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          {motivo(criar.error ?? apagar.error)}
        </p>
      )}

      {janelas.data &&
        (agendadas.length === 0 ? (
          <p className="small muted">Nenhuma prova agendada.</p>
        ) : (
          <ul aria-label="Janelas de prova agendadas" className="list">
            {agendadas.map((janela) => (
              <li key={janela.id} className="list-row">
                <Icone nome="calendar" />
                <span className="list-row-main">{descrever(janela)}</span>
                <button
                  type="button"
                  className="fr-icon-btn fr-icon-btn--sm"
                  aria-label={`Apagar a janela de ${descrever(janela)}`}
                  disabled={apagar.isPending}
                  onClick={() => apagar.mutate(janela.id)}
                >
                  <Icone nome="trash" />
                </button>
              </li>
            ))}
          </ul>
        ))}
    </section>
  );
}
