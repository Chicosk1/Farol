import { screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const PAGINA = 'Uma pilha segue a ordem LIFO. O último inserido é o primeiro a sair. Push e pop.';

function simular(mudancas: Record<string, unknown> = {}) {
  return simularApi({
    'GET /api/eu': { corpo: ANA },
    'GET /api/trechos/31': {
      corpo: {
        material_id: 7,
        aula_numero: 5,
        aula_titulo: 'Pilhas',
        pagina: 3,
        texto_da_pagina: PAGINA,
        inicio: 30,
        fim: 68,
        atualizado: false,
        ...mudancas,
      },
    },
  });
}

describe('página citada com o trecho destacado (MAT-T32)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mostra a página com o trecho destacado e o link para o PDF na mesma página', async () => {
    simular();
    const { container } = renderizarApp('/trechos/31');

    expect(await screen.findByRole('heading', { name: 'Aula 5: Pilhas' })).toBeInTheDocument();
    expect(container.querySelector('mark')).toHaveTextContent(
      'O último inserido é o primeiro a sair.',
    );
    expect(screen.getByRole('article', { name: 'Texto da página 3' })).toHaveTextContent(
      'Uma pilha segue a ordem LIFO.',
    );
    expect(screen.getByRole('link', { name: /Abrir o PDF nesta página/ })).toHaveAttribute(
      'href',
      '/api/materiais/7/arquivo?pagina=3#page=3',
    );
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('avisa quando o material foi atualizado depois da citação', async () => {
    simular({ atualizado: true });
    renderizarApp('/trechos/31');

    expect(await screen.findByText(/publicou uma versão nova deste material/)).toBeInTheDocument();
  });
});
