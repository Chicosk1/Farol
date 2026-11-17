import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { CARLOS, DISCIPLINAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const ESTRUTURAS = DISCIPLINAS.find((d) => d.nome === 'Estruturas de Dados')!;
const URL_DOS_MATERIAIS = `/api/disciplinas/${ESTRUTURAS.id}/materiais`;
const PAGINA = `/disciplinas/${ESTRUTURAS.id}/materiais`;

function material(mudancas: Record<string, unknown> = {}) {
  return {
    id: 7,
    aula_numero: 4,
    aula_titulo: 'Listas encadeadas',
    paginas: 12,
    status: 'pronto',
    status_rotulo: 'Pronto para o tutor',
    etapa: 'pronto',
    etapa_rotulo: 'Pronto para o tutor',
    erro: '',
    paginas_sem_texto: [],
    versao: 1,
    criado_em: '2026-11-10T10:00:00-03:00',
    ...mudancas,
  };
}

function simular(listas: unknown[][], extras: Parameters<typeof simularApi>[0] = {}) {
  let vez = 0;
  return simularApi({
    'GET /api/eu': { corpo: CARLOS },
    'GET /api/disciplinas': { corpo: DISCIPLINAS },
    [`GET ${URL_DOS_MATERIAIS}`]: () => ({ corpo: listas[Math.min(vez++, listas.length - 1)] }),
    ...extras,
  });
}

function pdf(nome = 'aula-5.pdf', tipo = 'application/pdf') {
  return new File(['%PDF-1.7'], nome, { type: tipo });
}

describe('materiais da disciplina para o professor (MAT-T24)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it('lista os materiais com o status de cada um', async () => {
    simular([
      [
        material(),
        material({
          id: 8,
          aula_numero: 5,
          aula_titulo: 'Pilhas',
          status: 'atencao',
          status_rotulo: 'Precisa de atenção',
          paginas_sem_texto: [1, 2, 3],
        }),
      ],
    ]);
    const { container } = renderizarApp(PAGINA);

    const lista = await screen.findByRole('list', { name: 'Materiais da disciplina' });
    const itens = within(lista).getAllByRole('listitem');
    expect(itens[0]).toHaveTextContent('Aula 4: Listas encadeadas');
    expect(itens[0]).toHaveTextContent('Pronto para o tutor');
    expect(itens[1]).toHaveTextContent('Precisa de atenção');
    expect(itens[1]).toHaveTextContent('Páginas sem texto: 1, 2, 3');
    expect(
      screen.getByRole('heading', { name: 'Materiais de Estruturas de Dados' }),
    ).toBeInTheDocument();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('envia o PDF com a aula e acompanha as etapas até ficar pronto', async () => {
    const processando = (etapa: string, rotulo: string) =>
      material({
        id: 9,
        aula_numero: 5,
        aula_titulo: 'Pilhas',
        status: 'processando',
        status_rotulo: 'Processando',
        etapa,
        etapa_rotulo: rotulo,
      });
    const { chamadas } = simular(
      [
        [],
        [processando('lendo', 'Lendo as páginas')],
        [material({ id: 9, aula_numero: 5, aula_titulo: 'Pilhas' })],
      ],
      {
        [`POST ${URL_DOS_MATERIAIS}`]: {
          status: 202,
          corpo: { material_id: 9, status: 'processando' },
        },
      },
    );
    renderizarApp(PAGINA);

    fireEvent.change(await screen.findByLabelText('Arquivo PDF da aula'), {
      target: { files: [pdf()] },
    });
    fireEvent.change(screen.getByLabelText('Número da aula'), { target: { value: '5' } });
    fireEvent.change(screen.getByLabelText('Título da aula'), { target: { value: 'Pilhas' } });
    fireEvent.click(screen.getByRole('button', { name: 'Enviar PDF' }));

    expect(await screen.findByText('Lendo as páginas')).toBeInTheDocument();
    const envio = chamadas.find((c) => c.metodo === 'POST');
    expect(envio?.formulario).toEqual({
      arquivo: 'aula-5.pdf',
      aula_numero: '5',
      aula_titulo: 'Pilhas',
    });
    expect(
      await screen.findByText('Pronto para o tutor', {}, { timeout: 4000 }),
    ).toBeInTheDocument();
  });

  it('recusa o arquivo que não é PDF, sem enviar nada', async () => {
    const { chamadas } = simular([[]]);
    renderizarApp(PAGINA);

    fireEvent.change(await screen.findByLabelText('Arquivo PDF da aula'), {
      target: { files: [pdf('slides.pptx', 'application/vnd.ms-powerpoint')] },
    });
    fireEvent.change(screen.getByLabelText('Número da aula'), { target: { value: '5' } });
    fireEvent.change(screen.getByLabelText('Título da aula'), { target: { value: 'Pilhas' } });
    fireEvent.click(screen.getByRole('button', { name: 'Enviar PDF' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Envie um arquivo PDF. Slides podem ser exportados como PDF.',
    );
    expect(chamadas.some((c) => c.metodo === 'POST')).toBe(false);
  });

  it('aceita o PDF arrastado para a área de envio', async () => {
    simular([[]]);
    renderizarApp(PAGINA);

    const area = await screen.findByTestId('area-de-envio');
    fireEvent.drop(area, { dataTransfer: { files: [pdf('arrastado.pdf')] } });

    expect(await screen.findByText('Arquivo escolhido: arrastado.pdf')).toBeInTheDocument();
  });

  it('mostra a recusa do servidor, como o PDF grande demais', async () => {
    simular([[]], {
      [`POST ${URL_DOS_MATERIAIS}`]: {
        status: 400,
        corpo: { arquivo: ['O PDF passa de 50 MB. Divida o arquivo e envie as partes.'] },
      },
    });
    renderizarApp(PAGINA);

    fireEvent.change(await screen.findByLabelText('Arquivo PDF da aula'), {
      target: { files: [pdf()] },
    });
    fireEvent.change(screen.getByLabelText('Número da aula'), { target: { value: '5' } });
    fireEvent.change(screen.getByLabelText('Título da aula'), { target: { value: 'Pilhas' } });
    fireEvent.click(screen.getByRole('button', { name: 'Enviar PDF' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('O PDF passa de 50 MB.');
  });

  it('retira um material da lista', async () => {
    const { chamadas } = simular([[material()], []], {
      'DELETE /api/materiais/7': { status: 204 },
    });
    renderizarApp(PAGINA);

    fireEvent.click(await screen.findByRole('button', { name: 'Retirar a aula 4' }));

    await waitFor(() => expect(screen.getByText('Nenhum material enviado ainda.')).toBeVisible());
    expect(chamadas.some((c) => c.metodo === 'DELETE')).toBe(true);
  });

  it('a lista de disciplinas do professor leva aos materiais', async () => {
    simular([[]]);
    const { roteador } = renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('link', { name: 'Materiais de Estruturas de Dados' }));

    await waitFor(() => expect(roteador.state.location.pathname).toBe(PAGINA));
  });

  it('envia a nova versão de um material e mostra a versão nova processando (MAT-T52)', async () => {
    const { chamadas } = simular(
      [
        [material()],
        [
          material({ status: 'substituido', status_rotulo: 'Substituído pela versão nova' }),
          material({
            id: 9,
            versao: 2,
            status: 'processando',
            status_rotulo: 'Processando',
            etapa: 'lendo',
            etapa_rotulo: 'Lendo as páginas',
          }),
        ],
      ],
      {
        'POST /api/materiais/7/versoes': {
          status: 202,
          corpo: { material_id: 9, status: 'processando' },
        },
      },
    );
    renderizarApp(PAGINA);

    fireEvent.change(await screen.findByLabelText('Enviar nova versão da aula 4'), {
      target: { files: [pdf('aula-4-corrigida.pdf')] },
    });

    expect(await screen.findByText('versão 2')).toBeInTheDocument();
    expect(screen.getByText('Substituído pela versão nova')).toBeInTheDocument();
    expect(chamadas.find((c) => c.caminho === '/api/materiais/7/versoes')?.formulario).toEqual({
      arquivo: 'aula-4-corrigida.pdf',
    });
    // Só a versão em uso oferece nova versão e retirada.
    expect(screen.getAllByRole('button', { name: /Retirar a aula 4/ })).toHaveLength(1);
  });
});
