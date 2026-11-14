/* Farol — estado do protótipo, salvo no navegador (localStorage) para sobreviver a recarregamentos.
   "Reiniciar demonstração" na barra de demonstração volta tudo ao estado inicial. */
/* Specs: TUT-RF-12. Rastreabilidade em docs/rastreabilidade.md. */
(function () {
  'use strict';
  const F = window.Farol;
  const KEY = 'farol-prototipo-v1';
  const clone = (value) => JSON.parse(JSON.stringify(value));

  function initialState() {
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return {
      role: null,
      theme: prefersDark ? 'dark' : 'light',
      framed: false,
      demoOpen: window.innerWidth >= 768,
      sidebarCollapsed: false,
      favorites: ['ed', 'bd1'],
      chats: {},
      questionsToday: 12,
      extraQuestions: 0,
      doubts: clone(F.data.duvidasIniciais),
      drafts: clone(F.data.rascunhos),
      materials: clone(F.data.materiais),
      settings: clone(F.data.configuracaoInicial),
      practice: null,
      reviewDone: null,
      radarWeek: 's17',
    };
  }

  function load() {
    const base = initialState();
    try {
      const saved = JSON.parse(localStorage.getItem(KEY) || 'null');
      return saved ? Object.assign(base, saved) : base;
    } catch (error) {
      return base;
    }
  }

  const store = {
    state: load(),
    save() {
      try {
        localStorage.setItem(KEY, JSON.stringify(store.state));
      } catch (error) {
        /* Sem armazenamento (modo privado, por exemplo): o protótipo segue funcionando só na memória. */
      }
    },
    /* Altera o estado, salva e redesenha a tela. Use { render: false } para mudanças feitas direto no DOM. */
    update(change, { render = true } = {}) {
      change(store.state);
      store.save();
      if (render) F.render();
    },
    reset() {
      const keep = { theme: store.state.theme, demoOpen: store.state.demoOpen };
      store.state = Object.assign(initialState(), keep);
      store.save();
    },
  };

  F.store = store;
})();
