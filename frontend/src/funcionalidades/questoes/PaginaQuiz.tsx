import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Link, useParams } from 'react-router';

import {
  obterQuiz,
  reiniciarQuiz,
  responderQuestao,
  type RetornoDaQuestao,
} from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { classesDoBotao } from '../../componentes/classes';
import { EstadoVazio } from '../../componentes/EstadoVazio';
import { Icone } from '../../componentes/Icone';
import { Progresso } from '../../componentes/Progresso';
import { useDisciplina } from '../disciplinas/consultas';
import { LETRAS, tutorComPergunta } from './textos';

/**
 * O quiz de uma aula, como no protótipo: uma questão por vez, com o retorno na hora, o atalho
 * para o tutor quando o aluno erra e o resumo no fim (QUE-RF-08, QUE-RF-09, QUE-RF-10).
 */
export function PaginaQuiz() {
  const { id, materialId } = useParams();
  const disciplinaId = Number(id);
  const aula = Number(materialId);
  const clienteDeDados = useQueryClient();
  const disciplina = useDisciplina(disciplinaId).data;
  const quiz = useQuery({ queryKey: ['quiz', aula], queryFn: () => obterQuiz(aula) });
  const [novas, setNovas] = useState<RetornoDaQuestao[]>([]);
  const [mostrando, setMostrando] = useState<number | null>(null);
  const responder = useMutation({
    mutationFn: ({ questao, alternativa }: { questao: number; alternativa: number }) =>
      responderQuestao(questao, alternativa),
    onSuccess: (retorno) => {
      setNovas((atuais) => [...atuais, retorno]);
      setMostrando(retorno.questao);
    },
  });
  const reiniciar = useMutation({
    mutationFn: () => reiniciarQuiz(aula),
    onSuccess: async () => {
      setNovas([]);
      setMostrando(null);
      await clienteDeDados.invalidateQueries({ queryKey: ['quiz', aula] });
    },
  });

  const dados = quiz.data;
  const titulo = dados ? `Quiz da Aula ${dados.aula_numero}` : 'Quiz';
  const cabecalho = (
    <>
      <nav className="breadcrumb" aria-label="Você está em">
        <Link to={`/disciplinas/${disciplinaId}`}>{disciplina?.nome ?? 'Disciplina'}</Link>
        <Icone nome="chevron-right" />
        <span aria-current="page">{titulo}</span>
      </nav>
      <div className="page-head">
        <div>
          <h1 className="page-title">{titulo}</h1>
          {dados && (
            <p className="page-sub">
              {disciplina ? `${disciplina.nome} · ` : ''}
              {dados.aula_titulo} · questões aprovadas pelo professor
            </p>
          )}
        </div>
      </div>
    </>
  );

  if (quiz.isPending) {
    return (
      <div className="page page--narrow">
        {cabecalho}
        <p role="status" className="muted">
          Carregando o quiz…
        </p>
      </div>
    );
  }
  if (quiz.isError || !dados) {
    return (
      <div className="page page--narrow">
        {cabecalho}
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível abrir o quiz. Tente de novo em instantes.
        </p>
      </div>
    );
  }
  const voltar = (
    <Link className={classesDoBotao('contorno')} to={`/disciplinas/${disciplinaId}`}>
      Voltar para a disciplina
    </Link>
  );
  if (dados.pausado || dados.questoes.length === 0) {
    return (
      <div className="page page--narrow">
        {cabecalho}
        <EstadoVazio
          icone={dados.pausado ? 'lock' : 'list-check'}
          titulo={
            dados.pausado ? 'O quiz está pausado durante a prova' : 'Nenhuma questão aprovada ainda'
          }
          texto={
            dados.pausado
              ? 'O professor pausou o tutor e os quizzes desta disciplina. Volte depois da prova.'
              : 'Quando o professor aprovar questões desta aula, elas aparecem aqui.'
          }
          acao={voltar}
        />
      </div>
    );
  }

  const respondidas = [
    ...dados.respostas,
    ...novas.filter((n) => !dados.respostas.some((r) => r.questao === n.questao)),
  ];
  const total = dados.questoes.length;
  const indice =
    mostrando !== null ? dados.questoes.findIndex((q) => q.id === mostrando) : respondidas.length;
  const terminou = mostrando === null && respondidas.length >= total;
  const acertos = respondidas.filter((r) => r.acerto).length;

  if (terminou) {
    const topicos = [...new Set(respondidas.filter((r) => !r.acerto).map((r) => r.topico))];
    return (
      <div className="page page--narrow">
        {cabecalho}
        <Progresso valor={total} maximo={total} rotulo={`${total} de ${total} questões`} />
        <section className="panel result" aria-labelledby="titulo-resultado">
          <span className="result-icon">
            <Icone nome="circle-check" />
          </span>
          <h2 id="titulo-resultado" className="section-title">
            Quiz concluído
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
                {topicos.map((topico) => (
                  <Link
                    key={topico}
                    className="chip-btn"
                    to={tutorComPergunta(disciplinaId, `Pode me explicar melhor: ${topico}?`)}
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
          <div className="row row--center">
            <Link className={classesDoBotao('primario')} to={`/disciplinas/${disciplinaId}`}>
              Voltar para a disciplina
            </Link>
            <Botao
              variante="contorno"
              disabled={reiniciar.isPending}
              onClick={() => reiniciar.mutate()}
            >
              Refazer quiz
            </Botao>
          </div>
        </section>
      </div>
    );
  }

  const questao = dados.questoes[indice]!;
  const retorno = respondidas.find((r) => r.questao === questao.id);
  const contados = respondidas.length;
  const ultima = indice === total - 1;

  return (
    <div className="page page--narrow">
      {cabecalho}
      <Progresso valor={contados} maximo={total} rotulo={`${contados} de ${total} questões`} />
      <section className="panel quiz-card" aria-labelledby="titulo-questao">
        <p className="quiz-topic">
          Questão {indice + 1} de {total} · {questao.topico}
        </p>
        <h2 className="fr-card-title quiz-question" id="titulo-questao">
          {questao.enunciado}
        </h2>
        <div className="fr-options">
          {questao.alternativas.map((texto, i) => {
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
                  if (!retorno) responder.mutate({ questao: questao.id, alternativa: i });
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
        {responder.isError && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível enviar a resposta. Tente de novo.
          </p>
        )}
        {retorno && (
          <div className="row row--end">
            {!retorno.acerto && (
              <Link
                className={classesDoBotao('contorno', true)}
                to={tutorComPergunta(
                  disciplinaId,
                  `Errei esta questão do quiz e quero entender: "${questao.enunciado}"`,
                )}
              >
                <Icone nome="message-circle" />
                Perguntar ao tutor sobre isso
              </Link>
            )}
            <Botao pequeno onClick={() => setMostrando(null)}>
              {ultima || contados >= total ? 'Ver resultado' : 'Próxima'}
            </Botao>
          </div>
        )}
      </section>
    </div>
  );
}
