/* Aluno: revisão do dia (repetição espaçada) e quizzes aprovados pelo professor. As duas telas usam o mesmo motor. */
/* Specs: QUE-RF-04, QUE-RF-08, QUE-RF-09, QUE-RF-10, REV-RF-01, REV-RF-02, REV-RF-03, REV-RF-04, REV-RF-05, REV-RF-08, REV-RF-10. Rastreabilidade em docs/rastreabilidade.md. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  const INTERVALS = { dificil: 'amanhã', bom: 'em 3 dias', facil: 'em 7 dias' };

  /* Monta a lista de questões de cada modo, no mesmo formato. */
  function deckFor(key) {
    if (key === 'revisao') return F.data.revisao;
    const material = F.data.materialById(key);
    if (!material) return [];
    return F.store.state.drafts
      .filter((q) => q.material === key && q.status === 'aprovada')
      .map((q) => Object.assign({ disciplina: material.disciplina, topico: material.titulo }, q));
  }

  function ensurePractice(key, total) {
    const s = F.store.state;
    if (!s.practice || s.practice.key !== key || s.practice.total !== total) {
      s.practice = { key, total, index: 0, picked: null, answers: [] };
      F.store.save();
    }
    return s.practice;
  }

  function summary(key, deck, result) {
    const isReview = key === 'revisao';
    const wrong = result.erros || [];
    const material = isReview ? null : F.data.materialById(key);
    const chips = wrong
      .map((e) => `<a class="chip-btn" href="#/aluno/tutor/${e.disciplina}">${F.icon('message-circle')}${F.esc(e.topico)}</a>`)
      .join('');
    return `<section class="panel result" aria-labelledby="h-result">
      <span class="result-icon">${F.icon('circle-check')}</span>
      <h2 id="h-result" class="section-title">${isReview ? 'Revisão concluída' : 'Quiz concluído'}</h2>
      <p class="result-score"><strong>${result.acertos} de ${deck.length}</strong> acertos</p>
      ${wrong.length ? `<p class="muted">Vale perguntar ao tutor sobre:</p><div class="chip-row">${chips}</div>` : '<p class="muted">Você acertou tudo.</p>'}
      ${isReview ? '<p class="small muted">A próxima revisão fica pronta amanhã às 6h. Os cartões que você achou difíceis voltam primeiro.</p>' : ''}
      <div class="row row--center">
        <a class="fr-btn fr-btn--primary" href="${isReview ? '#/aluno/inicio' : `#/aluno/disciplina/${material.disciplina}`}">${isReview ? 'Voltar ao início' : 'Voltar para a disciplina'}</a>
        <button type="button" class="fr-btn fr-btn--outline" data-action="practice-restart" data-key="${key}">${isReview ? 'Refazer revisão' : 'Refazer quiz'}</button>
      </div>
    </section>`;
  }

  function questionCard(key, deck, p) {
    const q = deck[p.index];
    const d = F.data.disciplineById(q.disciplina);
    const answered = p.picked !== null;
    const options = q.opcoes
      .map((text, i) => {
        let cls = 'fr-option';
        let mark = '';
        if (answered && i === q.correta) { cls += ' fr-option--correct'; mark = F.icon('check'); }
        else if (answered && i === p.picked) { cls += ' fr-option--wrong'; mark = F.icon('x'); }
        const state = answered ? (i === q.correta ? ', resposta correta' : i === p.picked ? ', sua resposta' : '') : '';
        return `<button type="button" class="${cls}" data-action="practice-pick" data-option="${i}" ${answered ? 'aria-disabled="true"' : ''} aria-label="${'ABCD'[i]}: ${F.esc(text)}${state}"><span class="fr-option-key">${'ABCD'[i]}</span>${F.esc(text)}${mark}</button>`;
      })
      .join('');
    let after = '';
    if (answered) {
      const ok = p.picked === q.correta;
      const isLast = p.index === deck.length - 1;
      after = `<div class="fr-feedback ${ok ? '' : 'fr-feedback--wrong'}" role="status">${ok ? 'Certo.' : 'Não foi dessa vez.'} ${F.esc(q.justificativa)} <button type="button" class="link-inline" data-action="open-cite" data-cite="${q.cite}">Ver ${F.esc(F.citeLabel(q.cite))}</button></div>`;
      after +=
        key === 'revisao'
          ? `<div class="rating"><p class="small muted">Como foi lembrar disso?</p><div class="rating-btns">
              <button type="button" class="fr-btn fr-btn--outline fr-btn--sm" data-action="practice-next" data-rate="dificil">Difícil</button>
              <button type="button" class="fr-btn fr-btn--outline fr-btn--sm" data-action="practice-next" data-rate="bom">Bom</button>
              <button type="button" class="fr-btn fr-btn--outline fr-btn--sm" data-action="practice-next" data-rate="facil">Fácil</button>
            </div></div>`
          : `<div class="row row--end"><button type="button" class="fr-btn fr-btn--primary fr-btn--sm" data-action="practice-next">${isLast ? 'Ver resultado' : 'Próxima'}</button></div>`;
    }
    return `<section class="panel quiz-card" aria-labelledby="q-title">
      <p class="quiz-topic">${F.esc(d.nome)} · ${F.esc(q.topico)}</p>
      <h2 class="fr-card-title quiz-question" id="q-title">${F.esc(q.pergunta)}</h2>
      <div class="fr-options">${options}</div>
      ${after}
    </section>`;
  }

  function renderPractice(key) {
    const s = F.store.state;
    const deck = deckFor(key);
    const isReview = key === 'revisao';
    const material = isReview ? null : F.data.materialById(key);
    const title = isReview ? 'Revisão do dia' : `Quiz da Aula ${material ? material.aula : ''}`;
    const sub = isReview
      ? `${deck.length} cartões · Estruturas de Dados e Banco de Dados I`
      : material ? `${F.data.disciplineById(material.disciplina).nome} · ${material.titulo} · questões aprovadas pelo professor` : '';

    if (!deck.length) {
      return { title, html: `<div class="page page--narrow">${F.emptyState({ icon: 'list-check', title: 'Nenhuma questão aprovada ainda', text: 'Quando o professor aprovar questões desta aula, elas aparecem aqui.', action: '<a class="fr-btn fr-btn--outline" href="#/aluno/disciplinas">Ver disciplinas</a>' })}</div>` };
    }

    let content;
    let count;
    if (isReview && s.reviewDone) {
      content = summary(key, deck, s.reviewDone);
      count = deck.length;
    } else {
      const p = ensurePractice(key, deck.length);
      if (p.done) {
        content = summary(key, deck, p.result);
        count = deck.length;
      } else {
        content = questionCard(key, deck, p);
        count = p.index + (p.picked !== null ? 1 : 0);
      }
    }

    const back = isReview ? '' : `<nav class="breadcrumb" aria-label="Você está em"><a href="#/aluno/disciplina/${material.disciplina}">${F.esc(F.data.disciplineById(material.disciplina).nome)}</a>${F.icon('chevron-right')}<span aria-current="page">${F.esc(title)}</span></nav>`;
    return {
      title,
      html: `<div class="page page--narrow">
        ${back}
        <div class="page-head"><div><h1 class="page-title">${F.esc(title)}</h1><p class="page-sub">${F.esc(sub)}</p></div></div>
        ${F.progress({ value: count, max: deck.length, label: `${count} de ${deck.length} ${isReview ? 'cartões' : 'questões'}` })}
        ${content}
      </div>`,
    };
  }

  F.screens['aluno-revisao'] = { render: () => renderPractice('revisao') };
  F.screens['aluno-quiz'] = { render: ({ id }) => renderPractice(id) };

  Object.assign((F.actions = F.actions || {}), {
    'practice-pick': (el) => {
      const p = F.store.state.practice;
      if (!p || p.picked !== null) return;
      F.store.update(() => { p.picked = Number(el.dataset.option); });
      const feedback = document.querySelector('.fr-feedback');
      if (feedback) feedback.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    },
    'practice-next': (el) => {
      const s = F.store.state;
      const p = s.practice;
      const deck = deckFor(p.key);
      const q = deck[p.index];
      const answer = { correct: p.picked === q.correta, disciplina: q.disciplina, topico: q.topico };
      if (el.dataset.rate) F.toast(`Este cartão volta ${INTERVALS[el.dataset.rate]}.`, 'clock');
      F.store.update(() => {
        p.answers.push(answer);
        p.picked = null;
        if (p.index === deck.length - 1) {
          const result = { acertos: p.answers.filter((a) => a.correct).length, erros: p.answers.filter((a) => !a.correct).map(({ disciplina, topico }) => ({ disciplina, topico })) };
          if (p.key === 'revisao') {
            s.reviewDone = result;
            s.practice = null;
          } else {
            p.done = true;
            p.result = result;
          }
        } else {
          p.index += 1;
        }
      });
    },
    'practice-restart': (el) => {
      F.store.update((s) => {
        if (el.dataset.key === 'revisao') s.reviewDone = null;
        s.practice = null;
      });
    },
  });
})();
