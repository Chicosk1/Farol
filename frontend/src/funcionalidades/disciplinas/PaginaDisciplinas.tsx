import { useEffect, useState } from 'react';
import { Link } from 'react-router';

import type { FiltroDeDisciplinas } from '../../api/cliente';
import { Abas } from '../../componentes/Abas';
import { Botao } from '../../componentes/Botao';
import { useEu } from '../contas/sessao';
import { useDefinirFavorito, useDisciplinas } from './consultas';

type Visao = 'grade' | 'lista';

const ABAS = [
  { id: 'todas', rotulo: 'Todas' },
  { id: 'favoritas', rotulo: 'Favoritas' },
  { id: 'com-tutor', rotulo: 'Com tutor' },
] as const satisfies readonly { id: FiltroDeDisciplinas; rotulo: string }[];

/** Espera o texto parar de mudar antes de buscar, para não chamar a API a cada tecla. */
function useTextoEstavel(texto: string, esperaEmMs = 250): string {
  const [estavel, setEstavel] = useState(texto);
  useEffect(() => {
    const espera = setTimeout(() => setEstavel(texto), esperaEmMs);
    return () => clearTimeout(espera);
  }, [texto, esperaEmMs]);
  return estavel;
}

function mensagemDeLista(aba: FiltroDeDisciplinas, comBusca: boolean): string {
  if (comBusca) return 'Nenhuma disciplina encontrada.';
  if (aba === 'favoritas') {
    return 'Você ainda não tem disciplinas favoritas. Use a estrela, na aba Todas, para marcar.';
  }
  if (aba === 'com-tutor') {
    return 'Nenhuma disciplina com material pronto para o tutor ainda.';
  }
  return 'Nenhuma disciplina encontrada.';
}

function rotuloDeQuantidade(quantidade: number): string {
  return `${quantidade} ${quantidade === 1 ? 'disciplina' : 'disciplinas'}`;
}

export function PaginaDisciplinas() {
  const [digitado, setDigitado] = useState('');
  const [visao, setVisao] = useState<Visao>('grade');
  const [aba, setAba] = useState<FiltroDeDisciplinas>('todas');
  const disciplinas = useDisciplinas(useTextoEstavel(digitado), aba);
  const favoritar = useDefinirFavorito();
  const perfil = useEu().data?.perfil_ativo;

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

      <div className="mt-4">
        <Abas rotulo="Filtrar disciplinas" abas={ABAS} ativa={aba} aoMudar={setAba}>
          {disciplinas.isError && (
            <p role="alert" className="mt-4 text-danger-text">
              Não foi possível carregar as disciplinas. Tente de novo em instantes.
            </p>
          )}
          {favoritar.isError && (
            <p role="alert" className="mt-4 text-danger-text">
              Não foi possível atualizar o favorito. Tente de novo.
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
                <p className="mt-2 text-ink">{mensagemDeLista(aba, digitado.trim() !== '')}</p>
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
                      className="flex items-start justify-between gap-2 rounded-lg border border-line bg-surface p-4 text-ink"
                    >
                      <div>
                        <p className="font-bold">{disciplina.nome}</p>
                        <p className="text-sm text-ink-muted">
                          {disciplina.codigo} · {disciplina.turma}
                        </p>
                        <p className="text-sm text-ink-muted">Prof. {disciplina.professor_nome}</p>
                        {perfil === 'aluno' && (
                          <Link
                            to={`/disciplinas/${disciplina.id}/tutor`}
                            aria-label={`Tutor de ${disciplina.nome}`}
                            className="mt-2 inline-flex min-h-12 items-center font-bold text-accent underline"
                          >
                            Tutor
                          </Link>
                        )}
                        {perfil === 'professor' && (
                          <Link
                            to={`/disciplinas/${disciplina.id}/tutor/configuracao`}
                            aria-label={`Configurar o tutor de ${disciplina.nome}`}
                            className="mt-2 inline-flex min-h-12 items-center font-bold text-accent underline"
                          >
                            Configurar tutor
                          </Link>
                        )}
                        {(perfil === 'professor' || perfil === 'aluno') && (
                          <Link
                            to={`/disciplinas/${disciplina.id}/materiais`}
                            aria-label={`Materiais de ${disciplina.nome}`}
                            className="mt-2 inline-flex min-h-12 items-center font-bold text-accent underline"
                          >
                            Materiais
                          </Link>
                        )}
                        {perfil === 'professor' && (
                          <Link
                            to={`/disciplinas/${disciplina.id}/duvidas`}
                            aria-label={`Dúvidas de ${disciplina.nome}`}
                            className="mt-2 ml-4 inline-flex min-h-12 items-center font-bold text-accent underline"
                          >
                            Dúvidas
                          </Link>
                        )}
                      </div>
                      <button
                        type="button"
                        aria-label={`Favoritar ${disciplina.nome}`}
                        aria-pressed={disciplina.favorita}
                        disabled={favoritar.isPending}
                        onClick={() =>
                          favoritar.mutate({ id: disciplina.id, favorita: !disciplina.favorita })
                        }
                        className="min-h-12 min-w-12 rounded-lg text-2xl text-accent"
                      >
                        <span aria-hidden="true">{disciplina.favorita ? '★' : '☆'}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </Abas>
      </div>
    </main>
  );
}
