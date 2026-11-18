import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import { defineConfig } from 'vitest/config';

import { MANIFESTO, OPCOES_DO_WORKBOX } from './src/app/pwa';

// O navegador fala com uma só origem: o Vite encaminha /api para o Django (ADR 0007).
// No Docker Compose, o alvo é o serviço backend; fora dele, o Django na porta 8000.
const alvoDaApi = process.env.FAROL_API_ALVO ?? 'http://localhost:8000';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    // PWA (ACE-RF-11): manifesto e service worker gerados no build; a versão nova entra sozinha.
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icone.svg'],
      manifest: MANIFESTO,
      workbox: OPCOES_DO_WORKBOX,
    }),
  ],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    proxy: {
      // changeOrigin desligado: o Django vê o mesmo endereço que o navegador, e a proteção CSRF confere a origem.
      '/api': { target: alvoDaApi, changeOrigin: false },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/testes/configuracao.ts'],
    css: false,
  },
});
