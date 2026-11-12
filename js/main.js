/* Farol — rotas, desenho das telas e eventos globais. As rotas usam o hash da URL (#/aluno/inicio),
   então o protótipo funciona abrindo o index.html direto no navegador, sem servidor. */
(function () {
  'use strict';
  const F = window.Farol;

  const ROUTES = [
    ['entrar', /^\/entrar$/],
    ['aluno-inicio', /^\/aluno\/inicio$/],
    ['aluno-disciplinas', /^\/aluno\/disciplinas$/],
    ['aluno-disciplina', /^\/aluno\/disciplina\/([\w-]+)$/, ['id']],
    ['aluno-tutor', /^\/aluno\/tutor(?:\/([\w-]+))?$/, ['id']],
    ['aluno-revisao', /^\/aluno\/revisao$/],
    ['aluno-quiz', /^\/aluno\/quiz\/([\w-]+)$/, ['id']],
    ['prof-radar', /^\/professor\/radar$/],
    ['prof-materiais', /^\/professor\/materiais$/],
    ['prof-questoes', /^\/professor\/questoes$/],
    ['prof-disciplina', /^\/professor\/disciplina$/],
  ];

  F.home = (role) => (role === 'professor' ? '#/professor/radar' : '#/aluno/inicio');

  F.go = (hash) => {
    if (location.hash === hash) F.render();
    else location.hash = hash;
  };

  function parseRoute() {
    const path = location.hash.replace(/^#/, '') || '/';
    for (const [name, pattern, keys = []] of ROUTES) {
      const match = path.match(pattern);
      if (match) {
        const params = {};
        keys.forEach((key, i) => { params[key] = match[i + 1]; });
        return { name, params, path };
      }
    }
    return null;
  }

  function isMobileLayout(state, route) {
    if (route.name === 'entrar') return false;
    return (state.framed && state.role === 'aluno') || window.innerWidth < 768;
  }

  let lastPath = null;
  let lastMobile = null;

  F.render = function render() {
    const state = F.store.state;
    document.documentElement.dataset.theme = state.theme;

    const route = parseRoute();
    if (!route) return F.go(state.role ? F.home(state.role) : '#/entrar');
    if (route.name !== 'entrar') {
      if (!state.role) return F.go('#/entrar');
      const routeRole = route.name.startsWith('prof') ? 'professor' : 'aluno';
      if (routeRole !== state.role) return F.go(F.home(state.role));
    }

    const screen = F.screens[route.name];
    const app = document.getElementById('app');
    const mobile = isMobileLayout(state, route);
    const routeChanged = route.path !== lastPath;
    const previousMain = app.querySelector('.app-main');
    const keepScroll = !routeChanged && previousMain ? previousMain.scrollTop : 0;

    if (routeChanged) F.closeModal();
    const view = screen.render(route.params, { mobile });
    document.title = `${view.title} · Farol`;
    document.body.classList.toggle('is-framed', state.framed && state.role === 'aluno' && route.name !== 'entrar');

    if (route.name === 'entrar') {
      app.dataset.layout = 'bare';
      app.innerHTML = view.html;
    } else {
      app.dataset.layout = mobile ? 'mobile' : 'desktop';
      app.dataset.sidebar = state.sidebarCollapsed ? 'collapsed' : 'open';
      app.innerHTML = F.shell.render(route, view.html);
    }

    const main = app.querySelector('.app-main') || app;
    main.scrollTop = keepScroll;
    if (screen.mount) screen.mount(main, route.params, { mobile });
    F.shell.renderDemoBar(route);

    if (routeChanged && lastPath !== null) {
      const heading = main.querySelector('h1');
      if (heading) {
        heading.setAttribute('tabindex', '-1');
        heading.focus({ preventScroll: true });
      }
    }
    lastPath = route.path;
    lastMobile = mobile;
  };

  /* Cliques em qualquer elemento com data-action chamam a função de mesmo nome em F.actions. */
  document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-action]');
    if (F.shell.hasPopover() && !event.target.closest('.popover') && !(target && target.dataset.action === 'toggle-popover')) {
      F.shell.closePopover();
      if (!target) return;
    }
    if (target && F.actions[target.dataset.action]) {
      event.preventDefault();
      F.actions[target.dataset.action](target, event);
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') F.shell.closePopover();
  });

  let resizeTimer = null;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      const route = parseRoute();
      if (route && isMobileLayout(F.store.state, route) !== lastMobile) F.render();
    }, 150);
  });

  window.addEventListener('hashchange', F.render);
  document.getElementById('demo-bar-host').addEventListener('click', F.shell.onDemoClick);

  F.actions['open-cite'] = (el) => F.openCitation(el.dataset.cite);
  F.actions['open-material'] = (el) => F.openMaterial(el.dataset.material);

  F.render();
})();
