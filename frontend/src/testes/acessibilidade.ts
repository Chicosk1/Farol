import axe from 'axe-core';

/**
 * Roda o axe no elemento e devolve as violações em texto, para a falha do teste dizer o que corrigir.
 * Toda tela nova tem pelo menos um teste que espera uma lista vazia (princípio V da constituição).
 *
 * O contraste de cores não é medido aqui: o jsdom não calcula estilos. Ele é conferido no navegador,
 * na auditoria de acessibilidade (ACE-T90).
 */
export async function violacoesDeAcessibilidade(elemento: Element): Promise<string[]> {
  const resultado = await axe.run(elemento, {
    rules: { 'color-contrast': { enabled: false } },
  });
  return resultado.violations.map(
    (violacao) => `${violacao.id}: ${violacao.help} (${violacao.nodes.length} elemento(s))`,
  );
}
