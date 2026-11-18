import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router';

import { obterTrecho } from '../../api/cliente';

/** A página citada pelo tutor, com o trecho destacado e o PDF original a um toque (MAT-RF-09). */
export function PaginaTrecho() {
  const trechoId = Number(useParams().id);
  const trecho = useQuery({ queryKey: ['trecho', trechoId], queryFn: () => obterTrecho(trechoId) });

  return (
    <main id="conteudo" className="mx-auto flex max-w-3xl flex-col gap-4 p-4 text-ink">
      {trecho.isPending && (
        <p role="status" className="text-ink-muted">
          Abrindo o trecho citado…
        </p>
      )}
      {trecho.isError && (
        <p role="alert" className="text-danger-text">
          Não foi possível abrir este trecho. O material pode ter sido retirado.
        </p>
      )}
      {trecho.data && (
        <>
          <div>
            <h1 className="text-2xl font-extrabold">
              Aula {trecho.data.aula_numero}: {trecho.data.aula_titulo}
            </h1>
            <p className="text-ink-muted">Página {trecho.data.pagina}</p>
          </div>
          {trecho.data.atualizado && (
            <p role="note" className="rounded-lg bg-warning-soft p-3 text-warning-text">
              O professor publicou uma versão nova deste material. O texto abaixo é da versão
              citada; o PDF abre na versão atual.
            </p>
          )}
          <article
            aria-label={`Texto da página ${trecho.data.pagina}`}
            className="whitespace-pre-wrap rounded-lg border border-line bg-surface p-4 leading-relaxed"
          >
            {trecho.data.texto_da_pagina.slice(0, trecho.data.inicio)}
            <mark className="rounded bg-brand-yellow px-0.5 text-on-yellow">
              {trecho.data.texto_da_pagina.slice(trecho.data.inicio, trecho.data.fim)}
            </mark>
            {trecho.data.texto_da_pagina.slice(trecho.data.fim)}
          </article>
          <a
            href={`/api/materiais/${trecho.data.material_id}/arquivo?pagina=${trecho.data.pagina}#page=${trecho.data.pagina}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex min-h-12 items-center self-start rounded-lg border border-line-control bg-surface px-4 font-bold underline"
          >
            Abrir o PDF nesta página
            <span className="sr-only"> (em nova aba)</span>
          </a>
        </>
      )}
    </main>
  );
}
