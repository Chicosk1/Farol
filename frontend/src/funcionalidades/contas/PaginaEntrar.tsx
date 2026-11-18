import { Navigate, useNavigate, useSearchParams } from 'react-router';

import { ENDERECO_DO_LOGIN_GOOGLE, tokenCsrf } from '../../api/cliente';
import { Avatar } from '../../componentes/Avatar';
import { Botao } from '../../componentes/Botao';
import { Icone } from '../../componentes/Icone';
import {
  loginDeDesenvolvimentoDisponivel,
  useEntrarEmDesenvolvimento,
  useEu,
  useFormasDeEntrar,
} from './sessao';

// Pessoas fictícias criadas pelo comando popular_demo (docs/desenvolvimento.md).
const PESSOAS_FICTICIAS = [
  {
    email: 'ana.souza@exemplo.edu.br',
    nome: 'Ana Souza',
    descricao: 'Aluna do 2º período de Sistemas de Informação',
    rotulo: 'Entrar como aluna',
  },
  {
    email: 'carlos.mendes@exemplo.edu.br',
    nome: 'Carlos Mendes',
    descricao: 'Professor de Estruturas de Dados',
    rotulo: 'Entrar como professor',
  },
] as const;

// O allauth devolve a pessoa a /entrar?erro=... quando o login com o Google não vale (ACE-RF-01).
const ERROS_DO_LOGIN: Record<string, string> = {
  conta_nao_verificada:
    'Confirme o seu e-mail no Google e tente de novo. O Farol só aceita contas com o e-mail verificado.',
  conta_externa:
    'Use a sua conta institucional. Este Farol só aceita contas do domínio da instituição.',
  conta_desativada:
    'A sua conta está desativada no Farol. Se isso parece um engano, fale com a secretaria do curso.',
  falha: 'Não foi possível entrar com o Google. Tente de novo.',
};

/** Tela de entrada, no formato do protótipo: cartão com a marca e as formas de entrar. */
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
    <main className="login" id="conteudo">
      <div className="login-card">
        <div className="fr-wordmark">
          <b>Farol</b>
          <span>Tutor de estudos</span>
        </div>
        <div className="stack-sm">
          <h1 className="page-title">Entrar no Farol</h1>
          <p className="muted">
            O tutor de estudos com IA da UNIMATER, com o material dos seus professores.
          </p>
        </div>

        {erro && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            {erro}
          </p>
        )}

        {formas.data?.google && (
          <form method="post" action={ENDERECO_DO_LOGIN_GOOGLE} className="stack-sm">
            <input type="hidden" name="csrfmiddlewaretoken" value={tokenCsrf() ?? ''} />
            <Botao type="submit" icone="school">
              Entrar com o Google
            </Botao>
            <p className="small muted login-hint">
              <Icone nome="shield-lock" />
              Use a conta Google da instituição. O Farol não cria senha nova.
            </p>
          </form>
        )}
        {formas.data && !formas.data.google && (
          <p className="small muted login-hint">
            <Icone nome="info-circle" />O login com o Google ainda não foi configurado neste
            ambiente.
          </p>
        )}

        {loginDeDesenvolvimentoDisponivel() && (
          <section aria-labelledby="titulo-dev" className="stack-sm">
            <h2 id="titulo-dev" className="section-title">
              Desenvolvimento
            </h2>
            <p className="small muted">Entre com uma pessoa fictícia do protótipo.</p>
            <div className="role-options">
              {PESSOAS_FICTICIAS.map((pessoa) => (
                <button
                  key={pessoa.email}
                  type="button"
                  className="role-option"
                  aria-label={pessoa.rotulo}
                  disabled={entrar.isPending}
                  onClick={() => entrarComo(pessoa.email)}
                >
                  <Avatar nome={pessoa.nome} grande />
                  <span className="role-option-text">
                    <span className="role-option-title">{pessoa.rotulo}</span>
                    <span className="small muted">
                      {pessoa.nome} · {pessoa.descricao}
                    </span>
                  </span>
                  <Icone nome="chevron-right" />
                </button>
              ))}
            </div>
            {entrar.isError && (
              <p role="alert" className="notice notice--danger">
                <Icone nome="alert-triangle" />
                Não foi possível entrar. Rode o comando popular_demo e tente de novo.
              </p>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
