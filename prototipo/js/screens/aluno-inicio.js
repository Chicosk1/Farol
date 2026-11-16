/* Aluno: tela inicial com revisão do dia, atalho para o tutor, novidades e disciplinas. */
/* Specs: ACE-RF-10, REV-RF-06, REV-RF-07. Rastreabilidade em docs/rastreabilidade.md. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  function reviewCard() {
    const state = F.store.state;
    const total = F.data.revisao.length;
    const done = state.reviewDone;
    const inProgress = state.practice && state.practice.key === 'revisao' && !done ? state.practice.index : 0;
    let body;
    if (done) {
      body = `<p class="home-card-text">Concluída: ${done.acertos} de ${total} acertos. A próxima fica pronta amanhã às 6h.</p>
        <a class="fr-btn fr-btn--outline fr-btn--sm" href="#/aluno/revisao">Ver resultado</a>`;
    } else {
      body = `<p class="home-card-text">${total} cartões de Estruturas de Dados e Banco de Dados I, cerca de 4 minutos.</p>
        ${inProgress ? F.progress({ value: inProgress, max: total, label: `${inProgress} de ${total} cartões` }) : ''}
        <a class="fr-btn fr-btn--primary fr-btn--sm" href="#/aluno/revisao">${inProgress ? 'Continuar' : 'Começar revisão'}</a>`;
    }
    return `<section class="panel home-card home-card--review" aria-labelledby="h-revisao">
      <div class="home-card-head"><span class="home-card-icon">${F.icon('cards')}</span><h2 id="h-revisao" class="card-heading">Revisão do dia</h2></div>
      ${body}
    </section>`;
  }

  function tutorCard() {
    const chat = F.store.state.chats.ed || [];
    const last = [...chat].reverse().find((m) => m.from === 'aluno');
    const text = last
      ? `Sua última pergunta: "${F.esc(last.text)}"`
      : 'Ficou com dúvida da aula de ontem? Pergunte ao tutor: ele responde com o material do professor e mostra a página.';
    return `<section class="panel home-card" aria-labelledby="h-tutor">
      <div class="home-card-head"><span class="home-card-icon">${F.icon('message-circle')}</span><h2 id="h-tutor" class="card-heading">Tutor de Estruturas de Dados</h2></div>
      <p class="home-card-text">${text}</p>
      <a class="fr-btn fr-btn--outline fr-btn--sm" href="#/aluno/tutor/ed">${last ? 'Continuar conversa' : 'Abrir tutor'}</a>
    </section>`;
  }

  function streakCard() {
    const doneToday = Boolean(F.store.state.reviewDone);
    const days = doneToday ? 6 : 5;
    const initials = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];
    let dots = '';
    /* Últimos 7 dias, terminando hoje: os 5 dias anteriores têm revisão feita. */
    for (let offset = 6; offset >= 0; offset -= 1) {
      const date = new Date();
      date.setDate(date.getDate() - offset);
      const done = offset === 0 ? doneToday : offset <= 5;
      dots += `<span class="streak-day ${done ? 'is-done' : ''} ${offset === 0 ? 'is-today' : ''}" aria-hidden="true">${initials[date.getDay()]}</span>`;
    }
    return `<section class="panel home-card" aria-labelledby="h-seq">
      <div class="home-card-head"><span class="home-card-icon home-card-icon--highlight">${F.icon('flame')}</span><h2 id="h-seq" class="card-heading">${days} dias seguidos</h2></div>
      <p class="home-card-text">${F.store.state.reviewDone ? 'Revisão de hoje feita. Volte amanhã para manter a sequência.' : 'Faça a revisão de hoje para chegar a 6 dias.'}</p>
      <div class="streak" role="img" aria-label="Revisão feita em ${days} dos últimos 7 dias">${dots}</div>
    </section>`;
  }

  F.screens['aluno-inicio'] = {
    render() {
      const state = F.store.state;
      const first = F.data.pessoas.aluno.nome.split(' ')[0];
      const ordered = [...F.data.disciplinas].sort((a, b) => state.favorites.includes(b.id) - state.favorites.includes(a.id));
      const cards = ordered.slice(0, 3).map((d) => F.courseCard(d, { favorite: state.favorites.includes(d.id) })).join('');
      const news = F.data.novidadesAluno
        .map((n) => `<li class="list-row">${F.icon(n.icone)}<div><p>${F.esc(n.texto)}</p><p class="small muted">${F.esc(n.quando)}</p></div></li>`)
        .join('');
      return {
        title: 'Início',
        html: `<div class="page">
          <div class="page-head">
            <div><h1 class="page-title">Olá, ${F.esc(first)}</h1><p class="page-sub">${F.todayLabel()}</p></div>
          </div>
          <div class="home-grid">${reviewCard()}${tutorCard()}${streakCard()}</div>
          <section class="stack" aria-labelledby="h-novidades">
            <h2 id="h-novidades" class="section-title">Novidades</h2>
            <ul class="panel list">${news}</ul>
          </section>
          <section class="stack" aria-labelledby="h-disc">
            <div class="section-head"><h2 id="h-disc" class="section-title">Suas disciplinas</h2><a class="link-btn" href="#/aluno/disciplinas">Ver todas${F.icon('chevron-right')}</a></div>
            <div class="grid-cards">${cards}</div>
          </section>
        </div>`,
      };
    },
  };

  F.actions = F.actions || {};
  F.actions['toggle-fav'] = (el) => {
    const id = el.dataset.id;
    F.store.update((s) => {
      s.favorites = s.favorites.includes(id) ? s.favorites.filter((x) => x !== id) : [...s.favorites, id];
    });
  };
})();
