import { Link } from 'react-router';

export function PaginaNaoEncontrada() {
  return (
    <main id="conteudo" className="mx-auto max-w-2xl p-4">
      <h1 className="text-2xl font-extrabold text-ink">Página não encontrada</h1>
      <p className="mt-2 text-ink-muted">Este endereço não existe no Farol.</p>
      <Link to="/" className="mt-4 inline-block font-bold text-accent underline">
        Voltar para o início
      </Link>
    </main>
  );
}
