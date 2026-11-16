import { Navigate, useNavigate } from 'react-router';

import { Botao } from '../../componentes/Botao';
import { loginDeDesenvolvimentoDisponivel, useEntrarEmDesenvolvimento, useEu } from './sessao';

// Pessoas fictícias criadas pelo comando popular_demo (docs/desenvolvimento.md).
const ALUNA = 'ana.souza@exemplo.edu.br';
const PROFESSOR = 'carlos.mendes@exemplo.edu.br';

export function PaginaEntrar() {
  const eu = useEu();
  const entrar = useEntrarEmDesenvolvimento();
  const navegar = useNavigate();

  if (eu.data) {
    return <Navigate to="/" replace />;
  }

  const entrarComo = (email: string) => entrar.mutate(email, { onSuccess: () => navegar('/') });

  return (
    <main id="conteudo" className="mx-auto max-w-md p-4">
      <h1 className="text-2xl font-extrabold text-ink">Entrar no Farol</h1>
      <p className="mt-2 text-ink-muted">
        O login com a conta institucional chega quando a instituição definir o provedor.
      </p>

      {loginDeDesenvolvimentoDisponivel() && (
        <section aria-labelledby="titulo-dev" className="mt-6">
          <h2 id="titulo-dev" className="text-base font-bold text-ink">
            Desenvolvimento
          </h2>
          <p className="mt-1 text-ink-muted">Entre com uma pessoa fictícia do protótipo.</p>
          <div className="mt-3 flex flex-col gap-3">
            <Botao onClick={() => entrarComo(ALUNA)} disabled={entrar.isPending}>
              Entrar como aluna
            </Botao>
            <Botao
              variante="secundario"
              onClick={() => entrarComo(PROFESSOR)}
              disabled={entrar.isPending}
            >
              Entrar como professor
            </Botao>
          </div>
          {entrar.isError && (
            <p role="alert" className="mt-3 text-danger-text">
              Não foi possível entrar. Rode o comando popular_demo e tente de novo.
            </p>
          )}
        </section>
      )}
    </main>
  );
}
