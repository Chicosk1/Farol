import { fireEvent, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { CARLOS, DISCIPLINAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const ESTRUTURAS = DISCIPLINAS.find((d) => d.nome === 'Estruturas de Dados')!;
const URL_DA_CONFIGURACAO = `/api/disciplinas/${ESTRUTURAS.id}/tutor/configuracao`;
const PADRAO = { modo_pistas: true, limite_diario: 40, politica: '' };

function simular(salvar = { status: 200, corpo: PADRAO as unknown }) {
  return simularApi({
    'GET /api/eu': { corpo: CARLOS },
    'GET /api/disciplinas': { corpo: DISCIPLINAS },
    [`GET ${URL_DA_CONFIGURACAO}`]: { corpo: PADRAO },
    [`PATCH ${URL_DA_CONFIGURACAO}`]: (chamada) =>
      salvar.status === 200 ? { corpo: { ...PADRAO, ...(chamada.corpo as object) } } : salvar,
    [`GET /api/disciplinas/${ESTRUTURAS.id}/janelas-prova`]: { corpo: [] },
  });
}

describe('configuração do tutor pelo professor (TUT-T43)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mostra a configuração atual: modo pistas ligado, limite 40 e sem política', async () => {
    simular();
    const { container } = renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor/configuracao`);

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Disciplina' }),
    ).toBeInTheDocument();
    expect(await screen.findByRole('checkbox', { name: /Modo pistas/ })).toBeChecked();
    expect(screen.getByRole('combobox', { name: 'Limite de perguntas por dia' })).toHaveValue('40');
    expect(screen.getByRole('textbox', { name: 'Política de uso de IA' })).toHaveValue('');
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('o professor desliga o modo pistas, muda o limite e escreve a política', async () => {
    const { chamadas } = simular();
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor/configuracao`);

    fireEvent.click(await screen.findByRole('checkbox', { name: /Modo pistas/ }));
    fireEvent.change(screen.getByRole('combobox', { name: 'Limite de perguntas por dia' }), {
      target: { value: '60' },
    });
    fireEvent.change(screen.getByRole('textbox', { name: 'Política de uso de IA' }), {
      target: { value: 'Use o tutor para estudar, não para copiar.' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Salvar configuração' }));

    expect(await screen.findByText('Configuração salva.')).toBeInTheDocument();
    expect(chamadas.find((c) => c.metodo === 'PATCH')?.corpo).toEqual({
      modo_pistas: false,
      limite_diario: 60,
      politica: 'Use o tutor para estudar, não para copiar.',
      resumo_semanal: true,
    });
  });

  it('avisa quando não consegue salvar', async () => {
    simular({ status: 400, corpo: { limite_diario: ['Escolha válida.'] } });
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor/configuracao`);

    fireEvent.click(await screen.findByRole('button', { name: 'Salvar configuração' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível salvar a configuração. Tente de novo.',
    );
  });

  it('a lista de disciplinas do professor leva à configuração do tutor', async () => {
    simular();
    const { roteador } = renderizarApp('/disciplinas');

    fireEvent.click(
      await screen.findByRole('link', { name: 'Configurar o tutor de Estruturas de Dados' }),
    );

    await waitFor(() =>
      expect(roteador.state.location.pathname).toBe(
        `/disciplinas/${ESTRUTURAS.id}/tutor/configuracao`,
      ),
    );
  });
});
