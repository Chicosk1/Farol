import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ANA, simularApi } from '../testes/api';
import {
  ErroDaApi,
  entrarEmDesenvolvimento,
  obterEu,
  obterSaude,
  sair,
  trocarPerfilAtivo,
} from './cliente';

describe('cliente da API', () => {
  beforeEach(() => {
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('obterSaude chama /api/saude na mesma origem e devolve o status', async () => {
    const { fetchFalso } = simularApi({ 'GET /api/saude': { corpo: { status: 'ok' } } });

    await expect(obterSaude()).resolves.toEqual({ status: 'ok' });
    expect(fetchFalso).toHaveBeenCalledWith(
      '/api/saude',
      expect.objectContaining({ method: 'GET', credentials: 'same-origin' }),
    );
  });

  it('gera um ErroDaApi com o status e o corpo quando a resposta não é de sucesso', async () => {
    simularApi({ 'GET /api/saude': { status: 503, corpo: { detail: 'Serviço indisponível.' } } });

    const erro = await obterSaude().catch((motivo: unknown) => motivo);

    expect(erro).toBeInstanceOf(ErroDaApi);
    expect(erro).toMatchObject({ status: 503, corpo: { detail: 'Serviço indisponível.' } });
  });

  describe('sessão', () => {
    it('obterEu devolve a pessoa logada', async () => {
      simularApi({ 'GET /api/eu': { corpo: ANA } });

      await expect(obterEu()).resolves.toEqual(ANA);
    });

    it('obterEu devolve null quando ninguém entrou (401)', async () => {
      simularApi({
        'GET /api/eu': { status: 401, corpo: { detail: 'Credenciais não foram fornecidas.' } },
      });

      await expect(obterEu()).resolves.toBeNull();
    });

    it('obterEu continua falhando nos outros erros', async () => {
      simularApi({ 'GET /api/eu': { status: 500 } });

      await expect(obterEu()).rejects.toBeInstanceOf(ErroDaApi);
    });

    it('entrarEmDesenvolvimento envia o e-mail em JSON e devolve a pessoa', async () => {
      const { chamadas } = simularApi({ 'POST /api/dev/entrar': { corpo: ANA } });

      await expect(entrarEmDesenvolvimento(ANA.email)).resolves.toEqual(ANA);
      expect(chamadas[0]).toMatchObject({
        metodo: 'POST',
        corpo: { email: ANA.email },
        cabecalhos: { 'content-type': 'application/json' },
      });
    });

    it('trocarPerfilAtivo envia o perfil escolhido', async () => {
      const { chamadas } = simularApi({
        'POST /api/eu/perfil-ativo': { corpo: { ...ANA, perfil_ativo: 'aluno' } },
      });

      await trocarPerfilAtivo('aluno');

      expect(chamadas[0]?.corpo).toEqual({ perfil: 'aluno' });
    });

    it('sair chama /api/sair e aceita a resposta sem corpo (204)', async () => {
      const { chamadas } = simularApi({ 'POST /api/sair': { status: 204 } });

      await expect(sair()).resolves.toBeUndefined();
      expect(chamadas[0]?.metodo).toBe('POST');
    });
  });

  describe('token CSRF', () => {
    it('chamadas que mudam dados levam o token do cookie no cabeçalho X-CSRFToken', async () => {
      document.cookie = 'csrftoken=token-de-teste';
      const { chamadas } = simularApi({ 'POST /api/sair': { status: 204 } });

      await sair();

      expect(chamadas[0]?.cabecalhos['x-csrftoken']).toBe('token-de-teste');
    });

    it('leituras não levam o token', async () => {
      document.cookie = 'csrftoken=token-de-teste';
      const { chamadas } = simularApi({ 'GET /api/eu': { corpo: ANA } });

      await obterEu();

      expect(chamadas[0]?.cabecalhos['x-csrftoken']).toBeUndefined();
    });

    it('sem cookie, a chamada segue sem o cabeçalho', async () => {
      const { chamadas } = simularApi({ 'POST /api/sair': { status: 204 } });

      await sair();

      expect(chamadas[0]?.cabecalhos['x-csrftoken']).toBeUndefined();
    });
  });
});
