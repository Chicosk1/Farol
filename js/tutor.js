/* Farol — tutor simulado. No produto, aqui entra a busca nos trechos (pgvector) e a chamada ao modelo de linguagem.
   No protótipo, a resposta vem de uma base fixa em data.js, escolhida por palavras-chave. */
(function () {
  'use strict';
  const F = window.Farol;

  const GREETING = /^(oi|ola|bom dia|boa tarde|boa noite|e ai)\b/;
  const EXERCISE = ['exercicio', 'resposta', 'resolve', 'resolva', 'gabarito', 'codigo pronto', 'faz o codigo', 'implementa pra mim', 'me da o codigo'];
  const OUT_OF_SCOPE = ['cai na prova', 'vai cair', 'nota', 'recuperacao', 'data da prova', 'quando e a prova', 'presenca', 'falta', 'trabalho em grupo'];

  function bestEntry(entries, text) {
    let best = null;
    let bestHits = 0;
    entries.forEach((entry) => {
      const hits = entry.keys.filter((key) => text.includes(key)).length;
      if (hits > bestHits) {
        best = entry;
        bestHits = hits;
      }
    });
    return best;
  }

  /* Decide a resposta para uma pergunta. Retorna { kind, text, cite, hint }. */
  function answer(disciplineId, question) {
    const text = F.normalize(question);
    const discipline = F.data.disciplineById(disciplineId);
    const settings = F.store.state.settings[disciplineId] || {};

    if (GREETING.test(text) && text.split(' ').length <= 4) {
      return {
        kind: 'greeting',
        text: `Oi, ${F.data.pessoas.aluno.nome.split(' ')[0]}. Pergunte sobre o conteúdo de ${discipline.nome}: eu respondo só com base no material publicado ${discipline.professor.replace('Prof.ª ', 'pela professora ').replace('Prof. ', 'pelo professor ')}.`,
      };
    }

    if (OUT_OF_SCOPE.some((key) => text.includes(key))) {
      return { kind: 'notFound', text: 'Não encontrei isso no material da disciplina.' };
    }

    const wantsAnswer = EXERCISE.some((key) => text.includes(key));
    const entry = bestEntry(F.data.tutor[disciplineId] || [], text);

    if (!entry) {
      if (wantsAnswer && settings.pistas) {
        return {
          kind: 'hint',
          hint: true,
          text: 'Posso te ajudar a chegar lá, mas não entrego a resposta pronta. Qual parte está travando: entender o enunciado, escolher a estrutura ou escrever o código?',
        };
      }
      return { kind: 'notFound', text: 'Não encontrei isso no material da disciplina.' };
    }

    if (wantsAnswer && settings.pistas) {
      return { kind: 'answer', hint: true, text: entry.pistas, cite: entry.cite };
    }
    return { kind: 'answer', text: entry.resposta, cite: entry.cite };
  }

  F.tutor = { answer };
})();
