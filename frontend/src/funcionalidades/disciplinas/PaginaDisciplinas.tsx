import { useEffect, useState } from 'react';

import { Botao } from '../../componentes/Botao';
import { useDisciplinas } from './consultas';

type Visao = 'grade' | 'lista';

/** Espera o texto parar de mudar antes de buscar, para não chamar a API a cada tecla. */
function useTextoEstavel(texto: string, esperaEmMs = 250): string {
  const [estavel, setEstavel] = useState(texto);
  useEffect(() => {
    const espera = setTimeout(() => setEstavel(texto), esperaEmMs);
    return () => clearTimeout(espera);
  }, [texto, esperaEmMs]);
  return estavel;
}

function rotuloDeQuantidade(quantidade: number): string {
  return `${quantidade} ${quantidade === 1 ? 'disciplina' : 'disciplinas'}`;
}

export function PaginaDisciplinas() {
  const [digitado, setDigitado] = useState('');
  const [visao, setVisao] = useState<Visao>('grade');
  const disciplinas = useDisciplinas(useTextoEstavel(digitado));

  return (
    <main id="conteudo" className="mx-auto max-w-5xl p-4">
      <h1 className="text-2xl font-extrabold text-ink">Disciplinas</h1>

      <div className="mt-4 flex flex-wrap items-end gap-3">
        <div className="min-w-0 flex-1">
          <label htmlFor="busca" className="block text-sm font-bold text-ink">
            Buscar disciplina
          </label>
          <input
            id="busca"
            type="search"
            value={digitado}
            onChange={(evento) => setDigitado(evento.target.value)}
            placeholder="Digite parte do nome"
            className="mt-1 min-h-12 w-full rounded-lg border border-line-control bg-surface px-3 text-ink"
          />
        </div>
        <div role="group" aria-label="Forma de exibição" className="flex gap-2">
          <Botao
            variante="secundario"
            aria-pressed={visao === 'grade'}
            onClick={() => setVisao('grade')}
          >
            Ver em grade
          </Botao>
          <Botao
            variante="secundario"
            aria-pressed={visao === 'lista'}
            onClick={() => setVisao('lista')}
          >
            Ver em lista
          </Botao>
        </div>
      </div>

      {disciplinas.isError && (
        <p role="alert" className="mt-4 text-danger-text">
          Não foi possível carregar as disciplinas. Tente de novo em instantes.
        </p>
      )}
      {disciplinas.isPending && (
        <p role="status" className="mt-4 text-ink-muted">
          Carregando disciplinas…
        </p>
      )}
      {disciplinas.data && (
        <>
          <p role="status" className="mt-4 text-ink-muted">
            {rotuloDeQuantidade(disciplinas.data.length)}
          </p>
          {disciplinas.data.length === 0 ? (
            <p className="mt-2 text-ink">Nenhuma disciplina encontrada.</p>
          ) : (
            <ul
              aria-label="Disciplinas"
              data-visao={visao}
              className={
                visao === 'grade'
                  ? 'mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3'
                  : 'mt-2 flex flex-col gap-2'
              }
            >
              {disciplinas.data.map((disciplina) => (
                <li
                  key={disciplina.id}
                  className="rounded-lg border border-line bg-surface p-4 text-ink"
                >
                  <p className="font-bold">{disciplina.nome}</p>
                  <p className="text-sm text-ink-muted">
                    {disciplina.codigo} · {disciplina.turma}
                  </p>
                  <p className="text-sm text-ink-muted">Prof. {disciplina.professor_nome}</p>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </main>
  );
}
