import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router';

import { listarNotificacoes, type Notificacao } from '../../api/cliente';
import { quando } from '../../app/datas';
import { Icone } from '../../componentes/Icone';
import type { NomeDoIcone } from '../../componentes/icones';

const QUANTAS = 5;

const ICONES: Record<Notificacao['tipo'], NomeDoIcone> = {
  material_pronto: 'file-text',
  material_atencao: 'alert-triangle',
  material_erro: 'circle-x',
  duvida_nova: 'message-question',
  orcamento_ia: 'alert-triangle',
};

/** As novidades da tela inicial, como no protótipo: as notificações mais recentes. */
export function Novidades() {
  // A mesma consulta do sino: as duas mostram os mesmos avisos.
  const notificacoes = useQuery({ queryKey: ['notificacoes'], queryFn: listarNotificacoes });
  const lista = notificacoes.data?.notificacoes.slice(0, QUANTAS) ?? [];

  return (
    <section className="stack" aria-labelledby="titulo-novidades">
      <h2 id="titulo-novidades" className="section-title">
        Novidades
      </h2>
      <ul className="panel list">
        {lista.length === 0 && (
          <li className="list-row muted">
            {notificacoes.isError
              ? 'Não foi possível carregar as novidades agora.'
              : 'Nenhuma novidade por enquanto.'}
          </li>
        )}
        {lista.map((notificacao) => (
          <li key={notificacao.id} className="list-row">
            <Icone nome={ICONES[notificacao.tipo]} />
            <div>
              <p>
                {notificacao.link ? (
                  <Link to={notificacao.link}>{notificacao.texto}</Link>
                ) : (
                  notificacao.texto
                )}
              </p>
              {notificacao.criada_em && (
                <p className="small muted">{quando(notificacao.criada_em)}</p>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
