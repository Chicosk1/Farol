/* Aluno: lista de disciplinas, no mesmo formato da plataforma acadêmica (busca, abas e grade ou lista). */
/* Specs: ACE-RF-10. Rastreabilidade em docs/rastreabilidade.md. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  const ui = { tab: 'todas', query: '', view: 'grade' };
  const TABS = [
    { id: 'todas', label: 'Todas' },
    { id: 'favoritas', label: 'Favoritas' },
    { id: 'tutor', label: 'Com tutor' },
  ];

  function filtered() {
    const state = F.store.state;
    const q = F.normalize(ui.query);
    return F.data.disciplinas.filter((d) => {
      if (ui.tab === 'favoritas' && !state.favorites.includes(d.id)) return false;
      if (ui.tab === 'tutor' && !d.tutor) return false;
      return !q || F.normalize(`${d.nome} ${d.professor}`).includes(q);
    });
  }

  function listRow(d) {
    return `<a class="course-row" href="#/aluno/disciplina/${d.id}">
      <span class="course-row-icon">${F.icon(d.icone)}</span>
      <span class="course-row-main"><span class="strong">${F.esc(d.nome)} (${d.codigo})</span><span class="small muted">${F.esc(d.professor)}</span></span>
      ${d.tutor ? '<span class="fr-badge fr-badge--accent fr-badge--pill">Com tutor</span>' : ''}
      <span class="course-row-progress">${F.progress({ value: d.progresso, label: `${d.progresso}% concluído`, ariaLabel: `Progresso em ${d.nome}` })}</span>
      ${F.icon('chevron-right')}
    </a>`;
  }

  function results() {
    const list = filtered();
    if (!list.length) {
      return F.emptyState({ icon: 'search', title: 'Nenhuma disciplina encontrada', text: 'Tente outro nome ou volte para a aba Todas.' });
    }
    const favorites = F.store.state.favorites;
    if (ui.view === 'lista') return `<div class="panel list-panel">${list.map(listRow).join('')}</div>`;
    return `<div class="grid-cards">${list.map((d) => F.courseCard(d, { favorite: favorites.includes(d.id) })).join('')}</div>`;
  }

  F.screens['aluno-disciplinas'] = {
    render() {
      const tabs = TABS.map((t) => `<button type="button" class="fr-tab" role="tab" aria-selected="${ui.tab === t.id}" data-action="disc-tab" data-tab="${t.id}">${t.label}</button>`).join('');
      return {
        title: 'Disciplinas',
        html: `<div class="page">
          <div class="page-head"><div><h1 class="page-title">Disciplinas</h1><p class="page-sub">${F.esc(F.data.curso.nome)} · 2026/2</p></div></div>
          <div class="toolbar">
            <div class="fr-input-wrap toolbar-search">${F.icon('search')}<input class="fr-input" type="search" id="busca-disciplina" placeholder="Buscar por disciplina ou professor" aria-label="Buscar disciplina" value="${F.esc(ui.query)}"></div>
            <div class="fr-tabs" role="tablist" aria-label="Filtrar disciplinas">${tabs}</div>
            <div class="fr-tabs fr-tabs--icon" role="group" aria-label="Modo de exibição">
              <button type="button" class="fr-tab" aria-pressed="${ui.view === 'grade'}" data-action="disc-view" data-view="grade" aria-label="Grade">${F.icon('layout-grid')}</button>
              <button type="button" class="fr-tab" aria-pressed="${ui.view === 'lista'}" data-action="disc-view" data-view="lista" aria-label="Lista">${F.icon('list')}</button>
            </div>
          </div>
          <section aria-label="Resultados" id="disc-results">${results()}</section>
        </div>`,
      };
    },
    mount(root) {
      const input = root.querySelector('#busca-disciplina');
      input.addEventListener('input', () => {
        ui.query = input.value;
        root.querySelector('#disc-results').innerHTML = results();
      });
    },
  };

  Object.assign((F.actions = F.actions || {}), {
    'disc-tab': (el) => { ui.tab = el.dataset.tab; F.render(); },
    'disc-view': (el) => { ui.view = el.dataset.view; F.render(); },
  });
})();
