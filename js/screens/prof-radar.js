/* Professor: radar da turma. Mostra tópicos com mais dúvidas, acerto por tópico, sugestão para a próxima aula
   e as dúvidas que o tutor não respondeu. Nada aqui identifica alunos. */
/* Specs: RAD-RF-02, RAD-RF-03, RAD-RF-04, RAD-RF-06, RAD-RF-07, RAD-RF-08, RAD-RF-09, RAD-RF-11, DUV-RF-05, DUV-RF-07. Rastreabilidade em docs/rastreabilidade.md. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  let expanded = null;

  function rateClass(rate) {
    if (rate < 50) return 'fr-rate--low';
    if (rate <= 70) return 'fr-rate--mid';
    return 'fr-rate--high';
  }

  /* Tópicos para retomar: muitos alunos com dúvida e acerto baixo pesam mais. */
  function suggestion(week) {
    return week.duvidas
      .map((t) => {
        const rate = (week.acertoTopicos.find((a) => a.topico === t.topico) || { taxa: 70 }).taxa;
        return { topico: t.topico, material: t.material, score: t.alunos * (100 - rate) };
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
  }

  function listJoin(items) {
    if (items.length <= 1) return items.join('');
    return `${items.slice(0, -1).join(', ')} e ${items[items.length - 1]}`;
  }

  F.screens['prof-radar'] = {
    render() {
      const s = F.store.state;
      const week = F.data.radar[s.radarWeek];
      const current = s.radarWeek === 's17';
      const open = s.doubts.filter((d) => d.status === 'aberta');
      const answered = s.doubts.filter((d) => d.status === 'respondida').slice(0, 3);
      const perguntas = week.perguntas + (current ? s.extraQuestions : 0);
      const semResposta = current ? open.length : 3;

      const metrics = [
        ['Alunos ativos', `${week.ativos} <small>de ${week.total}</small>`],
        ['Perguntas ao tutor', perguntas],
        ['Acerto nos quizzes', `${week.acerto}%`],
        ['Dúvidas sem resposta', semResposta],
      ]
        .map(([label, value]) => `<div class="fr-metric"><div class="fr-metric-label">${label}</div><div class="fr-metric-value">${value}</div></div>`)
        .join('');

      const max = Math.max(...week.duvidas.map((t) => t.alunos));
      const topics = week.duvidas
        .map((t) => {
          const isOpen = expanded === t.topico;
          const examples = isOpen
            ? `<div class="topic-examples">
                <ul>${t.exemplos.map((e) => `<li>"${F.esc(e)}"</li>`).join('')}</ul>
                <button type="button" class="link-btn" data-action="open-material" data-material="${t.material}">${F.icon('file-text')}Ver o material da aula</button>
              </div>`
            : '';
          return `<div class="topic-item">
            <button type="button" class="topic-toggle" data-action="radar-topic" data-topic="${F.esc(t.topico)}" aria-expanded="${isOpen}">
              <span class="fr-topic"><span>${F.esc(t.topico)}</span><span class="fr-topic-bar"><span style="width:${Math.round((t.alunos / max) * 100)}%"></span></span><span class="fr-topic-count">${t.alunos} alunos</span></span>
              ${F.icon(isOpen ? 'chevron-down' : 'chevron-right')}
            </button>
            ${examples}
          </div>`;
        })
        .join('');

      const rates = [...week.acertoTopicos]
        .sort((a, b) => a.taxa - b.taxa)
        .map((t) => `<div class="fr-topic"><span>${F.esc(t.topico)}</span><span class="fr-topic-bar"><span style="width:${t.taxa}%"></span></span><span class="fr-topic-count ${rateClass(t.taxa)}">${t.taxa}%</span></div>`)
        .join('');

      const suggested = suggestion(week);
      const doubtRows = open.length
        ? open
            .map((d) => `<li class="list-row">
              <span class="file-icon">${F.icon('message-question')}</span>
              <span class="list-row-main"><span>"${F.esc(d.texto)}"</span><span class="small muted">${F.esc(d.quando)} · enviada pelo tutor${d.nova ? ' · <span class="fr-badge fr-badge--accent fr-badge--pill">Nova</span>' : ''}</span></span>
              <button type="button" class="fr-btn fr-btn--outline fr-btn--sm" data-action="radar-answered" data-id="${d.id}">${F.icon('check')}Respondida em aula</button>
            </li>`)
            .join('')
        : '<li class="list-row muted">Nenhuma dúvida pendente. Bom trabalho.</li>';
      const answeredRows = answered
        .map((d) => `<li class="list-row is-done">${F.icon('circle-check')}<span class="list-row-main"><span>"${F.esc(d.texto)}"</span><span class="small muted">Respondida em aula</span></span></li>`)
        .join('');

      return {
        title: 'Radar da turma',
        html: `<div class="page">
          <div class="page-head">
            <div><h1 class="page-title">Radar da turma</h1><p class="page-sub">Estruturas de Dados · SINF2NA · ${F.esc(week.rotulo)}</p></div>
            <div class="fr-field radar-week">
              <label class="fr-label" for="radar-week">Período</label>
              <span class="fr-select-wrap"><select id="radar-week" class="fr-select">
                <option value="s17" ${current ? 'selected' : ''}>Semana 17 (atual)</option>
                <option value="s16" ${!current ? 'selected' : ''}>Semana 16</option>
              </select></span>
            </div>
          </div>
          <div class="metrics">${metrics}</div>
          <section class="panel suggestion" aria-labelledby="h-sug">
            <div class="suggestion-text">
              <h2 id="h-sug" class="card-heading">${F.icon('target')}Sugestão para a próxima aula</h2>
              <p>Comece retomando ${listJoin(suggested.map((t) => `<strong>${F.esc(t.topico.charAt(0).toLowerCase() + t.topico.slice(1))}</strong>`))}: são os tópicos com mais dúvidas e menor acerto nesta semana.</p>
            </div>
            <div class="row">
              <button type="button" class="fr-btn fr-btn--primary fr-btn--sm" data-action="radar-generate">${F.icon('sparkles')}Gerar 5 questões de revisão</button>
              <a class="fr-btn fr-btn--ghost fr-btn--sm" href="#duvidas" data-action="radar-scroll">Ver dúvidas sem resposta</a>
            </div>
          </section>
          <div class="cols-2">
            <section class="panel" aria-labelledby="h-top">
              <div class="panel-head"><h2 id="h-top" class="card-heading">Tópicos com mais dúvidas</h2><span class="small muted">Toque para ver exemplos</span></div>
              <div class="topic-list">${topics}</div>
            </section>
            <section class="panel" aria-labelledby="h-rate">
              <div class="panel-head"><h2 id="h-rate" class="card-heading">Acerto nos quizzes por tópico</h2></div>
              <div class="fr-topics">${rates}</div>
              <p class="small muted legend"><span class="fr-rate--low">abaixo de 50%</span> · <span class="fr-rate--mid">50% a 70%</span> · <span class="fr-rate--high">acima de 70%</span></p>
            </section>
          </div>
          <section class="stack" id="duvidas" aria-labelledby="h-duv">
            <div class="section-head"><h2 id="h-duv" class="section-title">Dúvidas que o material não respondeu</h2><span class="fr-badge fr-badge--pill">${open.length} pendentes</span></div>
            <ul class="panel list">${doubtRows}${answeredRows}</ul>
          </section>
          <p class="privacy-note">${F.icon('shield-lock')}O radar não mostra nomes. Tópicos com menos de 5 alunos não aparecem, e o texto das perguntas passa por remoção de dados pessoais.</p>
        </div>`,
      };
    },
    mount(main) {
      const select = main.querySelector('#radar-week');
      select.addEventListener('change', () => F.store.update((s) => { s.radarWeek = select.value; }));
    },
  };

  Object.assign((F.actions = F.actions || {}), {
    'radar-topic': (el) => {
      expanded = expanded === el.dataset.topic ? null : el.dataset.topic;
      F.render();
    },
    'radar-answered': (el) => {
      F.store.update((s) => {
        const d = s.doubts.find((x) => x.id === el.dataset.id);
        d.status = 'respondida';
        d.nova = false;
        s.doubts = [...s.doubts.filter((x) => x !== d), d];
      });
      F.toast('Dúvida marcada como respondida em aula.');
    },
    'radar-scroll': () => {
      const target = document.getElementById('duvidas');
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },
    'radar-generate': () => {
      const week = F.data.radar[F.store.state.radarWeek];
      const materials = suggestion(week).map((t) => t.material);
      const created = F.generateDrafts(materials, 5);
      F.questoesFilter('pendente');
      F.go('#/professor/questoes');
      setTimeout(() => {
        F.toast(created ? `${created} rascunhos gerados a partir do radar. Revise antes de publicar.` : 'Todas as questões de exemplo desses tópicos já foram geradas.', 'sparkles');
      }, 50);
    },
  });
})();
