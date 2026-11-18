/** Datas no formato das telas do protótipo, em português do Brasil. */

/** "Quarta-feira, 18 de novembro", para o subtítulo da tela inicial. */
export function hojePorExtenso(agora = new Date()): string {
  const texto = new Intl.DateTimeFormat('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  }).format(agora);
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

/** "hoje, 08h05" para hoje e "10/11" para outros dias, como nas novidades do protótipo. */
export function quando(iso: string, agora = new Date()): string {
  const data = new Date(iso);
  const mesmoDia =
    data.getFullYear() === agora.getFullYear() &&
    data.getMonth() === agora.getMonth() &&
    data.getDate() === agora.getDate();
  if (mesmoDia) {
    const hora = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' }).format(
      data,
    );
    return `hoje, ${hora.replace(':', 'h')}`;
  }
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit' }).format(data);
}
