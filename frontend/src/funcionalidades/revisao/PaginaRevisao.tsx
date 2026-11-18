import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router';

import {
  avaliarCartao,
  responderCartao,
  type AvaliacaoDoCartao,
  type RevisaoDeHoje,
} from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { classesDoBotao } from '../../componentes/classes';
import { useAvisos } from '../../componentes/contextoDosAvisos';
import { EstadoVazio } from '../../componentes/EstadoVazio';
import { Icone } from '../../componentes/Icone';
import { Progresso } from '../../componentes/Progresso';
import { LETRAS, tutorComPergunta } from '../questoes/textos';
import { CHAVE_DA_REVISAO, useRevisaoDeHoje } from './consultas';

const AVALIACOES: { id: AvaliacaoDoCartao; rotulo: string }[] = [
  { id: 'dificil', rotulo: 'Difícil' },
  { id: 'bom', rotulo: 'Bom' },
  { id: 'facil', rotulo: 'Fácil' },
];

/**
 * A revisão do dia, como no protótipo: um cartão por vez, o retorno, a avaliação Difícil, Bom
 * ou Fácil, e o resumo no fim (REV-RF-03, REV-RF-04, REV-RF-05, REV-RF-10).
 */
export function PaginaRevisao() {
  const revisao = useRevisaoDeHoje();
  const clienteDeDados = useQueryClient();
  const avisar = useAvisos();
  const atualizar = (mudar: (dados: RevisaoDeHoje) => RevisaoDeHoje) =>
    clienteDeDados.setQueryData<RevisaoDeHoje>(CHAVE_DA_REVISAO, (dados) =>
      dados ? mudar(dados) : dados,
    );
  const responder = useMutation({
    mutationFn: ({ cartao, alternativa }: { cartao: number; alternativa: number }) =>
      responderCartao(cartao, alternativa),
    onSuccess: (retorno) =>
      atualizar((dados) => ({
        ...dados,
        respostas: [...dados.respostas, { ...retorno, avaliacao: '', volta: '' }],
      })),
  });
  const avaliar = useMutation({
    mutationFn: ({ cartao, avaliacao }: { cartao: number; avaliacao: AvaliacaoDoCartao }) =>
      avaliarCartao(cartao, avaliacao),
    onSuccess: async (agenda, { cartao, avaliacao }) => {
      avisar(agenda.texto, 'clock');
      atualizar((dados) => ({
        ...dados,
        respostas: dados.respostas.map((r) =>
          r.cartao === cartao ? { ...r, avaliacao, volta: agenda.texto } : r,
        ),
      }));
      await clienteDeDados.invalidateQueries({ queryKey: CHAVE_DA_REVISAO });
    },
  });

  const dados = revisao.data;
  const total = dados?.cartoes.length ?? 0;
  const cabecalho = (
    <div className="page-head">
      <div>
        <h1 className="page-title">Revisão do dia</h1>
        {dados && total > 0 && (
          <p className="page-sub">
            {total} {total === 1 ? 'cartão' : 'cartões'} · {dados.disciplinas.join(' e ')}
          </p>
        )}
      </div>
    </div>
  );

  if (revisao.isPending) {
    return (
      <div className="page page--narrow">
        {cabecalho}
        <p role="status" className="muted">
          Carregando a revisão…
        </p>
      </div>
    );
  }
  if (revisao.isError || !dados) {
    return (
      <div className="page page--narrow">
        {cabecalho}
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível abrir a revisão. Tente de novo em instantes.
        </p>
      </div>
    );
  }
  const voltar = (
    <Link className={classesDoBotao('contorno')} to="/">
      Voltar ao início
    </Link>
  );
  if (total === 0) {
    return (
      <div className="page page--narrow">
        {cabecalho}
        <EstadoVazio
          icone="cards"
          titulo={dados.tem_questoes ? 'Nada para revisar hoje' : 'A revisão ainda não começou'}
          texto={
            dados.tem_questoes
              ? 'Você está em dia. A próxima revisão fica pronta amanhã às 6h.'
              : 'A revisão do dia começa quando os professores publicarem questões das aulas.'
          }
          acao={voltar}
        />
      </div>
    );
  }

  const avaliadas = dados.respostas.filter((r) => r.avaliacao).length;
  if (dados.concluida || avaliadas >= total) {
    const acertos = dados.respostas.filter((r) => r.acerto).length;
    const erradas = dados.respostas.filter((r) => !r.acerto);
    const topicos = [
      ...new Map(
        erradas.map((r) => {
          const cartao = dados.cartoes.find((c) => c.id === r.cartao);
          return [r.topico, cartao?.disciplina ?? 0] as const;
        }),
      ),
    ];
    return (
      <div className="page page--narrow">
        {cabecalho}
        <Progresso valor={total} maximo={total} rotulo={`${total} de ${total} cartões`} />
        <section className="panel result" aria-labelledby="titulo-resultado">
          <span className="result-icon">
            <Icone nome="circle-check" />
          </span>
          <h2 id="titulo-resultado" className="section-title">
            Revisão concluída
          </h2>
          <p className="result-score">
            <strong>
              {acertos} de {total}
            </strong>{' '}
            acertos
          </p>
          {topicos.length ? (
            <>
              <p className="muted">Vale perguntar ao tutor sobre:</p>
              <div className="chip-row">
                {topicos.map(([topico, disciplina]) => (
                  <Link
                    key={topico}
                    className="chip-btn"
                    to={tutorComPergunta(disciplina, `Pode me explicar melhor: ${topico}?`)}
                  >
                    <Icone nome="message-circle" />
                    {topico}
                  </Link>
                ))}
              </div>
            </>
          ) : (
            <p className="muted">Você acertou tudo.</p>
          )}
          <p className="small muted">
            A próxima revisão fica pronta amanhã às 6h. Os cartões que você achou difíceis voltam
            primeiro.
          </p>
          <div className="row row--center">
            <Link className={classesDoBotao('primario')} to="/">
              Voltar ao início
            </Link>
          </div>
        </section>
      </div>
    );
  }

  const cartao = dados.cartoes.find(
    (c) => !dados.respostas.some((r) => r.cartao === c.id && r.avaliacao),
  )!;
  const retorno = dados.respostas.find((r) => r.cartao === cartao.id);
  const indice = dados.cartoes.indexOf(cartao);

  return (
    <div className="page page--narrow">
      {cabecalho}
      <Progresso valor={avaliadas} maximo={total} rotulo={`${avaliadas} de ${total} cartões`} />
      <section className="panel quiz-card" aria-labelledby="titulo-cartao">
        <p className="quiz-topic">
          Cartão {indice + 1} de {total} · {cartao.disciplina_nome} · {cartao.topico}
        </p>
        <h2 className="fr-card-title quiz-question" id="titulo-cartao">
          {cartao.enunciado}
        </h2>
        <div className="fr-options">
          {cartao.alternativas.map((texto, i) => {
            let classe = 'fr-option';
            let marca = null;
            let estado = '';
            if (retorno && i === retorno.correta) {
              classe += ' fr-option--correct';
              marca = <Icone nome="check" />;
              estado = ', resposta correta';
            } else if (retorno && i === retorno.alternativa) {
              classe += ' fr-option--wrong';
              marca = <Icone nome="x" />;
              estado = ', sua resposta';
            }
            return (
              <button
                key={i}
                type="button"
                className={classe}
                aria-disabled={retorno ? true : undefined}
                aria-label={`${LETRAS[i]}: ${texto}${estado}`}
                disabled={responder.isPending}
                onClick={() => {
                  if (!retorno) responder.mutate({ cartao: cartao.id, alternativa: i });
                }}
              >
                <span className="fr-option-key">{LETRAS[i]}</span>
                {texto}
                {marca}
              </button>
            );
          })}
        </div>
        <div role="status">
          {retorno && (
            <div className={retorno.acerto ? 'fr-feedback' : 'fr-feedback fr-feedback--wrong'}>
              {retorno.acerto ? 'Certo.' : 'Não foi dessa vez.'} {retorno.justificativa}{' '}
              <Link to={`/trechos/${retorno.trecho.id}`}>Ver {retorno.trecho.rotulo}</Link>
            </div>
          )}
        </div>
        {(responder.isError || avaliar.isError) && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível enviar. Tente de novo.
          </p>
        )}
        {retorno && (
          <div className="rating">
            <p className="small muted" id="pergunta-avaliacao">
              Como foi lembrar disso?
            </p>
            <div className="rating-btns" role="group" aria-labelledby="pergunta-avaliacao">
              {AVALIACOES.map((a) => (
                <Botao
                  key={a.id}
                  variante="contorno"
                  disabled={avaliar.isPending}
                  onClick={() => avaliar.mutate({ cartao: cartao.id, avaliacao: a.id })}
                >
                  {a.rotulo}
                </Botao>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
