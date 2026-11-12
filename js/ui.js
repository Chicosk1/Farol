/* Farol — utilitários de interface: escape de HTML, ícones, toasts, modais e pedaços de marcação reaproveitados. */
(function () {
  'use strict';
  const F = (window.Farol = window.Farol || {});

  const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  F.esc = (value) => String(value == null ? '' : value).replace(/[&<>"']/g, (c) => ESCAPES[c]);

  F.icon = (name) => {
    const paths = F.iconPaths && F.iconPaths[name];
    if (!paths) return '';
    return `<i class="fr-ico" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${paths}</svg></i>`;
  };

  /* Normaliza texto para comparação: minúsculas, sem acentos e sem pontuação. */
  F.normalize = (text) =>
    String(text || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9()+\-\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();

  F.todayLabel = () => {
    const text = new Intl.DateTimeFormat('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date());
    return text.charAt(0).toUpperCase() + text.slice(1);
  };

  F.nowLabel = () => {
    const time = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' }).format(new Date());
    return `hoje, ${time.replace(':', 'h')}`;
  };

  /* ---------- Marcação reaproveitada ---------- */

  F.progress = ({ value, max = 100, label, ariaLabel }) => {
    const pct = Math.max(0, Math.min(100, Math.round((value / max) * 100)));
    return `<div class="fr-progress">
      <div class="fr-progress-track" role="progressbar" aria-valuenow="${value}" aria-valuemin="0" aria-valuemax="${max}" aria-label="${F.esc(ariaLabel || label)}">
        <div class="fr-progress-fill" style="width:${pct}%"></div>
      </div>
      <span class="fr-progress-label">${F.esc(label)}</span>
    </div>`;
  };

  F.cite = (citeId, extraClass = '') => {
    const c = F.data.citations[citeId];
    if (!c) return '';
    return `<button type="button" class="fr-cite ${extraClass}" data-action="open-cite" data-cite="${citeId}">${F.icon('file-text')}${F.esc(F.citeLabel(citeId))}</button>`;
  };

  /* "do Prof. Carlos Mendes" ou "da Prof.ª Marta Ribeiro". */
  F.ofProfessor = (d) => (d.professor.startsWith('Prof.ª') ? `da ${d.professor}` : `do ${d.professor}`);

  F.citeLabel = (citeId) => {
    const c = F.data.citations[citeId];
    const m = F.data.materialById(c.materialId);
    return `Aula ${m.aula}, p. ${c.page}`;
  };

  F.courseCard = (d, { favorite }) => {
    const badge = d.novidade
      ? `<span class="fr-badge fr-badge--accent fr-badge--pill">${F.esc(d.novidade)}</span>`
      : `<span class="fr-badge">${F.icon('tag')}Normal</span>`;
    return `<article class="fr-card is-clickable">
      <div class="fr-card-media">${F.icon(d.icone)}
        <button type="button" class="fr-card-fav ${favorite ? 'is-fav' : ''}" data-action="toggle-fav" data-id="${d.id}" aria-pressed="${favorite}" aria-label="${favorite ? 'Remover dos favoritos' : 'Favoritar'} ${F.esc(d.nome)}">${F.icon('star')}</button>
        ${badge}
      </div>
      <div class="fr-card-body">
        <h3 class="fr-card-title"><a class="card-link" href="#/aluno/disciplina/${d.id}">${F.esc(d.nome)} (${F.esc(d.codigo)})</a></h3>
        <div class="fr-meta">${F.icon('school')}${F.esc(F.data.curso.nome)}</div>
        <div class="fr-card-dates"><span>Início: ${d.inicio}</span><span>Encerra: ${d.fim}</span></div>
        <div class="fr-card-foot">
          ${F.progress({ value: d.progresso, label: `${d.progresso}% concluído`, ariaLabel: `Progresso em ${d.nome}` })}
          ${d.tutor ? `<a class="fr-icon-btn fr-icon-btn--sm" href="#/aluno/tutor/${d.id}" aria-label="Abrir o tutor de ${F.esc(d.nome)}">${F.icon('message-circle')}</a>` : ''}
        </div>
      </div>
    </article>`;
  };

  F.emptyState = ({ icon, title, text, action = '' }) => `<div class="empty-state">
    <span class="empty-state-icon">${F.icon(icon)}</span>
    <h2 class="section-title">${F.esc(title)}</h2>
    <p class="muted">${F.esc(text)}</p>
    ${action}
  </div>`;

  /* ---------- Toasts ---------- */

  F.toast = (message, icon = 'circle-check') => {
    let host = document.querySelector('.toast-host');
    if (!host) {
      host = document.createElement('div');
      host.className = 'toast-host';
      host.setAttribute('role', 'status');
      host.setAttribute('aria-live', 'polite');
      document.body.appendChild(host);
    }
    const el = document.createElement('div');
    el.className = 'toast';
    el.innerHTML = `${F.icon(icon)}<span>${F.esc(message)}</span>`;
    host.appendChild(el);
    while (host.children.length > 2) host.firstElementChild.remove();
    setTimeout(() => el.remove(), 3200);
  };

  /* ---------- Modal ---------- */

  let lastFocus = null;

  F.closeModal = () => {
    const backdrop = document.querySelector('.modal-backdrop');
    if (!backdrop) return;
    backdrop.remove();
    document.removeEventListener('keydown', onModalKey);
    if (lastFocus && document.contains(lastFocus)) lastFocus.focus();
  };

  function onModalKey(event) {
    if (event.key === 'Escape') F.closeModal();
    if (event.key === 'Tab') {
      const modal = document.querySelector('.modal');
      const focusables = modal.querySelectorAll('button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      if (!focusables.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  }

  F.openModal = ({ title, subtitle = '', body, wide = false }) => {
    F.closeModal();
    lastFocus = document.activeElement;
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.innerHTML = `<div class="modal ${wide ? 'modal--wide' : ''}" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div class="modal-head">
        <div>
          <h2 id="modal-title" class="modal-title">${F.esc(title)}</h2>
          ${subtitle ? `<p class="small muted">${F.esc(subtitle)}</p>` : ''}
        </div>
        <button type="button" class="fr-icon-btn" data-modal-close aria-label="Fechar">${F.icon('x')}</button>
      </div>
      <div class="modal-body">${body}</div>
    </div>`;
    backdrop.addEventListener('click', (event) => {
      if (event.target === backdrop || event.target.closest('[data-modal-close]')) F.closeModal();
    });
    document.getElementById('app').appendChild(backdrop);
    document.addEventListener('keydown', onModalKey);
    backdrop.querySelector('[data-modal-close]').focus();
  };

  /* Abre a página do material citada pelo tutor, com o trecho destacado. */
  F.openCitation = (citeId) => {
    const c = F.data.citations[citeId];
    if (!c) return;
    const m = F.data.materialById(c.materialId);
    const d = F.data.disciplineById(m.disciplina);
    const body = `<article class="paper" aria-label="Página ${c.page} do material">
      <p class="paper-meta">${F.esc(d.nome)} · Aula ${m.aula} · ${F.esc(m.titulo)}</p>
      <h3 class="paper-heading">${F.esc(c.heading)}</h3>
      ${c.before ? `<p>${F.esc(c.before)}</p>` : ''}
      <p><mark class="cite-mark">${F.esc(c.excerpt)}</mark></p>
      ${c.code ? `<pre class="code"><code>${F.esc(c.code)}</code></pre>` : ''}
      ${c.after ? `<p>${F.esc(c.after)}</p>` : ''}
      <p class="paper-page">${c.page} / ${m.paginas}</p>
    </article>
    <p class="small muted modal-note">${F.icon('info-circle')}Trecho destacado: a parte do material que o tutor usou na resposta.</p>`;
    F.openModal({ title: `Aula ${m.aula}, página ${c.page}`, subtitle: `${m.titulo} · PDF publicado pelo professor`, body, wide: true });
  };

  F.openMaterial = (materialId) => {
    const m = F.data.materialById(materialId);
    const firstCite = Object.keys(F.data.citations).find((id) => F.data.citations[id].materialId === materialId);
    if (firstCite) return F.openCitation(firstCite);
    const d = F.data.disciplineById(m.disciplina);
    const body = `<article class="paper">
      <p class="paper-meta">${F.esc(d.nome)} · ${F.esc(d.professor)}</p>
      <h3 class="paper-heading">Aula ${m.aula}: ${F.esc(m.titulo)}</h3>
      <p>Esta é uma página de exemplo do protótipo. No produto, aqui aparece o PDF que o professor publicou.</p>
      <p class="paper-page">1 / ${m.paginas}</p>
    </article>`;
    F.openModal({ title: `Aula ${m.aula}: ${m.titulo}`, subtitle: `${m.paginas} páginas`, body, wide: true });
  };
})();
