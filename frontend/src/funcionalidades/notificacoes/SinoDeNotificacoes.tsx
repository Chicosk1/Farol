import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router';

import { listarNotificacoes, marcarNotificacaoComoLida } from '../../api/cliente';
import { usePopover } from '../../app/popover';
import { Icone } from '../../componentes/Icone';

/** De quanto em quanto tempo o sino busca avisos novos. */
const INTERVALO_EM_MS = 30_000;
const CHAVE = ['notificacoes'];

function rotuloDoSino(naoLidas: number): string {
  if (naoLidas === 0) return 'Notificações';
  return `Notificações: ${naoLidas} ${naoLidas === 1 ? 'não lida' : 'não lidas'}`;
}

/**
 * O sino do cabeçalho, como no protótipo: avisos como "Aula 5, Pilhas, está pronta para o tutor"
 * (MAT-RF-06) e as dúvidas novas (DUV-RF-06). O ponto vermelho marca que há avisos não lidos.
 */
export function SinoDeNotificacoes() {
  const clienteDeDados = useQueryClient();
  const { aberto, botao, area, alternar, fechar, aoTeclar } = usePopover();
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
    <div ref={area} onKeyDown={aoTeclar}>
      <button
        ref={botao}
        type="button"
        className="fr-icon-btn"
        aria-label={rotuloDoSino(naoLidas)}
        aria-expanded={aberto}
        aria-controls="lista-de-notificacoes"
        onClick={alternar}
      >
        <Icone nome="bell" />
        {naoLidas > 0 && <span className="fr-dot" aria-hidden="true" />}
      </button>
      {aberto && (
        <div id="lista-de-notificacoes" className="popover">
          <p className="popover-title">Notificações</p>
          {lista.length === 0 ? (
            <p className="popover-item muted">Nenhuma notificação.</p>
          ) : (
            <ul aria-label="Notificações">
              {lista.map((notificacao) => (
                <li
                  key={notificacao.id}
                  className={notificacao.lida ? 'popover-item' : 'popover-item is-unread'}
                >
                  <Icone nome={notificacao.lida ? 'circle-check' : 'bell'} />
                  <div className="stack-sm">
                    {notificacao.link ? (
                      <Link
                        to={notificacao.link}
                        onClick={() => {
                          fechar();
                          if (!notificacao.lida) marcar.mutate(notificacao.id);
                        }}
                      >
                        {notificacao.texto}
                      </Link>
                    ) : (
                      <p>{notificacao.texto}</p>
                    )}
                    {!notificacao.lida && (
                      <button
                        type="button"
                        className="link-btn"
                        aria-label={`Marcar como lida: ${notificacao.texto}`}
                        disabled={marcar.isPending}
                        onClick={() => marcar.mutate(notificacao.id)}
                      >
                        Marcar como lida
                      </button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
