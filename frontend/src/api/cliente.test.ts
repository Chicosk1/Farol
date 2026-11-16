import { afterEach, describe, expect, it, vi } from 'vitest';

import { ErroDaApi, obterSaude } from './cliente';

function respostaJson(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('cliente da API', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('obterSaude chama /api/saude na mesma origem e devolve o status', async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respostaJson({ status: 'ok' }));
    vi.stubGlobal('fetch', fetchFalso);

    await expect(obterSaude()).resolves.toEqual({ status: 'ok' });
    expect(fetchFalso).toHaveBeenCalledWith(
      '/api/saude',
      expect.objectContaining({ method: 'GET', credentials: 'same-origin' }),
    );
  });

  it('gera um ErroDaApi com o status e o corpo quando a resposta não é de sucesso', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(respostaJson({ detail: 'Serviço indisponível.' }, 503)),
    );

    const erro = await obterSaude().catch((motivo: unknown) => motivo);

    expect(erro).toBeInstanceOf(ErroDaApi);
    expect(erro).toMatchObject({ status: 503, corpo: { detail: 'Serviço indisponível.' } });
  });
});
