import { useQuery } from '@tanstack/react-query';

import { listarMateriaisDoAluno } from '../../api/cliente';
import { Icone } from '../../componentes/Icone';

function paginas(quantidade: number): string {
  return `${quantidade} ${quantidade === 1 ? 'página' : 'páginas'}`;
}

/**
 * Os materiais prontos da disciplina, por aula, como na lista do protótipo: cada linha abre o PDF
 * na primeira página (MAT-RF-08, MAT-RF-09).
 */
export function MateriaisDoAluno({ disciplinaId }: { disciplinaId: number }) {
  const materiais = useQuery({
    queryKey: ['materiais-do-aluno', disciplinaId],
    queryFn: () => listarMateriaisDoAluno(disciplinaId),
  });

  if (materiais.isPending) {
    return (
      <p role="status" className="panel muted">
        Carregando os materiais…
      </p>
    );
  }
  if (materiais.isError) {
    return (
      <p role="alert" className="notice notice--danger">
        <Icone nome="alert-triangle" />
        Não foi possível carregar os materiais. Tente de novo em instantes.
      </p>
    );
  }
  if (materiais.data.length === 0) {
    return (
      <ul className="panel list">
        <li className="list-row muted">
          O professor ainda não publicou material nesta disciplina.
        </li>
      </ul>
    );
  }
  return (
    <ul aria-label="Materiais da disciplina" className="panel list">
      {/* Da aula mais recente para a mais antiga, como no protótipo. */}
      {[...materiais.data]
        .sort((a, b) => b.aula_numero - a.aula_numero)
        .map((material) => (
          <li key={material.id}>
            <a
              className="list-row list-row--action"
              href={`/api/materiais/${material.id}/arquivo?pagina=1#page=1`}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`Abrir a aula ${material.aula_numero} (PDF em nova aba)`}
            >
              <span className="file-icon">
                <Icone nome="file-type-pdf" />
              </span>
              <span className="list-row-main">
                <span className="strong">
                  Aula {material.aula_numero} · {material.aula_titulo}
                </span>
                <span className="small muted">{paginas(material.paginas)}</span>
              </span>
              <Icone nome="eye" />
            </a>
          </li>
        ))}
    </ul>
  );
}
