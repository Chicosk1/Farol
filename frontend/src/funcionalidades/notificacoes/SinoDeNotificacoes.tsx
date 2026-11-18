import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Link } from 'react-router';

import { listarNotificacoes, marcarNotificacaoComoLida } from '../../api/cliente';
import { Botao } from '../../componentes/Botao';

/** De quanto em quanto tempo o sino busca avisos novos. */
const INTERVALO_EM_MS = 30_000;
const CHAVE = ['notificacoes'];

function rotuloDoSino(naoLidas: number): string {
  if (naoLidas === 0) return 'Notificações';
  return `Notificações: ${naoLidas} ${naoLidas === 1 ? 'não lida' : 'não lidas'}`;
}

/** O sino do cabeçalho: avisos como "Aula 5, Pilhas, está pronta para o tutor" (MAT-RF-06). */
export function SinoDeNotificacoes() {
  const clienteDeDados = useQueryClient();
  const [aberto, setAberto] = useState(false);
  const notificacoes = useQuery({
    queryKey: CHAVE,
    queryFn: listarNotificacoes,
    refetchInterval: INTERVALO_EM_MS,
  });
  const marcar = useMutation({
    mutationFn: marcarNotificacaoComoLida,
    onSuccess: () => clienteDeDados.invalidateQueries({ queryKey: CHAVE }),
  });

  // Sem a lista (carregando ou fora do ar), o sino não aparece: o resto da tela segue normal.
  if (!notificacoes.data) return null;
  const { notificacoes: lista, nao_lidas: naoLidas } = notificacoes.data;

  return (
    <div className="relative">
      <button
        type="button"
        aria-label={rotuloDoSino(naoLidas)}
        aria-expanded={aberto}
        aria-controls="lista-de-notificacoes"
        onClick={() => setAberto((valor) => !valor)}
        className="relative inline-flex min-h-12 min-w-12 items-center justify-center rounded-lg text-xl"
      >
        <span aria-hidden="true">🔔</span>
        {naoLidas > 0 && (
          <span
            aria-hidden="true"
            className="absolute right-0 top-0 rounded-full bg-brand-yellow px-1.5 text-xs font-bold text-on-yellow"
          >
            {naoLidas}
          </span>
        )}
      </button>
      {aberto && (
        <div
          id="lista-de-notificacoes"
          className="absolute right-0 z-10 mt-2 w-80 max-w-[90vw] rounded-lg border border-line bg-surface p-3 text-ink shadow-lg"
        >
          {lista.length === 0 ? (
            <p className="text-ink-muted">Nenhuma notificação.</p>
          ) : (
            <ul aria-label="Notificações" className="flex flex-col gap-2">
              {lista.map((notificacao) => (
                <li
                  key={notificacao.id}
                  className={`rounded-lg p-2 ${notificacao.lida ? '' : 'bg-accent-soft'}`}
                >
                  {notificacao.link ? (
                    <Link
                      to={notificacao.link}
                      onClick={() => {
                        setAberto(false);
                        if (!notificacao.lida) marcar.mutate(notificacao.id);
                      }}
                      className="font-bold underline"
                    >
                      {notificacao.texto}
                    </Link>
                  ) : (
                    <p className="font-bold">{notificacao.texto}</p>
                  )}
                  {!notificacao.lida && (
                    <Botao
                      variante="secundario"
                      className="mt-1"
                      aria-label={`Marcar como lida: ${notificacao.texto}`}
                      disabled={marcar.isPending}
                      onClick={() => marcar.mutate(notificacao.id)}
                    >
                      Marcar como lida
                    </Botao>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
