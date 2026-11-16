import { useNavigate } from 'react-router';

import { Botao } from '../componentes/Botao';
import { useEu, useSair } from '../funcionalidades/contas/sessao';

/** Página provisória da primeira fatia: mostra quem entrou. As disciplinas chegam na ACE-T33. */
export function PaginaInicial() {
  const eu = useEu();
  const sair = useSair();
  const navegar = useNavigate();

  return (
    <main id="conteudo" className="mx-auto max-w-2xl p-4">
      <h1 className="text-2xl font-extrabold text-ink">Farol</h1>
      <p className="mt-2 text-ink-muted">Tutor de estudos com IA da UNIMATER.</p>
      {eu.data && (
        <section aria-label="Sessão" className="mt-6">
          <p className="font-bold text-ink">Olá, {eu.data.nome}</p>
          <p className="text-ink-muted">Perfil: {eu.data.perfil_ativo}</p>
          <Botao
            variante="secundario"
            className="mt-3"
            onClick={() => sair.mutate(undefined, { onSuccess: () => navegar('/entrar') })}
          >
            Sair
          </Botao>
        </section>
      )}
    </main>
  );
}
