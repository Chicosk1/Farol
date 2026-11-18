import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, DISCIPLINAS, FAVORITAS_VAZIAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const ESTRUTURAS = DISCIPLINAS.find((d) => d.nome === 'Estruturas de Dados')!;
const PAGINA = `/disciplinas/${ESTRUTURAS.id}/materiais`;

function simular(materiais: unknown[]) {
  return simularApi({
    'GET /api/eu': { corpo: ANA },
    ...FAVORITAS_VAZIAS,
    'GET /api/disciplinas': { corpo: DISCIPLINAS },
    [`GET /api/disciplinas/${ESTRUTURAS.id}/materiais`]: { corpo: materiais },
  });
}

describe('materiais da disciplina para a aluna (MAT-T33)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('lista as aulas com material pronto e abre o PDF na primeira página', async () => {
    simular([
      { id: 7, aula_numero: 4, aula_titulo: 'Listas encadeadas', paginas: 12 },
      { id: 8, aula_numero: 5, aula_titulo: 'Pilhas e filas', paginas: 1 },
    ]);
    const { container } = renderizarApp(PAGINA);

    const lista = await screen.findByRole('list', { name: 'Materiais da disciplina' });
    const [primeira, segunda] = within(lista).getAllByRole('listitem');
    expect(primeira).toHaveTextContent('Aula 4: Listas encadeadas');
    expect(primeira).toHaveTextContent('12 páginas');
    expect(segunda).toHaveTextContent('1 página');
    expect(within(lista).getByRole('link', { name: /Abrir a aula 4/ })).toHaveAttribute(
      'href',
      '/api/materiais/7/arquivo?pagina=1#page=1',
    );
    expect(screen.queryByLabelText('Arquivo PDF da aula')).toBeNull(); // sem envio para a aluna
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('avisa quando o professor ainda não publicou material', async () => {
    simular([]);
    renderizarApp(PAGINA);

    expect(
      await screen.findByText('O professor ainda não publicou material nesta disciplina.'),
    ).toBeInTheDocument();
  });

  it('a lista de disciplinas da aluna leva aos materiais', async () => {
    simular([]);
    const { roteador } = renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('link', { name: 'Materiais de Estruturas de Dados' }));

    await waitFor(() => expect(roteador.state.location.pathname).toBe(PAGINA));
  });
});
