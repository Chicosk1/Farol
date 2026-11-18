import { useQuery } from '@tanstack/react-query';

import { listarMateriaisDoAluno } from '../../api/cliente';

function paginas(quantidade: number): string {
  return `${quantidade} ${quantidade === 1 ? 'página' : 'páginas'}`;
}

/** Os materiais prontos da disciplina, por aula, para a aluna abrir o PDF (MAT-RF-08, MAT-RF-09). */
export function MateriaisDoAluno({ disciplinaId }: { disciplinaId: number }) {
  const materiais = useQuery({
    queryKey: ['materiais-do-aluno', disciplinaId],
    queryFn: () => listarMateriaisDoAluno(disciplinaId),
  });

  if (materiais.isPending) {
    return (
      <p role="status" className="text-ink-muted">
        Carregando os materiais…
      </p>
    );
  }
  if (materiais.isError) {
    return (
      <p role="alert" className="text-danger-text">
        Não foi possível carregar os materiais. Tente de novo em instantes.
      </p>
    );
  }
  if (materiais.data.length === 0) {
    return (
      <p className="text-ink-muted">O professor ainda não publicou material nesta disciplina.</p>
    );
  }
  return (
    <ul aria-label="Materiais da disciplina" className="flex flex-col gap-2">
      {materiais.data.map((material) => (
        <li
          key={material.id}
          className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-line bg-surface p-4"
        >
          <div>
            <p className="font-bold">
              Aula {material.aula_numero}: {material.aula_titulo}
            </p>
            <p className="text-sm text-ink-muted">{paginas(material.paginas)}</p>
          </div>
          <a
            href={`/api/materiais/${material.id}/arquivo?pagina=1#page=1`}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`Abrir a aula ${material.aula_numero} (PDF em nova aba)`}
            className="inline-flex min-h-12 items-center rounded-lg border border-line-control px-4 font-bold text-ink underline"
          >
            Abrir PDF
          </a>
        </li>
      ))}
    </ul>
  );
}
