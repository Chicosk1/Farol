/* Professor: rascunhos de questões gerados pela IA. Nada chega ao aluno sem aprovação. */
/* Specs: QUE-RF-01, QUE-RF-02, QUE-RF-05, QUE-RF-06. Rastreabilidade em docs/rastreabilidade.md. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  const ui = { filter: 'pendente', editing: null, generating: false };

  F.questoesFilter = (filter) => { ui.filter = filter; };

  /* Simula a geração: pega questões do banco de exemplo que ainda não estão na lista. */
  F.generateDrafts = (materialIds, count) => {
    const s = F.store.state;
    const existing = new Set(s.drafts.map((q) => q.pergunta));
    const pools = materialIds.map((id) => (F.data.bancoGeracao[id] || []).filter((q) => !existing.has(q.pergunta)).map((q) => Object.assign({ material: id }, q)));
    const picked = [];
    let round = 0;
    while (picked.length < count && pools.some((pool) => pool.length > round)) {
      pools.forEach((pool) => { if (pool[round] && picked.length < count) picked.push(pool[round]); });
      round += 1;
    }
    F.store.update((st) => {
      picked.forEach((q, i) => st.drafts.unshift(Object.assign({}, q, { id: `g${Date.now()}${i}`, status: 'pendente', nova: true })));
    }, { render: false });
    return picked.length;
  };

  function draftCard(q) {
    const m = F.data.materialById(q.material);
    const editing = ui.editing === q.id;
    const options = q.opcoes
      .map((text, i) => `<li class="draft-option ${i === q.correta ? 'is-correct' : ''}"><span class="fr-option-key">${'ABCD'[i]}</span><span>${F.esc(text)}</span>${i === q.correta ? `<span class="fr-badge fr-badge--success">${F.icon('check')}Correta</span>` : ''}</li>`)
      .join('');
    const statusBadge = {
      pendente: q.nova ? '<span class="fr-badge fr-badge--accent fr-badge--pill">Novo rascunho</span>' : '<span class="fr-badge fr-badge--pill">Pendente</span>',
      aprovada: `<span class="fr-badge fr-badge--success">${F.icon('circle-check')}Publicada para a turma</span>`,
      descartada: '<span class="fr-badge">Descartada</span>',
    }[q.status];

    const body = editing
      ? `<div class="stack">
          <label class="fr-field"><span class="fr-label">Enunciado</span><textarea class="fr-input textarea" id="edit-stem-${q.id}" rows="3">${F.esc(q.pergunta)}</textarea></label>
          <label class="fr-field"><span class="fr-label">Justificativa</span><textarea class="fr-input textarea" id="edit-just-${q.id}" rows="2">${F.esc(q.justificativa)}</textarea></label>
        </div>`
      : `<h3 class="fr-card-title">${F.esc(q.pergunta)}</h3>
        <ol class="draft-options">${options}</ol>
        <p class="small"><span class="strong">Justificativa:</span> ${F.esc(q.justificativa)}</p>`;

    let actions = '';
    if (editing) {
      actions = `<button type="button" class="fr-btn fr-btn--primary fr-btn--sm" data-action="draft-save" data-id="${q.id}">Salvar</button>
        <button type="button" class="fr-btn fr-btn--ghost fr-btn--sm" data-action="draft-cancel">Cancelar</button>`;
    } else if (q.status === 'pendente') {
      actions = `<button type="button" class="fr-btn fr-btn--primary fr-btn--sm" data-action="draft-status" data-status="aprovada" data-id="${q.id}">${F.icon('check')}Aprovar</button>
        <button type="button" class="fr-btn fr-btn--outline fr-btn--sm" data-action="draft-edit" data-id="${q.id}">${F.icon('pencil')}Editar</button>
        <button type="button" class="fr-btn fr-btn--ghost fr-btn--sm" data-action="draft-status" data-status="descartada" data-id="${q.id}">${F.icon('trash')}Descartar</button>`;
    } else {
      actions = `<button type="button" class="fr-btn fr-btn--ghost fr-btn--sm" data-action="draft-status" data-status="pendente" data-id="${q.id}">${F.icon('arrow-left')}Voltar para pendentes</button>`;
    }

    return `<article class="panel draft ${q.status === 'descartada' ? 'is-muted' : ''}">
      <div class="draft-head">
        <span class="small muted">Aula ${m.aula} · ${F.esc(m.titulo)}</span>
        <div class="row">${statusBadge}${F.cite(q.cite)}</div>
      </div>
      ${body}
      <div class="draft-actions">${actions}</div>
    </article>`;
  }

  F.screens['prof-questoes'] = {
    render() {
      const s = F.store.state;
      const counts = { pendente: 0, aprovada: 0, descartada: 0 };
      s.drafts.forEach((q) => { counts[q.status] += 1; });
      const tabs = [
        ['pendente', 'Pendentes'],
        ['aprovada', 'Publicadas'],
        ['descartada', 'Descartadas'],
      ]
        .map(([id, label]) => `<button type="button" class="fr-tab" role="tab" aria-selected="${ui.filter === id}" data-action="draft-filter" data-filter="${id}">${label} (${counts[id]})</button>`)
        .join('');
      const list = s.drafts.filter((q) => q.status === ui.filter);
      const materials = s.materials.filter((m) => m.disciplina === 'ed' && m.status === 'pronto');
      const options = materials.map((m) => `<option value="${m.id}" ${m.id === 'ed-a3' ? 'selected' : ''}>Aula ${m.aula} · ${F.esc(m.titulo)}</option>`).join('');
      const empty = {
        pendente: 'Nenhum rascunho pendente. Gere questões a partir de uma aula.',
        aprovada: 'Nenhuma questão publicada ainda.',
        descartada: 'Nenhuma questão descartada.',
      }[ui.filter];

      return {
        title: 'Questões',
        html: `<div class="page">
          <div class="page-head"><div><h1 class="page-title">Questões</h1><p class="page-sub">A IA gera rascunhos a partir dos seus materiais. Nada chega aos alunos sem a sua aprovação.</p></div></div>
          <form class="panel generator" id="gen-form">
            <div class="fr-field generator-aula"><label class="fr-label" for="gen-aula">Aula</label><span class="fr-select-wrap"><select id="gen-aula" class="fr-select">${options}</select></span></div>
            <div class="fr-field generator-qtd"><label class="fr-label" for="gen-qtd">Quantidade</label><span class="fr-select-wrap"><select id="gen-qtd" class="fr-select"><option>2</option><option selected>3</option><option>5</option></select></span></div>
            <button type="submit" class="fr-btn fr-btn--primary" ${ui.generating ? 'disabled' : ''}>${ui.generating ? `<span class="spin">${F.icon('loader-2')}</span>Gerando…` : `${F.icon('sparkles')}Gerar rascunhos`}</button>
          </form>
          <div class="fr-tabs" role="tablist" aria-label="Filtrar questões">${tabs}</div>
          <div class="stack" id="draft-list">${list.length ? list.map(draftCard).join('') : F.emptyState({ icon: 'list-check', title: 'Nada por aqui', text: empty })}</div>
        </div>`,
      };
    },
    mount(main) {
      const form = main.querySelector('#gen-form');
      form.addEventListener('submit', (event) => {
        event.preventDefault();
        if (ui.generating) return;
        const material = main.querySelector('#gen-aula').value;
        const qtd = Number(main.querySelector('#gen-qtd').value);
        ui.generating = true;
        F.render();
        setTimeout(() => {
          ui.generating = false;
          ui.filter = 'pendente';
          const created = F.generateDrafts([material], qtd);
          F.render();
          F.toast(created ? `${created} ${created === 1 ? 'rascunho gerado' : 'rascunhos gerados'}. Revise antes de publicar.` : 'O banco de exemplo desta aula já foi todo usado no protótipo.', 'sparkles');
        }, 1400);
      });
    },
  };

  Object.assign((F.actions = F.actions || {}), {
    'draft-filter': (el) => { ui.filter = el.dataset.filter; ui.editing = null; F.render(); },
    'draft-edit': (el) => { ui.editing = el.dataset.id; F.render(); },
    'draft-cancel': () => { ui.editing = null; F.render(); },
    'draft-save': (el) => {
      const id = el.dataset.id;
      const stem = document.getElementById(`edit-stem-${id}`).value.trim();
      const just = document.getElementById(`edit-just-${id}`).value.trim();
      if (!stem) {
        F.toast('O enunciado não pode ficar vazio.', 'alert-triangle');
        return;
      }
      ui.editing = null;
      F.store.update((s) => {
        const q = s.drafts.find((x) => x.id === id);
        q.pergunta = stem;
        q.justificativa = just || q.justificativa;
      });
      F.toast('Questão atualizada.');
    },
    'draft-status': (el) => {
      const status = el.dataset.status;
      F.store.update((s) => {
        const q = s.drafts.find((x) => x.id === el.dataset.id);
        q.status = status;
        q.nova = false;
      });
      const messages = { aprovada: 'Questão publicada no quiz da turma.', descartada: 'Questão descartada.', pendente: 'Questão voltou para pendentes.' };
      F.toast(messages[status], status === 'descartada' ? 'trash' : 'circle-check');
    },
  });
})();
