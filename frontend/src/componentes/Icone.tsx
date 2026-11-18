import { ICONES, type NomeDoIcone } from './icones';

/** Ícone do design system (Tabler), decorativo: quem dá o nome acessível é o elemento em volta. */
export function Icone({ nome }: { nome: NomeDoIcone }) {
  return (
    <i className="fr-ico" aria-hidden="true">
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {ICONES[nome].map((traco) => (
          <path key={traco} d={traco} />
        ))}
      </svg>
    </i>
  );
}
