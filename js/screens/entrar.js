/* Tela de entrada: escolha do perfil. No produto, o acesso é pelo login institucional (OpenID Connect). */
/* Specs: ACE-RF-01, ACE-RF-02. Rastreabilidade em docs/rastreabilidade.md. */
(function () {
  'use strict';
  const F = window.Farol;
  F.screens = F.screens || {};

  F.screens.entrar = {
    render() {
      const { aluno, professor } = F.data.pessoas;
      const option = (role, person, title) => `<button type="button" class="role-option" data-action="enter" data-role="${role}">
        <span class="fr-avatar fr-avatar--lg" aria-hidden="true">${person.iniciais}</span>
        <span class="role-option-text"><span class="role-option-title">${title}</span><span class="small muted">${F.esc(person.nome)} · ${F.esc(person.descricao)}</span></span>
        ${F.icon('chevron-right')}
      </button>`;
      return {
        title: 'Entrar',
        html: `<main class="login" id="conteudo">
          <div class="login-card">
            <div class="fr-wordmark"><b>Farol</b><span>Tutor de estudos</span></div>
            <div class="stack-sm">
              <h1 class="page-title">Como você quer entrar?</h1>
              <p class="muted">Protótipo navegável com dados fictícios do curso de Sistemas de Informação. No produto, o acesso é feito com a conta institucional.</p>
            </div>
            <div class="role-options">
              ${option('aluno', aluno, 'Entrar como aluna')}
              ${option('professor', professor, 'Entrar como professor')}
            </div>
            <p class="small muted login-hint">${F.icon('presentation')}Use a barra de demonstração, no canto da tela, para trocar de perfil a qualquer momento.</p>
          </div>
        </main>`,
      };
    },
  };

  F.actions = F.actions || {};
  F.actions.enter = (el) => {
    const role = el.dataset.role;
    F.store.update((s) => { s.role = role; }, { render: false });
    F.go(F.home(role));
  };
})();
