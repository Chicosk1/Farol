import './estilos/global.css';

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { App } from './app/App';
import { aplicarTema } from './estilos/tema';

aplicarTema();

const raiz = document.getElementById('raiz');
if (!raiz) {
  throw new Error('O elemento #raiz não existe no index.html.');
}

createRoot(raiz).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
