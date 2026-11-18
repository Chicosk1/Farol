import { act, fireEvent, render, screen } from '@testing-library/react';
import { useState } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../testes/acessibilidade';
import { Avatar } from './Avatar';
import { ProvedorDeAvisos } from './Avisos';
import { Botao } from './Botao';
import { classesDoBotao, iniciais } from './classes';
import { useAvisos } from './contextoDosAvisos';
import { EstadoVazio } from './EstadoVazio';
import { Icone } from './Icone';
import { ICONES } from './icones';
import { Modal } from './Modal';
import { Progresso } from './Progresso';
import { Selo } from './Selo';

describe('design system do protótipo (ACE-T70)', () => {
  afterEach(() => vi.useRealTimers());

  it('o ícone é um SVG decorativo com os traços do Tabler', () => {
    const { container } = render(<Icone nome="bell" />);

    const icone = container.querySelector('i.fr-ico');
    expect(icone).toHaveAttribute('aria-hidden', 'true');
    expect(icone?.querySelectorAll('path')).toHaveLength(ICONES.bell.length);
  });

  it('os botões usam as classes do protótipo', () => {
    render(
      <>
        <Botao>Salvar</Botao>
        <Botao variante="contorno" pequeno icone="upload">
          Enviar PDF
        </Botao>
        <Botao variante="fantasma">Ver todas</Botao>
      </>,
    );

    expect(screen.getByRole('button', { name: 'Salvar' })).toHaveClass('fr-btn', 'fr-btn--primary');
    expect(screen.getByRole('button', { name: 'Enviar PDF' })).toHaveClass(
      'fr-btn--outline',
      'fr-btn--sm',
    );
    expect(screen.getByRole('button', { name: 'Ver todas' })).toHaveClass('fr-btn--ghost');
    expect(screen.getByRole('button', { name: 'Salvar' })).toHaveAttribute('type', 'button');
    expect(classesDoBotao('contorno')).toBe('fr-btn fr-btn--outline');
  });

  it('o selo, o avatar e o estado vazio montam a marcação do protótipo', () => {
    const { container } = render(
      <>
        <Selo tom="sucesso" icone="check">
          Pronto para o tutor
        </Selo>
        <Avatar nome="Ana Clara Souza" />
        <EstadoVazio
          icone="search"
          titulo="Nenhuma disciplina encontrada"
          texto="Tente outro nome."
        />
      </>,
    );

    expect(screen.getByText('Pronto para o tutor')).toHaveClass('fr-badge', 'fr-badge--success');
    expect(container.querySelector('.fr-avatar')).toHaveTextContent('AS');
    expect(
      screen.getByRole('heading', { level: 2, name: 'Nenhuma disciplina encontrada' }),
    ).toBeInTheDocument();
    expect(iniciais('  carlos  ')).toBe('C');
  });

  it('a barra de progresso informa o valor a leitores de tela', () => {
    render(<Progresso valor={3} maximo={8} rotulo="3 de 8 cartões" />);

    const barra = screen.getByRole('progressbar', { name: '3 de 8 cartões' });
    expect(barra).toHaveAttribute('aria-valuenow', '3');
    expect(barra).toHaveAttribute('aria-valuemax', '8');
    expect(barra.firstElementChild).toHaveStyle({ width: '38%' });
  });

  it('o modal prende o foco, fecha com Esc e devolve o foco a quem abriu', () => {
    function Pagina() {
      const [aberto, setAberto] = useState(false);
      return (
        <>
          <button type="button" onClick={() => setAberto(true)}>
            Abrir
          </button>
          {aberto && (
            <Modal titulo="Política de uso de IA" aoFechar={() => setAberto(false)}>
              <button type="button">Entendi</button>
            </Modal>
          )}
        </>
      );
    }
    render(<Pagina />);
    const abrir = screen.getByRole('button', { name: 'Abrir' });
    abrir.focus();
    fireEvent.click(abrir);

    const dialogo = screen.getByRole('dialog', { name: 'Política de uso de IA' });
    expect(dialogo).toHaveAttribute('aria-modal', 'true');
    const fechar = screen.getByRole('button', { name: 'Fechar' });
    const entendi = screen.getByRole('button', { name: 'Entendi' });
    expect(fechar).toHaveFocus();

    fireEvent.keyDown(entendi, { key: 'Tab' });
    entendi.focus();
    fireEvent.keyDown(entendi, { key: 'Tab' });
    expect(fechar).toHaveFocus();
    fireEvent.keyDown(fechar, { key: 'Tab', shiftKey: true });
    expect(entendi).toHaveFocus();

    fireEvent.keyDown(entendi, { key: 'Escape' });
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(abrir).toHaveFocus();
  });

  it('o modal sem aoFechar só fecha pelo próprio conteúdo', () => {
    render(
      <Modal titulo="Aviso de privacidade">
        <button type="button">Entendi</button>
      </Modal>,
    );

    expect(screen.queryByRole('button', { name: 'Fechar' })).toBeNull();
    fireEvent.keyDown(screen.getByRole('button', { name: 'Entendi' }), { key: 'Escape' });
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('os avisos aparecem numa região anunciada e somem sozinhos', () => {
    vi.useFakeTimers();
    function Salvar() {
      const avisar = useAvisos();
      return (
        <button type="button" onClick={() => avisar('Política salva.')}>
          Salvar
        </button>
      );
    }
    render(
      <ProvedorDeAvisos>
        <Salvar />
      </ProvedorDeAvisos>,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Salvar' }));
    expect(screen.getByRole('status')).toHaveTextContent('Política salva.');

    act(() => vi.advanceTimersByTime(3300));
    expect(screen.getByRole('status')).toBeEmptyDOMElement();
  });

  it('não tem violações de acessibilidade', async () => {
    const { container } = render(
      <main>
        <h1>Componentes</h1>
        <Botao icone="send" aria-label="Enviar pergunta" />
        <Selo tom="destaque" pilula>
          Com tutor
        </Selo>
        <Progresso valor={40} rotulo="40% concluído" />
        <EstadoVazio icone="message-circle" titulo="Pergunte ao tutor" />
      </main>,
    );

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});
