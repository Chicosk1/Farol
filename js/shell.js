/* Farol — moldura das telas: cabeçalho, menu lateral, barra inferior no celular e barra de demonstração. */
(function () {
  'use strict';
  const F = window.Farol;

  const NAV = {
    aluno: [
      { label: 'Início', short: 'Início', icon: 'home', href: '#/aluno/inicio', match: ['aluno-inicio'] },
      { label: 'Disciplinas', short: 'Disciplinas', icon: 'school', href: '#/aluno/disciplinas', match: ['aluno-disciplinas', 'aluno-disciplina', 'aluno-quiz'] },
      { label: 'Tutor', short: 'Tutor', icon: 'message-circle', href: '#/aluno/tutor/ed', match: ['aluno-tutor'] },
      { label: 'Revisão do dia', short: 'Revisão', icon: 'cards', href: '#/aluno/revisao', match: ['aluno-revisao'] },
    ],
    professor: [
      { label: 'Radar da turma', short: 'Radar', icon: 'radar', href: '#/professor/radar', match: ['prof-radar'] },
      { label: 'Materiais', short: 'Materiais', icon: 'files', href: '#/professor/materiais', match: ['prof-materiais'] },
      { label: 'Questões', short: 'Questões', icon: 'list-check', href: '#/professor/questoes', match: ['prof-questoes'] },
      { label: 'Disciplina', short: 'Disciplina', icon: 'settings', href: '#/professor/disciplina', match: ['prof-disciplina'] },
    ],
  };

  let openPopover = null;

  function notifications(role) {
    const state = F.store.state;
    if (role === 'aluno') return F.data.novidadesAluno;
    const list = [];
    const fresh = state.doubts.filter((d) => d.nova && d.status === 'aberta').length;
    if (fresh) list.push({ icone: 'message-question', texto: `${fresh} ${fresh === 1 ? 'dúvida nova enviada' : 'dúvidas novas enviadas'} pelo tutor, sem identificação.`, quando: 'agora' });
    const ready = state.materials.find((m) => m.id === 'ed-a7' && m.status === 'pronto');
    if (ready) list.push({ icone: 'circle-check', texto: 'Aula 7, Árvores AVL, está pronta para o tutor.', quando: 'hoje' });
    list.push({ icone: 'mail', texto: 'Resumo semanal da turma SINF2NA enviado para o seu e-mail.', quando: 'segunda, 07h00' });
    const pending = state.drafts.filter((q) => q.status === 'pendente').length;
    if (pending) list.push({ icone: 'list-check', texto: `${pending} ${pending === 1 ? 'rascunho de questão aguarda' : 'rascunhos de questões aguardam'} sua revisão.`, quando: 'agora' });
    return list;
  }

  function popoverHtml(role) {
    if (openPopover === 'bell') {
      const items = notifications(role)
        .map((n) => `<li class="popover-item">${F.icon(n.icone)}<div><p>${F.esc(n.texto)}</p><p class="small muted">${F.esc(n.quando)}</p></div></li>`)
        .join('');
      return `<div class="popover" role="dialog" aria-label="Notificações"><p class="popover-title">Notificações</p><ul class="popover-list">${items}</ul></div>`;
    }
    if (openPopover === 'conta') {
      const p = F.data.pessoas[role];
      return `<div class="popover popover--small" role="dialog" aria-label="Sua conta">
        <div class="popover-account"><span class="fr-avatar fr-avatar--lg" aria-hidden="true">${p.iniciais}</span><div><p class="strong">${F.esc(p.nome)}</p><p class="small muted">${F.esc(p.descricao)}</p></div></div>
        <button type="button" class="popover-action" data-action="switch-profile">${F.icon('logout')}Trocar de perfil</button>
      </div>`;
    }
    return '';
  }

  function header(route) {
    const role = F.store.state.role;
    const p = F.data.pessoas[role];
    const hasNews = role === 'aluno' || F.store.state.doubts.some((d) => d.nova && d.status === 'aberta');
    const collapsed = F.store.state.sidebarCollapsed;
    return `<header class="fr-header">
      <button type="button" class="fr-icon-btn hide-mobile" data-action="toggle-sidebar" aria-label="${collapsed ? 'Abrir menu' : 'Recolher menu'}" aria-expanded="${!collapsed}">${F.icon('menu-2')}</button>
      <a class="fr-wordmark brand-link" href="${F.home(role)}"><b>Farol</b><span>${role === 'aluno' ? 'Tutor de estudos' : 'Painel do professor'}</span></a>
      <div class="fr-header-spacer"></div>
      <button type="button" class="fr-icon-btn" data-action="toggle-popover" data-popover="bell" aria-label="Notificações" aria-expanded="${openPopover === 'bell'}">${F.icon('bell')}${hasNews ? '<span class="fr-dot"></span>' : ''}</button>
      <button type="button" class="avatar-btn" data-action="toggle-popover" data-popover="conta" aria-label="Conta de ${F.esc(p.nome)}" aria-expanded="${openPopover === 'conta'}"><span class="fr-avatar" aria-hidden="true">${p.iniciais}</span></button>
      ${popoverHtml(role)}
    </header>`;
  }

  function sidebar(route) {
    const role = F.store.state.role;
    const band =
      role === 'aluno'
        ? `<a class="fr-sidebar-search" href="#/aluno/disciplinas">${F.icon('search')}Buscar disciplina</a>`
        : `<div class="sidebar-context"><span class="small">Turma</span><b>Estruturas de Dados · SINF2NA</b></div>`;
    const items = NAV[role]
      .map((item) => `<a class="fr-nav-item" href="${item.href}" ${item.match.includes(route.name) ? 'aria-current="page"' : ''}>${F.icon(item.icon)}${item.label}</a>`)
      .join('');
    return `<nav class="fr-sidebar" aria-label="Menu principal">
      <div class="fr-sidebar-band">${band}</div>
      <div class="fr-nav">${items}</div>
      <p class="sidebar-foot">Protótipo com dados fictícios</p>
    </nav>`;
  }

  function tabbar(route) {
    const role = F.store.state.role;
    const items = NAV[role]
      .map((item) => `<a href="${item.href}" ${item.match.includes(route.name) ? 'aria-current="page"' : ''}>${F.icon(item.icon)}<span>${item.short}</span></a>`)
      .join('');
    return `<nav class="tabbar" aria-label="Menu principal">${items}</nav>`;
  }

  function render(route, content) {
    return `${header(route)}${sidebar(route)}<main class="app-main" id="conteudo">${content}</main>${tabbar(route)}`;
  }

  function renderDemoBar(route) {
    const state = F.store.state;
    const host = document.getElementById('demo-bar-host');
    const open = state.demoOpen;
    const role = state.role;
    host.innerHTML = `<div class="demo-bar ${open ? '' : 'is-collapsed'}" role="region" aria-label="Controles da demonstração">
      <button type="button" class="demo-btn" data-demo="toggle" aria-expanded="${open}" aria-label="${open ? 'Esconder' : 'Mostrar'} controles da demonstração" title="Controles da demonstração">${F.icon(open ? 'x' : 'presentation')}</button>
      ${
        open
          ? `<span class="demo-label">Demonstração</span>
      <div class="demo-seg" role="group" aria-label="Ver como">
        <button type="button" data-demo="role" data-role="aluno" aria-pressed="${role === 'aluno'}">Aluna</button>
        <button type="button" data-demo="role" data-role="professor" aria-pressed="${role === 'professor'}">Professor</button>
      </div>
      ${role === 'aluno' && route.name !== 'entrar' ? `<button type="button" class="demo-btn" data-demo="frame" aria-pressed="${state.framed}" aria-label="Ver dentro de um celular" title="Ver dentro de um celular">${F.icon('device-mobile')}</button>` : ''}
      <button type="button" class="demo-btn" data-demo="theme" aria-label="${state.theme === 'dark' ? 'Usar tema claro' : 'Usar tema escuro'}" title="Trocar tema">${F.icon(state.theme === 'dark' ? 'sun' : 'moon')}</button>
      <button type="button" class="demo-btn" data-demo="reset" aria-label="Reiniciar demonstração" title="Reiniciar demonstração">${F.icon('refresh')}</button>`
          : ''
      }
    </div>`;
  }

  function onDemoClick(event) {
    const el = event.target.closest('[data-demo]');
    if (!el) return;
    const store = F.store;
    const kind = el.dataset.demo;
    if (kind === 'toggle') store.update((s) => { s.demoOpen = !s.demoOpen; });
    if (kind === 'theme') store.update((s) => { s.theme = s.theme === 'dark' ? 'light' : 'dark'; });
    if (kind === 'frame') store.update((s) => { s.framed = !s.framed; });
    if (kind === 'role') {
      const role = el.dataset.role;
      store.update((s) => { s.role = role; }, { render: false });
      F.go(F.home(role));
    }
    if (kind === 'reset') {
      F.closeModal();
      store.reset();
      F.go('#/entrar');
      F.toast('Demonstração reiniciada', 'refresh');
    }
  }

  /* Ações do cabeçalho e do menu, disparadas pelo atributo data-action. */
  Object.assign((F.actions = F.actions || {}), {
    'toggle-sidebar': () => F.store.update((s) => { s.sidebarCollapsed = !s.sidebarCollapsed; }),
    'toggle-popover': (el) => {
      openPopover = openPopover === el.dataset.popover ? null : el.dataset.popover;
      F.render();
    },
    'switch-profile': () => {
      openPopover = null;
      F.store.update((s) => { s.role = null; s.framed = false; }, { render: false });
      F.go('#/entrar');
    },
  });

  F.shell = {
    render,
    renderDemoBar,
    onDemoClick,
    hasPopover: () => openPopover !== null,
    closePopover: () => {
      if (!openPopover) return false;
      openPopover = null;
      F.render();
      return true;
    },
  };
})();
