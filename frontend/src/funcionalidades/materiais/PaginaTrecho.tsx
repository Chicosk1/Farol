import { useQuery } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router';

import { obterTrecho } from '../../api/cliente';
import { classesDoBotao } from '../../componentes/classes';
import { Icone } from '../../componentes/Icone';

/**
 * A página citada pelo tutor, no formato de "página de papel" do protótipo: o texto da página com
 * o trecho destacado e o PDF original a um toque (MAT-RF-09).
 */
export function PaginaTrecho() {
  const trechoId = Number(useParams().id);
  const navegar = useNavigate();
  const trecho = useQuery({ queryKey: ['trecho', trechoId], queryFn: () => obterTrecho(trechoId) });
  const dados = trecho.data;

  return (
    <div className="page page--narrow">
      <button type="button" className="link-btn" onClick={() => navegar(-1)}>
        <Icone nome="arrow-left" />
        Voltar
      </button>
      {trecho.isPending && (
        <p role="status" className="muted">
          Abrindo o trecho citado…
        </p>
      )}
      {trecho.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível abrir este trecho. O material pode ter sido retirado.
        </p>
      )}
      {dados && (
        <>
          <div className="page-head">
            <div>
              <h1 className="page-title">
                Aula {dados.aula_numero}, página {dados.pagina}
              </h1>
              <p className="page-sub">{dados.aula_titulo} · PDF publicado pelo professor</p>
            </div>
            <a
              className={classesDoBotao('contorno')}
              href={`/api/materiais/${dados.material_id}/arquivo?pagina=${dados.pagina}#page=${dados.pagina}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Icone nome="external-link" />
              Abrir o PDF nesta página
              <span className="sr-only"> (em nova aba)</span>
            </a>
          </div>
          {dados.atualizado && (
            <p role="note" className="notice">
              <Icone nome="info-circle" />O professor publicou uma versão nova deste material. O
              texto abaixo é da versão citada; o PDF abre na versão atual.
            </p>
          )}
          <article className="paper" aria-label={`Texto da página ${dados.pagina}`}>
            <p className="paper-meta">
              Aula {dados.aula_numero} · {dados.aula_titulo}
            </p>
            <p className="trecho-texto">
              {dados.texto_da_pagina.slice(0, dados.inicio)}
              <mark className="cite-mark">
                {dados.texto_da_pagina.slice(dados.inicio, dados.fim)}
              </mark>
              {dados.texto_da_pagina.slice(dados.fim)}
            </p>
            <p className="paper-page">Página {dados.pagina}</p>
          </article>
          <p className="small muted modal-note">
            <Icone nome="info-circle" />
            Trecho destacado: a parte do material que o tutor usou na resposta.
          </p>
        </>
      )}
    </div>
  );
}
