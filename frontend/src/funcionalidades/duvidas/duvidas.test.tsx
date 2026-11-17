import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { CARLOS, DISCIPLINAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const ESTRUTURAS = DISCIPLINAS.find((d) => d.nome === 'Estruturas de Dados')!;
const URL = `/api/disciplinas/${ESTRUTURAS.id}/duvidas`;
const PAGINA = `/disciplinas/${ESTRUTURAS.id}/duvidas`;

function dia(diasAtras: number): string {
  const data = new Date();
  data.setDate(data.getDate() - diasAtras);
  const mes = String(data.getMonth() + 1).padStart(2, '0');
  return `${data.getFullYear()}-${mes}-${String(data.getDate()).padStart(2, '0')}`;
}

/** API simulada com estado: mudar o status tira a dúvida das abertas. */
function simular() {
  const duvidas = [
    { id: 1, texto: 'A prova cobre árvores AVL?', data: dia(0), status: 'aberta', nova: true },
    { id: 2, texto: 'Vale ponto extra?', data: dia(3), status: 'aberta', nova: false },
  ];
  const lista = (status: string) => () => ({
    corpo: duvidas.filter((d) => d.status === status),
  });
  const rotas: Parameters<typeof simularApi>[0] = {
    'GET /api/eu': { corpo: CARLOS },
    'GET /api/disciplinas': { corpo: DISCIPLINAS },
    [`GET ${URL}?status=aberta`]: lista('aberta'),
    [`GET ${URL}?status=respondida`]: lista('respondida'),
  };
  for (const duvida of duvidas) {
    rotas[`PATCH ${URL}/${duvida.id}`] = (chamada) => {
      duvida.status = (chamada.corpo as { status: string }).status;
      duvida.nova = false;
      return { corpo: duvida };
    };
  }
  return simularApi(rotas);
}

describe('dúvidas da turma para o professor (DUV-T23)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mostra as dúvidas abertas com a marca Nova e há quanto tempo foram enviadas', async () => {
    simular();
    const { container } = renderizarApp(PAGINA);

    const lista = await screen.findByRole('list', { name: 'Dúvidas' });
    const [primeira, segunda] = within(lista).getAllByRole('listitem');
    expect(primeira).toHaveTextContent('Nova');
    expect(primeira).toHaveTextContent('Enviada hoje');
    expect(primeira).toHaveTextContent('A prova cobre árvores AVL?');
    expect(segunda).not.toHaveTextContent('Nova');
    expect(segunda).toHaveTextContent('Enviada há 3 dias');
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('respondida em aula sai das abertas e aparece na aba das respondidas', async () => {
    const { chamadas } = simular();
    renderizarApp(PAGINA);

    const lista = await screen.findByRole('list', { name: 'Dúvidas' });
    const primeira = within(lista).getAllByRole('listitem')[0]!;
    fireEvent.click(within(primeira).getByRole('button', { name: 'Respondida em aula' }));

    await waitFor(() => expect(screen.queryByText('A prova cobre árvores AVL?')).toBeNull());
    expect(chamadas.find((c) => c.metodo === 'PATCH')?.corpo).toEqual({ status: 'respondida' });
    fireEvent.click(screen.getByRole('tab', { name: 'Respondidas em aula' }));
    expect(await screen.findByText('A prova cobre árvores AVL?')).toBeInTheDocument();
  });

  it('oculta a dúvida ofensiva', async () => {
    simular();
    renderizarApp(PAGINA);

    fireEvent.click(
      await screen.findByRole('button', { name: 'Ocultar a dúvida: Vale ponto extra?' }),
    );

    await waitFor(() => expect(screen.queryByText('Vale ponto extra?')).toBeNull());
  });

  it('a lista de disciplinas do professor leva às dúvidas', async () => {
    simular();
    const { roteador } = renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('link', { name: 'Dúvidas de Estruturas de Dados' }));

    await waitFor(() => expect(roteador.state.location.pathname).toBe(PAGINA));
  });
});
