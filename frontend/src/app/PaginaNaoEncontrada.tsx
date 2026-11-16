import { Link } from 'react-router';

export function PaginaNaoEncontrada() {
  return (
    <main id="conteudo">
      <h1>Página não encontrada</h1>
      <p>Este endereço não existe no Farol.</p>
      <Link to="/">Voltar para o início</Link>
    </main>
  );
}
