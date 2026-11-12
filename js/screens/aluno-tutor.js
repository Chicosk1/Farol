/* Aluno: tutor da disciplina. Respostas com citação, modo pistas, modo prova e envio anônimo de dúvidas ao professor. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, reduceMotion ? 0 : ms));
  let current = null;

  function settingsOf(id) {
    return F.store.state.settings[id] || { pistas: true, prova: false, limite: 40, politica: '' };
  }

  function tutorBubble(m, index, disciplineId) {
    const tag = m.hint ? `<span class="bubble-tag">${F.icon('bulb')}Modo pistas</span>` : '';
    let extra = '';
    if (m.cite) extra += `<div>${F.cite(m.cite)}</div>`;
    if (m.kind === 'notFound') {
      extra += m.sent
        ? `<p class="bubble-note">${F.icon('circle-check')}Dúvida enviada ao professor, sem o seu nome.</p>`
        : `<div class="fr-bubble-actions"><button type="button" class="fr-btn fr-btn--outline fr-btn--sm" data-action="tutor-send-doubt" data-index="${index}" data-disc="${disciplineId}">Enviar dúvida ao professor</button></div>`;
    }
    if (m.kind === 'answer') {
      extra += `<div class="answer-tools" role="group" aria-label="Avaliar resposta">
        <button type="button" class="tool-btn" data-action="tutor-rate" data-rate="util" data-index="${index}" data-disc="${disciplineId}" aria-pressed="${m.rating === 'util'}">${F.icon('check')}Útil</button>
        <button type="button" class="tool-btn" data-action="tutor-rate" data-rate="incorreta" data-index="${index}" data-disc="${disciplineId}" aria-pressed="${m.rating === 'incorreta'}">${F.icon('alert-triangle')}Incorreta</button>
      </div>`;
    }
    return `<div class="fr-bubble fr-bubble--tutor" data-msg="${index}">${tag}<p class="bubble-text">${F.esc(m.text)}</p>${extra}</div>`;
  }

  function messageHtml(m, index, disciplineId) {
    if (m.from === 'aluno') return `<div class="fr-bubble fr-bubble--student" data-msg="${index}">${F.esc(m.text)}</div>`;
    return tutorBubble(m, index, disciplineId);
  }

  function emptyLog(d) {
    return `<div class="tutor-empty" id="tutor-empty">
      <span class="empty-state-icon">${F.icon('message-circle')}</span>
      <h2 class="section-title">Pergunte sobre ${F.esc(d.nome)}</h2>
      <p class="muted">O tutor só usa o material publicado por ${F.esc(d.professor)} e mostra a página de onde tirou cada resposta. Quando o assunto não estiver no material, ele avisa, e você pode mandar a dúvida para o professor sem se identificar.</p>
    </div>`;
  }

  function counterText(id) {
    return `${F.store.state.questionsToday} de ${settingsOf(id).limite} perguntas hoje`;
  }

  F.screens['aluno-tutor'] = {
    render(params) {
      const id = params.id || 'ed';
      const d = F.data.disciplineById(id);
      const withTutor = F.data.disciplinas.filter((x) => x.tutor);
      if (!d || !d.tutor) {
        return {
          title: 'Tutor',
          html: `<div class="page">${F.emptyState({ icon: 'message-circle', title: 'Tutor indisponível nesta disciplina', text: 'O tutor funciona nas disciplinas em que o professor já publicou materiais.', action: '<a class="fr-btn fr-btn--primary" href="#/aluno/tutor/ed">Abrir tutor de Estruturas de Dados</a>' })}</div>`,
        };
      }
      const s = settingsOf(id);
      const chat = F.store.state.chats[id] || [];
      const options = withTutor.map((x) => `<option value="${x.id}" ${x.id === id ? 'selected' : ''}>${F.esc(x.nome)}</option>`).join('');
      const badges = [
        s.pistas ? `<span class="fr-badge fr-badge--accent fr-badge--pill">${F.icon('bulb')}Modo pistas</span>` : '',
        s.prova ? `<span class="fr-badge fr-badge--danger">${F.icon('lock')}Modo prova</span>` : '',
      ].join('');
      const suggestions = (F.data.sugestoesTutor[id] || [])
        .map((text) => `<button type="button" class="chip-btn" data-action="tutor-suggest" data-text="${F.esc(text)}">${F.esc(text)}</button>`)
        .join('');

      const body = s.prova
        ? `<section class="panel tutor-locked" aria-labelledby="h-lock">
            <span class="empty-state-icon">${F.icon('lock')}</span>
            <h2 id="h-lock" class="section-title">O tutor está pausado durante a prova</h2>
            <p class="muted">${F.esc(d.professor)} ativou o modo prova nesta disciplina. O tutor volta a responder quando a prova terminar.</p>
          </section>`
        : `<div class="tutor-log" id="tutor-log" aria-live="polite">${chat.length ? chat.map((m, i) => messageHtml(m, i, id)).join('') : emptyLog(d)}</div>
          <div class="composer">
            <div class="suggestions" aria-label="Sugestões de pergunta">${suggestions}</div>
            <form class="composer-form" id="tutor-form" novalidate>
              <label for="tutor-input" class="sr-only">Sua pergunta</label>
              <input id="tutor-input" class="fr-input" placeholder="Pergunte sobre ${F.esc(d.nome)}" autocomplete="off" maxlength="300">
              <button type="submit" class="fr-btn fr-btn--primary composer-send" aria-label="Enviar pergunta">${F.icon('send')}</button>
            </form>
            <p class="composer-error" id="tutor-error" role="alert"></p>
            <p class="small muted composer-meta"><span id="tutor-counter">${counterText(id)}</span> · As dúvidas chegam ao professor sem o seu nome.</p>
          </div>`;

      return {
        title: `Tutor · ${d.nome}`,
        html: `<div class="page page--tutor">
          <div class="tutor-head">
            <div>
              <h1 class="page-title">Tutor</h1>
              <p class="page-sub">Respostas só com o material ${F.esc(F.ofProfessor(d))}, sempre com a página citada.</p>
            </div>
            <div class="tutor-select">
              <label for="tutor-disc" class="fr-label">Disciplina</label>
              <span class="fr-select-wrap"><select id="tutor-disc" class="fr-select">${options}</select></span>
            </div>
          </div>
          <div class="tutor-status">${badges}<button type="button" class="link-btn" data-action="tutor-policy" data-disc="${id}">${F.icon('shield-lock')}Política de uso de IA</button></div>
          ${body}
        </div>`,
      };
    },

    mount(main, params) {
      const id = params.id || 'ed';
      const select = main.querySelector('#tutor-disc');
      if (select) select.addEventListener('change', () => F.go(`#/aluno/tutor/${select.value}`));
      const form = main.querySelector('#tutor-form');
      if (!form) { current = null; return; }

      const input = main.querySelector('#tutor-input');
      const log = main.querySelector('#tutor-log');
      const error = main.querySelector('#tutor-error');
      const keepBottom = () => { main.scrollTop = main.scrollHeight; };
      let busy = false;
      keepBottom();

      input.addEventListener('input', () => { error.textContent = ''; });

      async function ask(question) {
        const text = question.trim();
        if (busy) return;
        if (!text) {
          error.textContent = 'Escreva uma pergunta antes de enviar.';
          input.focus();
          return;
        }
        const s = settingsOf(id);
        if (F.store.state.questionsToday >= s.limite) {
          error.textContent = `Você chegou ao limite de ${s.limite} perguntas de hoje. O limite volta amanhã.`;
          return;
        }
        busy = true;
        input.value = '';
        const empty = main.querySelector('#tutor-empty');
        if (empty) empty.remove();

        F.store.update((st) => {
          st.chats[id] = st.chats[id] || [];
          st.chats[id].push({ from: 'aluno', text });
          st.questionsToday += 1;
          st.extraQuestions += 1;
        }, { render: false });
        const studentIndex = F.store.state.chats[id].length - 1;
        log.insertAdjacentHTML('beforeend', messageHtml(F.store.state.chats[id][studentIndex], studentIndex, id));
        main.querySelector('#tutor-counter').textContent = counterText(id);

        log.insertAdjacentHTML('beforeend', `<div class="fr-bubble fr-bubble--tutor is-typing" id="tutor-typing"><span class="spin">${F.icon('loader-2')}</span>Procurando no material…</div>`);
        keepBottom();
        await wait(900);

        const res = F.tutor.answer(id, text);
        const message = { from: 'tutor', kind: res.kind, text: res.text, cite: res.cite || null, hint: Boolean(res.hint) };
        F.store.update((st) => { st.chats[id].push(message); }, { render: false });
        const index = F.store.state.chats[id].length - 1;

        const typing = main.querySelector('#tutor-typing');
        if (!typing) { busy = false; return; }
        typing.outerHTML = `<div class="fr-bubble fr-bubble--tutor" data-msg="${index}">${message.hint ? `<span class="bubble-tag">${F.icon('bulb')}Modo pistas</span>` : ''}<p class="bubble-text"></p></div>`;
        const bubble = log.querySelector(`[data-msg="${index}"]`);
        const target = bubble.querySelector('.bubble-text');
        if (reduceMotion) {
          target.textContent = message.text;
        } else {
          for (let i = 0; i <= message.text.length; i += 3) {
            target.textContent = message.text.slice(0, i);
            keepBottom();
            await wait(14);
          }
        }
        bubble.outerHTML = tutorBubble(message, index, id);
        keepBottom();
        busy = false;
        input.focus();
      }

      form.addEventListener('submit', (event) => {
        event.preventDefault();
        ask(input.value);
      });
      current = { ask };
    },
  };

  Object.assign((F.actions = F.actions || {}), {
    'tutor-suggest': (el) => { if (current) current.ask(el.dataset.text); },
    'tutor-policy': (el) => {
      const d = F.data.disciplineById(el.dataset.disc);
      F.openModal({
        title: 'Política de uso de IA',
        subtitle: `${d.nome} · definida por ${d.professor}`,
        body: `<p class="policy-text">${F.esc(settingsOf(d.id).politica)}</p>
          <ul class="policy-list">
            <li>${F.icon('file-text')}O tutor responde só com o material da disciplina e cita a página.</li>
            <li>${F.icon('bulb')}Em exercícios, ele dá pistas em vez de entregar a resposta.</li>
            <li>${F.icon('shield-lock')}O professor vê os temas das dúvidas da turma, nunca quem perguntou.</li>
          </ul>`,
      });
    },
    'tutor-send-doubt': (el) => {
      const id = el.dataset.disc;
      const index = Number(el.dataset.index);
      const chat = F.store.state.chats[id];
      const question = [...chat.slice(0, index)].reverse().find((m) => m.from === 'aluno');
      F.store.update((s) => {
        s.chats[id][index].sent = true;
        s.doubts.unshift({ id: `n${Date.now()}`, texto: question ? question.text : 'Dúvida sem texto', quando: F.nowLabel(), status: 'aberta', nova: true });
      }, { render: false });
      el.closest('.fr-bubble').outerHTML = tutorBubble(F.store.state.chats[id][index], index, id);
      F.toast('Dúvida enviada ao professor, sem o seu nome.');
    },
    'tutor-rate': (el) => {
      const id = el.dataset.disc;
      const index = Number(el.dataset.index);
      const rate = el.dataset.rate;
      F.store.update((s) => {
        const m = s.chats[id][index];
        m.rating = m.rating === rate ? null : rate;
      }, { render: false });
      const m = F.store.state.chats[id][index];
      el.closest('.fr-bubble').outerHTML = tutorBubble(m, index, id);
      if (m.rating === 'incorreta') F.toast('Obrigado. Respostas marcadas como incorretas vão para revisão da equipe.', 'info-circle');
      if (m.rating === 'util') F.toast('Obrigado pela avaliação.');
    },
  });
})();
