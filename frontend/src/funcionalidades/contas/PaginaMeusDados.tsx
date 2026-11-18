import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { apagarHistorico, obterHistorico } from '../../api/cliente';
import { Botao } from '../../componentes/Botao';

const DATA = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
});

/** O que o Farol guarda da aluna e o botão para apagar o histórico do tutor (ACE-RF-09). */
export function PaginaMeusDados() {
  const clienteDeDados = useQueryClient();
  const historico = useQuery({ queryKey: ['historico'], queryFn: obterHistorico });
  const [confirmando, setConfirmando] = useState(false);
  const apagar = useMutation({
    mutationFn: apagarHistorico,
    onSuccess: async () => {
      setConfirmando(false);
      // As conversas guardadas no cache das telas do tutor também deixam de existir.
      clienteDeDados.removeQueries({ queryKey: ['tutor'] });
      await clienteDeDados.invalidateQueries({ queryKey: ['historico'] });
    },
  });

  return (
    <div className="page">
      <h1 className="text-2xl font-extrabold">Meus dados</h1>
      <p className="text-ink-muted">
        O Farol guarda as suas conversas com o tutor para você continuar de onde parou. O professor
        não vê as suas conversas.
      </p>

      <section aria-labelledby="titulo-historico" className="flex flex-col gap-3">
        <h2 id="titulo-historico" className="text-lg font-bold">
          Conversas com o tutor
        </h2>
        {historico.isPending && (
          <p role="status" className="text-ink-muted">
            Carregando o histórico…
          </p>
        )}
        {historico.isError && (
          <p role="alert" className="text-danger-text">
            Não foi possível carregar o histórico. Tente de novo em instantes.
          </p>
        )}
        {historico.data &&
          (historico.data.length === 0 ? (
            <p className="text-ink-muted">Você não tem conversas guardadas com o tutor.</p>
          ) : (
            <>
              <ul aria-label="Conversas guardadas" className="flex flex-col gap-2">
                {historico.data.map((conversa) => (
                  <li
                    key={conversa.disciplina_id}
                    className="rounded-lg border border-line bg-surface p-3"
                  >
                    <p className="font-bold">{conversa.disciplina_nome}</p>
                    <p className="text-sm text-ink-muted">
                      {conversa.mensagens} {conversa.mensagens === 1 ? 'mensagem' : 'mensagens'} ·
                      última em {DATA.format(new Date(conversa.ultima_em))}
                    </p>
                  </li>
                ))}
              </ul>
              {confirmando ? (
                <div
                  role="group"
                  aria-labelledby="confirmar-apagar"
                  className="rounded-lg border border-danger bg-danger-soft p-3"
                >
                  <p id="confirmar-apagar" className="font-bold text-danger-text">
                    Apagar todas as conversas com o tutor? Não dá para desfazer.
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <Botao disabled={apagar.isPending} onClick={() => apagar.mutate()}>
                      Sim, apagar meu histórico
                    </Botao>
                    <Botao variante="secundario" onClick={() => setConfirmando(false)}>
                      Cancelar
                    </Botao>
                  </div>
                </div>
              ) : (
                <Botao
                  variante="secundario"
                  className="self-start"
                  onClick={() => setConfirmando(true)}
                >
                  Apagar meu histórico
                </Botao>
              )}
            </>
          ))}
        <p role="status" className="text-success-text">
          {apagar.isSuccess ? 'Histórico apagado.' : ''}
        </p>
        {apagar.isError && (
          <p role="alert" className="text-danger-text">
            Não foi possível apagar o histórico. Tente de novo.
          </p>
        )}
      </section>
    </div>
  );
}
