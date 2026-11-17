/// <reference types="node" />
import { readFileSync } from 'node:fs';

import { describe, expect, it } from 'vitest';

// Lido do disco: nos testes, o CSS importado vem vazio (css: false no vite.config.ts).
const tokens = readFileSync('src/estilos/tokens.css', 'utf-8'); // a partir da pasta frontend/

/**
 * Contraste das cores do design system Farol, nos temas claro e escuro (ACE-T90, ACE-RNF-01).
 * O jsdom não calcula estilos, então o axe não mede o contraste nas telas; este teste mede os pares
 * de texto e fundo que as telas usam, pela fórmula da WCAG 2.2 (mínimo 4,5:1 para texto).
 */

type Tema = 'light' | 'dark';

function cores(tema: Tema): Record<string, string> {
  const bloco = tokens.split(`[data-theme="${tema}"]`)[1]?.split('}')[0] ?? '';
  return Object.fromEntries(
    [...bloco.matchAll(/--([a-z-]+):\s*(#[0-9a-f]{6})/gi)].map(([, nome, valor]) => [nome, valor]),
  );
}

function luminancia(hex: string): number {
  const canais = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const [r, g, b] = canais.map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r! + 0.7152 * g! + 0.0722 * b!;
}

function contraste(frente: string, fundo: string): number {
  const [clara, escura] = [luminancia(frente), luminancia(fundo)].sort((a, b) => b - a);
  return (clara! + 0.05) / (escura! + 0.05);
}

/** Pares de texto e fundo usados nas telas (classes text-* sobre bg-*). */
const PARES: [texto: string, fundo: string][] = [
  ['ink', 'surface'],
  ['ink', 'surface-page'],
  ['ink-muted', 'surface'],
  ['ink-muted', 'surface-page'],
  ['ink', 'accent-soft'],
  ['accent', 'surface'],
  ['on-accent', 'accent'],
  ['on-chrome', 'chrome'],
  ['on-yellow', 'brand-yellow'],
  ['danger-text', 'surface'],
  ['danger-text', 'danger-soft'],
  ['success-text', 'surface'],
  ['warning-text', 'surface'],
  ['warning-text', 'warning-soft'],
];

describe.each(['light', 'dark'] as const)('contraste no tema %s (ACE-T90)', (tema) => {
  const paleta = cores(tema);

  it.each(PARES)('texto %s sobre %s tem contraste de pelo menos 4,5:1', (texto, fundo) => {
    expect(paleta[texto], texto).toBeDefined();
    expect(paleta[fundo], fundo).toBeDefined();
    expect(contraste(paleta[texto]!, paleta[fundo]!)).toBeGreaterThanOrEqual(4.5);
  });
});
