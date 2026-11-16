import { useEu } from '../funcionalidades/contas/sessao';

/** Página provisória da primeira fatia: mostra quem entrou. Os favoritos chegam na ACE-T35. */
export function PaginaInicial() {
  const eu = useEu();

  return (
    <main id="conteudo" className="mx-auto max-w-2xl p-4">
      <h1 className="text-2xl font-extrabold text-ink">Farol</h1>
      <p className="mt-2 text-ink-muted">Tutor de estudos com IA da UNIMATER.</p>
      {eu.data && (
        <section aria-label="Sessão" className="mt-6">
          <p className="font-bold text-ink">Olá, {eu.data.nome}</p>
          <p className="text-ink-muted">Perfil: {eu.data.perfil_ativo}</p>
        </section>
      )}
    </main>
  );
}
