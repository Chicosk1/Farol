import { Navigate, useNavigate, useSearchParams } from 'react-router';

import { ENDERECO_DO_LOGIN_GOOGLE, tokenCsrf } from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import {
  loginDeDesenvolvimentoDisponivel,
  useEntrarEmDesenvolvimento,
  useEu,
  useFormasDeEntrar,
} from './sessao';

// Pessoas fictícias criadas pelo comando popular_demo (docs/desenvolvimento.md).
const ALUNA = 'ana.souza@exemplo.edu.br';
const PROFESSOR = 'carlos.mendes@exemplo.edu.br';

// O allauth devolve a pessoa a /entrar?erro=... quando o login com o Google não vale (ACE-RF-01).
const ERROS_DO_LOGIN: Record<string, string> = {
  conta_externa:
    'Use a sua conta institucional. Contas pessoais do Google e de outras instituições não entram no Farol.',
  conta_desativada:
    'A sua conta está desativada no Farol. Se isso parece um engano, fale com a secretaria do curso.',
  falha: 'Não foi possível entrar com o Google. Tente de novo.',
};

export function PaginaEntrar() {
  const eu = useEu();
  const formas = useFormasDeEntrar();
  const entrar = useEntrarEmDesenvolvimento();
  const navegar = useNavigate();
  const [parametros] = useSearchParams();
  const erro = ERROS_DO_LOGIN[parametros.get('erro') ?? ''];

  if (eu.data) {
    return <Navigate to="/" replace />;
  }

  const entrarComo = (email: string) => entrar.mutate(email, { onSuccess: () => navegar('/') });

  return (
    <main id="conteudo" className="mx-auto max-w-md p-4">
      <h1 className="text-2xl font-extrabold text-ink">Entrar no Farol</h1>

      {erro && (
        <p role="alert" className="mt-4 rounded-md bg-danger-soft p-3 text-danger-text">
          {erro}
        </p>
      )}

      {formas.data?.google && (
        <form method="post" action={ENDERECO_DO_LOGIN_GOOGLE} className="mt-6">
          <p className="text-ink-muted">
            Entre com a conta Google da instituição, sem criar senha nova.
          </p>
          <input type="hidden" name="csrfmiddlewaretoken" value={tokenCsrf() ?? ''} />
          <Botao type="submit" className="mt-3 w-full">
            Entrar com o Google
          </Botao>
        </form>
      )}
      {formas.data && !formas.data.google && (
        <p className="mt-4 text-ink-muted">
          O login com o Google ainda não foi configurado neste ambiente.
        </p>
      )}

      {loginDeDesenvolvimentoDisponivel() && (
        <section aria-labelledby="titulo-dev" className="mt-8">
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
