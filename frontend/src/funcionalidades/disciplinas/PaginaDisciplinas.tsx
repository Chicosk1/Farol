import { useEffect, useId, useState } from 'react';
import { Link } from 'react-router';

import type { Disciplina, FiltroDeDisciplinas } from '../../api/cliente';
import { ListaDeAbas } from '../../componentes/Abas';
import { EstadoVazio } from '../../componentes/EstadoVazio';
import { Icone } from '../../componentes/Icone';
import type { NomeDoIcone } from '../../componentes/icones';
import { useEu } from '../contas/sessao';
import { CartaoDeDisciplina, LinhaDeDisciplina } from './CartaoDeDisciplina';
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

function listaVazia(
  aba: FiltroDeDisciplinas,
  comBusca: boolean,
): { icone: NomeDoIcone; titulo: string; texto: string } {
  if (comBusca) {
    return {
      icone: 'search',
      titulo: 'Nenhuma disciplina encontrada',
      texto: 'Tente outro nome ou volte para a aba Todas.',
    };
  }
  if (aba === 'favoritas') {
    return {
      icone: 'star',
      titulo: 'Nenhuma favorita ainda',
      texto: 'Você ainda não tem disciplinas favoritas. Use a estrela, na aba Todas, para marcar.',
    };
  }
  if (aba === 'com-tutor') {
    return {
      icone: 'message-circle',
      titulo: 'Nenhum tutor disponível ainda',
      texto: 'Nenhuma disciplina com material pronto para o tutor ainda.',
    };
  }
  return {
    icone: 'school',
    titulo: 'Nenhuma disciplina encontrada',
    texto: 'Se você já está matriculado, fale com a secretaria do curso para conferir a matrícula.',
  };
}

function rotuloDeQuantidade(quantidade: number): string {
  return `${quantidade} ${quantidade === 1 ? 'disciplina' : 'disciplinas'}`;
}

function Atalho({ para, icone, rotulo }: { para: string; icone: NomeDoIcone; rotulo: string }) {
  return (
    <Link className="fr-icon-btn fr-icon-btn--sm" to={para} aria-label={rotulo}>
      <Icone nome={icone} />
    </Link>
  );
}

/** Atalhos do cartão: materiais e tutor para o aluno; materiais, dúvidas e configuração para o professor. */
function Atalhos({ disciplina, professor }: { disciplina: Disciplina; professor: boolean }) {
  const base = `/disciplinas/${disciplina.id}`;
  return (
    <>
      <Atalho para={`${base}/materiais`} icone="files" rotulo={`Materiais de ${disciplina.nome}`} />
      {professor && (
        <>
          <Atalho
            para={`${base}/duvidas`}
            icone="message-question"
            rotulo={`Dúvidas de ${disciplina.nome}`}
          />
          <Atalho
            para={`${base}/tutor/configuracao`}
            icone="settings"
            rotulo={`Configurar o tutor de ${disciplina.nome}`}
          />
        </>
      )}
      {!professor && disciplina.tem_tutor && (
        <Atalho
          para={`${base}/tutor`}
          icone="message-circle"
          rotulo={`Tutor de ${disciplina.nome}`}
        />
      )}
    </>
  );
}

/** Disciplinas no formato do protótipo: busca, abas, grade de cartões ou lista (ACE-RF-10). */
export function PaginaDisciplinas() {
  const [digitado, setDigitado] = useState('');
  const [visao, setVisao] = useState<Visao>('grade');
  const [aba, setAba] = useState<FiltroDeDisciplinas>('todas');
  const disciplinas = useDisciplinas(useTextoEstavel(digitado), aba);
  const favoritar = useDefinirFavorito();
  const professor = useEu().data?.perfil_ativo === 'professor';
  const base = useId();
  const idDoPainel = `${base}-painel`;
  const destino = (disciplina: Disciplina) => `/disciplinas/${disciplina.id}/materiais`;

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Disciplinas</h1>
          <p className="page-sub">
            {professor
              ? 'As disciplinas que você leciona'
              : 'As disciplinas em que você está matriculado'}
          </p>
        </div>
      </div>

      <div className="toolbar">
        <div className="fr-input-wrap toolbar-search">
          <Icone nome="search" />
          <input
            className="fr-input"
            type="search"
            value={digitado}
            onChange={(evento) => setDigitado(evento.target.value)}
            placeholder="Buscar pelo nome da disciplina"
            aria-label="Buscar disciplina"
          />
        </div>
        <ListaDeAbas
          rotulo="Filtrar disciplinas"
          abas={ABAS}
          ativa={aba}
          aoMudar={setAba}
          base={base}
          idDoPainel={idDoPainel}
        />
        <div className="fr-tabs fr-tabs--icon" role="group" aria-label="Modo de exibição">
          <button
            type="button"
            className="fr-tab"
            aria-pressed={visao === 'grade'}
            aria-label="Ver em grade"
            onClick={() => setVisao('grade')}
          >
            <Icone nome="layout-grid" />
          </button>
          <button
            type="button"
            className="fr-tab"
            aria-pressed={visao === 'lista'}
            aria-label="Ver em lista"
            onClick={() => setVisao('lista')}
          >
            <Icone nome="list" />
          </button>
        </div>
      </div>

      <section id={idDoPainel} role="tabpanel" aria-labelledby={`${base}-${aba}`} className="stack">
        {disciplinas.isError && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível carregar as disciplinas. Tente de novo em instantes.
          </p>
        )}
        {favoritar.isError && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível atualizar o favorito. Tente de novo.
          </p>
        )}
        {disciplinas.isPending && (
          <p role="status" className="muted">
            Carregando disciplinas…
          </p>
        )}
        {disciplinas.data && (
          <>
            <p role="status" className="small muted">
              {rotuloDeQuantidade(disciplinas.data.length)}
            </p>
            {disciplinas.data.length === 0 ? (
              <EstadoVazio {...listaVazia(aba, digitado.trim() !== '')} />
            ) : (
              <ul
                aria-label="Disciplinas"
                data-visao={visao}
                className={visao === 'grade' ? 'grid-cards' : 'panel list-panel'}
              >
                {disciplinas.data.map((disciplina) => (
                  <li key={disciplina.id}>
                    {visao === 'grade' ? (
                      <CartaoDeDisciplina
                        disciplina={disciplina}
                        destino={destino(disciplina)}
                        atalhos={<Atalhos disciplina={disciplina} professor={professor} />}
                        favoritando={favoritar.isPending}
                        aoFavoritar={(favorita) =>
                          favoritar.mutate({ id: disciplina.id, favorita })
                        }
                      />
                    ) : (
                      <LinhaDeDisciplina disciplina={disciplina} destino={destino(disciplina)} />
                    )}
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </section>
    </div>
  );
}
