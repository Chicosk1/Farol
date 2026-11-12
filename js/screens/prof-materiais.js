/* Professor: materiais da disciplina. O envio de PDF é simulado: o arquivo não sai do navegador. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  const LAST_STEP = F.data.etapasProcessamento.length - 1;
  let timer = null;

  function statusHtml(m) {
    if (m.status === 'pronto') {
      return `<span class="material-status"><span class="fr-badge fr-badge--success">${F.icon('check')}Pronto para o tutor</span><span class="small muted">${Math.round(m.paginas * 2.5)} trechos indexados</span></span>`;
    }
    const step = m.etapa || 0;
    return `<span class="material-status material-status--processing">
      ${F.progress({ value: step + 1, max: LAST_STEP + 1, label: `${F.data.etapasProcessamento[step]}…`, ariaLabel: `Processando Aula ${m.aula}` })}
    </span>`;
  }

  function rowHtml(m) {
    return `<li class="list-row material-row" data-material-row="${m.id}">
      <span class="file-icon">${F.icon('file-type-pdf')}</span>
      <span class="list-row-main"><span class="strong">Aula ${m.aula} · ${F.esc(m.titulo)}</span><span class="small muted">${m.paginas} páginas · enviado ${m.enviadoEm === 'hoje' ? 'hoje' : `em ${m.enviadoEm}`}</span></span>
      ${statusHtml(m)}
      <button type="button" class="fr-icon-btn fr-icon-btn--sm" data-action="open-material" data-material="${m.id}" aria-label="Ver Aula ${m.aula}" ${m.status === 'pronto' ? '' : 'disabled'}>${F.icon('eye')}</button>
    </li>`;
  }

  /* Avança as etapas dos materiais em processamento; continua mesmo se o professor mudar de tela. */
  function tick() {
    const processing = F.store.state.materials.filter((m) => m.status === 'processando');
    if (!processing.length) {
      clearInterval(timer);
      timer = null;
      return;
    }
    F.store.update((s) => {
      s.materials.forEach((m) => {
        if (m.status !== 'processando') return;
        m.etapa = (m.etapa || 0) + 1;
        if (m.etapa >= LAST_STEP) {
          m.status = 'pronto';
          m.etapa = LAST_STEP;
          F.toast(`Aula ${m.aula}, ${m.titulo}, está pronta para o tutor.`);
        }
      });
    }, { render: false });
    processing.forEach((m) => {
      const fresh = F.store.state.materials.find((x) => x.id === m.id);
      const row = document.querySelector(`[data-material-row="${m.id}"]`);
      if (row) row.outerHTML = rowHtml(fresh);
    });
  }

  function startProcessing() {
    if (!timer && F.store.state.materials.some((m) => m.status === 'processando')) timer = setInterval(tick, 1200);
  }

  function addFile(file) {
    if (!file) return;
    const isPdf = file.type === 'application/pdf' || /\.pdf$/i.test(file.name);
    if (!isPdf) {
      F.toast('Envie um arquivo PDF. Slides podem ser exportados como PDF.', 'alert-triangle');
      return;
    }
    const s = F.store.state;
    const nextAula = Math.max(...s.materials.filter((m) => m.disciplina === 'ed').map((m) => m.aula)) + 1;
    const title = file.name.replace(/\.pdf$/i, '').replace(/[_-]+/g, ' ').trim() || 'Material novo';
    F.store.update((st) => {
      st.materials.push({
        id: `ed-up${Date.now()}`,
        disciplina: 'ed',
        aula: nextAula,
        titulo: title.charAt(0).toUpperCase() + title.slice(1),
        paginas: Math.min(60, Math.max(6, Math.round(file.size / 45000))),
        enviadoEm: 'hoje',
        status: 'processando',
        etapa: 0,
      });
    });
    F.toast(`Recebido: ${file.name}`, 'upload');
  }

  F.screens['prof-materiais'] = {
    render() {
      const list = F.store.state.materials.filter((m) => m.disciplina === 'ed').sort((a, b) => b.aula - a.aula);
      return {
        title: 'Materiais',
        html: `<div class="page">
          <div class="page-head">
            <div><h1 class="page-title">Materiais</h1><p class="page-sub">Estruturas de Dados · SINF2NA · Os PDFs publicados aqui alimentam o tutor e o gerador de questões.</p></div>
            <button type="button" class="fr-btn fr-btn--primary" data-action="mat-pick">${F.icon('upload')}Enviar PDF</button>
          </div>
          <div class="dropzone" id="dropzone">
            <span class="empty-state-icon">${F.icon('cloud-upload')}</span>
            <p>Arraste um PDF para cá ou <button type="button" class="link-inline" data-action="mat-pick">escolha um arquivo</button>.</p>
            <p class="small muted">Use PDFs com texto selecionável. No protótipo, o arquivo não sai do seu computador.</p>
            <input type="file" id="upload-input" accept="application/pdf,.pdf" class="sr-only" tabindex="-1" aria-hidden="true">
          </div>
          <section class="stack" aria-labelledby="h-pub">
            <h2 id="h-pub" class="section-title">Publicados (${list.length})</h2>
            <ul class="panel list">${list.map(rowHtml).join('')}</ul>
          </section>
        </div>`,
      };
    },
    mount(main) {
      const input = main.querySelector('#upload-input');
      input.addEventListener('change', () => {
        addFile(input.files[0]);
        input.value = '';
      });
      const zone = main.querySelector('#dropzone');
      ['dragenter', 'dragover'].forEach((type) => zone.addEventListener(type, (event) => {
        event.preventDefault();
        zone.classList.add('is-over');
      }));
      ['dragleave', 'drop'].forEach((type) => zone.addEventListener(type, () => zone.classList.remove('is-over')));
      zone.addEventListener('drop', (event) => {
        event.preventDefault();
        addFile(event.dataTransfer.files[0]);
      });
      startProcessing();
    },
  };

  F.actions = F.actions || {};
  F.actions['mat-pick'] = () => {
    const input = document.getElementById('upload-input');
    if (input) input.click();
  };
})();
