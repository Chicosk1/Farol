import { useEu } from '../funcionalidades/contas/sessao';
import { FavoritasNaInicial } from '../funcionalidades/disciplinas/FavoritasNaInicial';

/** Tela inicial: as disciplinas favoritas no topo e, abaixo, quem entrou. */
export function PaginaInicial() {
  const eu = useEu();

  return (
    <div className="page">
      <h1 className="text-2xl font-extrabold text-ink">Farol</h1>
      <p className="mt-2 text-ink-muted">Tutor de estudos com IA da UNIMATER.</p>
      <FavoritasNaInicial />
      {eu.data && (
        <section aria-label="Sessão" className="mt-6">
          <p className="font-bold text-ink">Olá, {eu.data.nome}</p>
          <p className="text-ink-muted">Perfil: {eu.data.perfil_ativo}</p>
        </section>
      )}
    </div>
  );
}
