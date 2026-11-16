import { useQuery } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';

import { obterAvisoDePrivacidade } from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { useConfirmarCienciaDoAviso } from './sessao';

/**
 * Aviso de privacidade (ACE-RF-08): aparece na primeira entrada do aluno e a cada nova versão, e
 * só some quando ele confirma que leu. Não fecha com Esc de propósito.
 */
export function AvisoDePrivacidade() {
  const aviso = useQuery({ queryKey: ['aviso-privacidade'], queryFn: obterAvisoDePrivacidade });
  const confirmar = useConfirmarCienciaDoAviso();
  const caixa = useRef<HTMLDivElement>(null);

  // Leva o foco para dentro do aviso assim que o texto aparece.
  useEffect(() => {
    if (aviso.data) {
      caixa.current?.focus();
    }
  }, [aviso.data]);

  if (!aviso.data) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-chrome/80 p-4 sm:items-center">
      <div
        ref={caixa}
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-aviso"
        tabIndex={-1}
        className="max-h-full w-full max-w-lg overflow-y-auto rounded-lg bg-surface p-5 text-ink"
      >
        <h2 id="titulo-aviso" className="text-xl font-extrabold">
          {aviso.data.titulo}
        </h2>
        {aviso.data.itens.map((item) => (
          <section key={item.titulo} className="mt-4">
            <h3 className="font-bold">{item.titulo}</h3>
            <p className="text-ink-soft">{item.texto}</p>
          </section>
        ))}
        {confirmar.isError && (
          <p role="alert" className="mt-4 text-danger-text">
            Não foi possível registrar a sua confirmação. Tente de novo.
          </p>
        )}
        <Botao
          className="mt-5 w-full"
          disabled={confirmar.isPending}
          onClick={() => confirmar.mutate(aviso.data.versao)}
        >
          Entendi
        </Botao>
      </div>
    </div>
  );
}
