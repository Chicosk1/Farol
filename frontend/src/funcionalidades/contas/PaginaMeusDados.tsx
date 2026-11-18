import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { apagarHistorico, obterHistorico } from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { EstadoVazio } from '../../componentes/EstadoVazio';
import { Icone } from '../../componentes/Icone';

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
    <div className="page page--narrow">
      <div className="page-head">
        <div>
          <h1 className="page-title">Meus dados</h1>
          <p className="page-sub">O que o Farol guarda sobre você, e como apagar</p>
        </div>
      </div>

      <p className="privacy-note">
        <Icone nome="shield-lock" />O Farol guarda as suas conversas com o tutor para você continuar
        de onde parou. O professor não vê as suas conversas.
      </p>

      <section className="panel stack" aria-labelledby="titulo-historico">
        <h2 id="titulo-historico" className="card-heading">
          <Icone nome="message-circle" />
          Conversas com o tutor
        </h2>
        {historico.isPending && (
          <p role="status" className="muted">
            Carregando o histórico…
          </p>
        )}
        {historico.isError && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível carregar o histórico. Tente de novo em instantes.
          </p>
        )}
        {historico.data &&
          (historico.data.length === 0 ? (
            <EstadoVazio
              icone="message-circle"
              titulo="Nenhuma conversa guardada"
              texto="Você não tem conversas guardadas com o tutor."
            />
          ) : (
            <>
              <ul aria-label="Conversas guardadas" className="list">
                {historico.data.map((conversa) => (
                  <li key={conversa.disciplina_id} className="list-row">
                    <span className="file-icon file-icon--accent">
                      <Icone nome="message-circle" />
                    </span>
                    <span className="list-row-main">
                      <span className="strong">{conversa.disciplina_nome}</span>
                      <span className="small muted">
                        {conversa.mensagens} {conversa.mensagens === 1 ? 'mensagem' : 'mensagens'} ·
                        última em {DATA.format(new Date(conversa.ultima_em))}
                      </span>
                    </span>
                  </li>
                ))}
              </ul>
              {confirmando ? (
                <div
                  role="group"
                  aria-labelledby="confirmar-apagar"
                  className="notice notice--danger stack-sm"
                >
                  <p id="confirmar-apagar" className="strong">
                    Apagar todas as conversas com o tutor? Não dá para desfazer.
                  </p>
                  <div className="row">
                    <Botao pequeno disabled={apagar.isPending} onClick={() => apagar.mutate()}>
                      Sim, apagar meu histórico
                    </Botao>
                    <Botao variante="contorno" pequeno onClick={() => setConfirmando(false)}>
                      Cancelar
                    </Botao>
                  </div>
                </div>
              ) : (
                <div className="row">
                  <Botao variante="contorno" icone="trash" onClick={() => setConfirmando(true)}>
                    Apagar meu histórico
                  </Botao>
                </div>
              )}
            </>
          ))}
        <p role="status" className="bubble-note">
          {apagar.isSuccess ? 'Histórico apagado.' : ''}
        </p>
        {apagar.isError && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível apagar o histórico. Tente de novo.
          </p>
        )}
      </section>
    </div>
  );
}
