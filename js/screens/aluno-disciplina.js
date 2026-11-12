/* Aluno: página de uma disciplina, com materiais, quizzes aprovados pelo professor e acesso ao tutor. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  F.screens['aluno-disciplina'] = {
    render({ id }) {
      const state = F.store.state;
      const d = F.data.disciplineById(id);
      if (!d) {
        return { title: 'Disciplina', html: `<div class="page">${F.emptyState({ icon: 'school', title: 'Disciplina não encontrada', text: 'Volte para a lista de disciplinas.', action: '<a class="fr-btn fr-btn--outline" href="#/aluno/disciplinas">Ver disciplinas</a>' })}</div>` };
      }
      const materials = state.materials.filter((m) => m.disciplina === id && m.status === 'pronto').sort((a, b) => b.aula - a.aula);
      const quizzes = materials
        .map((m) => ({ m, total: state.drafts.filter((q) => q.material === m.id && q.status === 'aprovada').length }))
        .filter((x) => x.total > 0);

      const materialRows = materials.length
        ? materials
            .map((m) => `<li><button type="button" class="list-row list-row--action" data-action="open-material" data-material="${m.id}">
              <span class="file-icon">${F.icon('file-type-pdf')}</span>
              <span class="list-row-main"><span class="strong">Aula ${m.aula} · ${F.esc(m.titulo)}</span><span class="small muted">${m.paginas} páginas · publicado em ${m.enviadoEm}</span></span>
              ${F.icon('eye')}
            </button></li>`)
            .join('')
        : `<li class="list-row muted">O professor ainda não publicou materiais nesta disciplina.</li>`;

      const quizRows = quizzes.length
        ? quizzes
            .map(({ m, total }) => `<li class="list-row">
              <span class="file-icon file-icon--accent">${F.icon('list-check')}</span>
              <span class="list-row-main"><span class="strong">Quiz da Aula ${m.aula} · ${F.esc(m.titulo)}</span><span class="small muted">${total} ${total === 1 ? 'questão aprovada' : 'questões aprovadas'} pelo professor</span></span>
              <a class="fr-btn fr-btn--outline fr-btn--sm" href="#/aluno/quiz/${m.id}">Fazer quiz</a>
            </li>`)
            .join('')
        : `<li class="list-row muted">Nenhum quiz publicado ainda.</li>`;

      const tutorAction = d.tutor
        ? `<a class="fr-btn fr-btn--primary" href="#/aluno/tutor/${d.id}">${F.icon('message-circle')}Perguntar ao tutor</a>`
        : `<p class="notice">${F.icon('info-circle')}O tutor desta disciplina ainda não foi ativado. Ele começa a funcionar quando o professor publicar os materiais.</p>`;

      return {
        title: d.nome,
        html: `<div class="page">
          <nav class="breadcrumb" aria-label="Você está em"><a href="#/aluno/disciplinas">Disciplinas</a>${F.icon('chevron-right')}<span aria-current="page">${F.esc(d.nome)}</span></nav>
          <div class="discipline-head panel">
            <span class="discipline-icon">${F.icon(d.icone)}</span>
            <div class="discipline-info">
              <h1 class="page-title">${F.esc(d.nome)} (${d.codigo})</h1>
              <p class="page-sub">${F.esc(d.professor)} · ${F.esc(F.data.curso.nome)}</p>
              <div class="discipline-progress">${F.progress({ value: d.progresso, label: `${d.progresso}% concluído`, ariaLabel: `Progresso em ${d.nome}` })}</div>
            </div>
            <div class="discipline-actions">${tutorAction}</div>
          </div>
          <div class="cols-2">
            <section class="stack" aria-labelledby="h-mat"><h2 id="h-mat" class="section-title">Materiais</h2><ul class="panel list">${materialRows}</ul></section>
            <section class="stack" aria-labelledby="h-quiz"><h2 id="h-quiz" class="section-title">Quizzes</h2><ul class="panel list">${quizRows}</ul></section>
          </div>
        </div>`,
      };
    },
  };
})();
