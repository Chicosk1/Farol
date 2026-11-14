/* Professor: configurações da disciplina. Modo pistas, modo prova, limite diário, resumo semanal e política de uso de IA. */
/* Specs: ACE-RF-06, TUT-RF-06, TUT-RF-07, TUT-RF-08, TUT-RF-10, RAD-RF-10. Rastreabilidade em docs/rastreabilidade.md. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  function switchRow({ key, title, text, checked, extra = '' }) {
    return `<div class="switch-row">
      <div class="switch-text"><label class="strong" for="sw-${key}">${title}</label><p class="small muted" id="sw-${key}-desc">${text}</p>${extra}</div>
      <input type="checkbox" class="switch" id="sw-${key}" data-setting="${key}" aria-describedby="sw-${key}-desc" ${checked ? 'checked' : ''}>
    </div>`;
  }

  F.screens['prof-disciplina'] = {
    render() {
      const s = F.store.state.settings.ed;
      const provaNotice = s.prova ? `<p class="notice notice--danger">${F.icon('lock')}O tutor está pausado para a turma agora. Desligue quando a prova terminar.</p>` : '';
      const limitOptions = [20, 40, 60].map((n) => `<option value="${n}" ${s.limite === n ? 'selected' : ''}>${n} perguntas</option>`).join('');
      return {
        title: 'Disciplina',
        html: `<div class="page page--narrow">
          <div class="page-head"><div><h1 class="page-title">Disciplina</h1><p class="page-sub">Estruturas de Dados · SINF2NA · 46 alunos</p></div></div>
          <section class="panel" aria-labelledby="h-tutor">
            <h2 id="h-tutor" class="card-heading">Tutor</h2>
            ${switchRow({ key: 'pistas', title: 'Modo pistas', text: 'Em perguntas de exercício, o tutor guia em etapas e não entrega a resposta final.', checked: s.pistas })}
            ${switchRow({ key: 'prova', title: 'Modo prova', text: 'Pausa o tutor para toda a turma. Use durante avaliações.', checked: s.prova, extra: provaNotice })}
            <div class="switch-row">
              <div class="switch-text"><label class="strong" for="limite">Limite diário por aluno</label><p class="small muted">Controla o custo e evita abuso. O contador zera à meia-noite.</p></div>
              <span class="fr-select-wrap select-inline"><select id="limite" class="fr-select">${limitOptions}</select></span>
            </div>
          </section>
          <section class="panel" aria-labelledby="h-radar">
            <h2 id="h-radar" class="card-heading">Radar</h2>
            ${switchRow({ key: 'resumo', title: 'Resumo semanal por e-mail', text: 'Toda segunda, às 7h, com os tópicos de mais dúvida e as dúvidas sem resposta.', checked: s.resumo })}
          </section>
          <section class="panel" aria-labelledby="h-pol">
            <h2 id="h-pol" class="card-heading">Política de uso de IA</h2>
            <p class="small muted">Os alunos veem este texto no tutor, no link "Política de uso de IA".</p>
            <label class="sr-only" for="politica">Texto da política</label>
            <textarea id="politica" class="fr-input textarea" rows="4">${F.esc(s.politica)}</textarea>
            <div class="row row--end"><button type="button" class="fr-btn fr-btn--outline fr-btn--sm" data-action="save-policy">Salvar política</button></div>
          </section>
          <section class="panel" aria-labelledby="h-turma">
            <h2 id="h-turma" class="card-heading">Turma</h2>
            <div class="switch-row">
              <div class="switch-text"><p class="strong">46 alunos matriculados</p><p class="small muted">Importados do sistema acadêmico em 20/07/2026, por planilha CSV.</p></div>
              <button type="button" class="fr-btn fr-btn--outline fr-btn--sm" data-action="import-csv">${F.icon('upload')}Importar CSV</button>
            </div>
          </section>
        </div>`,
      };
    },
    mount(main) {
      main.querySelectorAll('.switch').forEach((input) => {
        input.addEventListener('change', () => {
          const key = input.dataset.setting;
          F.store.update((s) => { s.settings.ed[key] = input.checked; }, { render: key === 'prova' });
          const labels = {
            pistas: input.checked ? 'Modo pistas ligado.' : 'Modo pistas desligado: o tutor responde exercícios diretamente.',
            prova: input.checked ? 'Modo prova ligado: o tutor está pausado para a turma.' : 'Modo prova desligado: o tutor voltou a responder.',
            resumo: input.checked ? 'Resumo semanal ligado.' : 'Resumo semanal desligado.',
          };
          F.toast(labels[key], input.checked ? 'circle-check' : 'info-circle');
        });
      });
      const limite = main.querySelector('#limite');
      limite.addEventListener('change', () => {
        F.store.update((s) => { s.settings.ed.limite = Number(limite.value); }, { render: false });
        F.toast(`Limite diário: ${limite.value} perguntas por aluno.`);
      });
    },
  };

  Object.assign((F.actions = F.actions || {}), {
    'save-policy': () => {
      const text = document.getElementById('politica').value.trim();
      if (!text) {
        F.toast('A política não pode ficar vazia.', 'alert-triangle');
        return;
      }
      F.store.update((s) => { s.settings.ed.politica = text; }, { render: false });
      F.toast('Política salva. Os alunos já veem o texto novo.');
    },
    'import-csv': () => F.toast('No protótipo, a importação de turma é simulada.', 'info-circle'),
  });
})();
