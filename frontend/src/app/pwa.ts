/**
 * O Farol instalável na tela inicial do celular (ACE-RF-11). O manifesto e as regras do service worker
 * ficam aqui, fora do vite.config.ts, para serem testados.
 */

import type { ManifestOptions } from 'vite-plugin-pwa';

export const MANIFESTO = {
  name: 'Farol',
  short_name: 'Farol',
  description: 'Tutor de estudos com IA da UNIMATER, só com o material das suas disciplinas.',
  lang: 'pt-BR',
  start_url: '/',
  scope: '/',
  display: 'standalone',
  orientation: 'portrait',
  background_color: '#203a6e',
  theme_color: '#203a6e',
  icons: [
    { src: '/icone-192.png', sizes: '192x192', type: 'image/png' },
    { src: '/icone-512.png', sizes: '512x512', type: 'image/png' },
    { src: '/icone-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
  ],
} satisfies Partial<ManifestOptions>;

/**
 * O service worker guarda só a casca do site (HTML, JS, CSS, fontes e ícones). Nada da API entra
 * no cache: conversas, materiais e notas são da pessoa e mudam o tempo todo.
 */
export const OPCOES_DO_WORKBOX = {
  globPatterns: ['**/*.{js,css,html,svg,png,woff,woff2}'],
  navigateFallback: '/index.html',
  navigateFallbackDenylist: [/^\/api\//, /^\/admin\//, /^\/static\//, /^\/media\//, /^\/contas\//],
  runtimeCaching: [],
};
