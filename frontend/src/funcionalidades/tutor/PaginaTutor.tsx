import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router';

import {
  avaliarResposta,
  enviarDuvida,
  ErroDaApi,
  listarMinhasDuvidas,
  perguntarAoTutor,
  previaDaDuvida,
  type AvaliacaoDaResposta,
  type CitacaoDoTutor,
  type EventoDoTutor,
  type MensagemDoTutor,
  type TipoDeMensagem,
} from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { Icone } from '../../componentes/Icone';
import { Modal } from '../../componentes/Modal';
import { Selo } from '../../componentes/Selo';
import { useDisciplina, useDisciplinas } from '../disciplinas/consultas';
import { useTutor } from './consultas';

const LIMITE_DE_CARACTERES = 1000;

/** Uma mensagem como a tela mostra: a guardada no servidor ou a desta visita. */
type MensagemNaTela = {
  chave: string;
  /** O id no servidor: a resposta nova só o recebe no fim. */
  id?: number;
  avaliacao?: AvaliacaoDaResposta;
  autor: 'aluno' | 'tutor';
  texto: string;
  tipo?: TipoDeMensagem;
  citacoes: CitacaoDoTutor[];
  respondendo?: boolean;
};

function daConversaGuardada(mensagem: MensagemDoTutor): MensagemNaTela {
  return {
    chave: `guardada-${mensagem.id}`,
    id: mensagem.id,
    avaliacao: mensagem.avaliacao,
    autor: mensagem.autor,
    texto: mensagem.texto,
    tipo: mensagem.tipo,
    citacoes: mensagem.citacoes,
  };
}

function mensagemDeErro(erro: unknown): string {
  if (erro instanceof ErroDaApi) {
    const corpo = erro.corpo as { detail?: string; texto?: string[] } | undefined;
    if (corpo?.detail) return corpo.detail;
    if (corpo?.texto?.[0]) return corpo.texto[0];
  }
  return 'O tutor não conseguiu responder agora. Tente de novo em instantes.';
}

function Citacoes({ citacoes }: { citacoes: CitacaoDoTutor[] }) {
  if (citacoes.length === 0) return null;
  return (
    <ul aria-label="Fontes da resposta" className="row">
      {citacoes.map((citacao) => (
        <li key={citacao.ordem}>
          <Link to={`/trechos/${citacao.trecho_id}`} className="fr-cite">
            <Icone nome="file-text" />[{citacao.ordem}] {citacao.rotulo}
            <span className="sr-only"> (abre a página com o trecho destacado)</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

const OPCOES_DE_AVALIACAO = [
  { valor: 'util', rotulo: 'Útil', icone: 'check' },
  { valor: 'nao_util', rotulo: 'Não útil', icone: 'x' },
  { valor: 'incorreta', rotulo: 'Incorreta', icone: 'alert-triangle' },
] as const;

const OBRIGADO = 'Obrigado. Respostas marcadas como incorretas vão para revisão da equipe.';

/** Útil, não útil ou incorreta; tocar de novo na marcada desfaz (TUT-RF-09). */
function AvaliarResposta({
  mensagemId,
  inicial,
}: {
  mensagemId: number;
  inicial: AvaliacaoDaResposta;
}) {
  const [atual, setAtual] = useState<AvaliacaoDaResposta>(inicial);
  const [aviso, setAviso] = useState('');
  const [salvando, setSalvando] = useState(false);

  async function marcar(valor: AvaliacaoDaResposta) {
    const nova = atual === valor ? '' : valor;
    setSalvando(true);
    try {
      await avaliarResposta(mensagemId, nova);
      setAtual(nova);
      setAviso(nova === 'incorreta' ? OBRIGADO : '');
    } catch {
      setAviso('Não foi possível registrar a avaliação. Tente de novo.');
    } finally {
      setSalvando(false);
    }
  }

  return (
    <>
      <div role="group" aria-label="Avaliar resposta" className="answer-tools">
        {OPCOES_DE_AVALIACAO.map((opcao) => (
          <button
            key={opcao.valor}
            type="button"
            className="tool-btn"
            aria-pressed={atual === opcao.valor}
            disabled={salvando}
            onClick={() => void marcar(opcao.valor)}
          >
            <Icone nome={opcao.icone} />
            {opcao.rotulo}
          </button>
        ))}
      </div>
      <p role="status" className="small muted">
        {aviso}
      </p>
    </>
  );
}

type StatusDaDuvida = 'aberta' | 'respondida';

/** A nota da dúvida enviada ao professor, com o status dela (DUV-RF-08). */
function DuvidaEnviada({ status }: { status: StatusDaDuvida }) {
  return (
    <div>
      <p className="bubble-note">
        <Icone nome="circle-check" />
        Dúvida enviada ao professor, sem o seu nome.
      </p>
      <p className="small muted">
        {status === 'respondida'
          ? 'O professor marcou como respondida em aula.'
          : 'Aguardando o professor tratar em aula.'}
      </p>
    </div>
  );
}

type DuvidaEmPrevia = { mensagemId: number; texto: string };

/** A pré-visualização da dúvida: o texto exato e o aviso de anonimato antes de enviar (DUV-RF-02). */
function PreviaDaDuvida({
  previa,
  aoFechar,
  aoEnviar,
  enviando,
  erro,
}: {
  previa: DuvidaEmPrevia;
  aoFechar: () => void;
  aoEnviar: () => void;
  enviando: boolean;
  erro: string;
}) {
  return (
    <Modal
      titulo="Enviar dúvida ao professor"
      subtitulo="O professor vai ler exatamente este texto"
      aoFechar={aoFechar}
    >
      <div className="stack">
        <blockquote className="panel trecho-texto">{previa.texto}</blockquote>
        <p className="privacy-note">
          <Icone nome="lock" />O professor não verá o seu nome, o seu e-mail nem o horário do envio.
          Em turmas pequenas, o jeito de escrever ainda pode identificar você.
        </p>
        {erro && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            {erro}
          </p>
        )}
        <div className="row row--end">
          <Botao variante="contorno" onClick={aoFechar} data-foco-inicial>
            Cancelar
          </Botao>
          <Botao onClick={aoEnviar} disabled={enviando}>
            Enviar ao professor
          </Botao>
        </div>
      </div>
    </Modal>
  );
}

function Mensagem({
  mensagem,
  duvida,
  aoPedirDuvida,
}: {
  mensagem: MensagemNaTela;
  duvida?: StatusDaDuvida;
  aoPedirDuvida: (mensagemId: number) => void;
}) {
  if (mensagem.autor === 'aluno') {
    return (
      <li className="fr-bubble fr-bubble--student">
        <span className="sr-only">Você: </span>
        <p className="trecho-texto">{mensagem.texto}</p>
      </li>
    );
  }
  const erro = mensagem.tipo === 'erro';
  if (mensagem.respondendo && !mensagem.texto) {
    return (
      <li className="fr-bubble fr-bubble--tutor is-typing">
        <span className="spin">
          <Icone nome="loader-2" />
        </span>
        Procurando no material…
      </li>
    );
  }
  return (
    <li className={erro ? 'fr-bubble fr-bubble--tutor bolha-erro' : 'fr-bubble fr-bubble--tutor'}>
      <span className="sr-only">Tutor: </span>
      {mensagem.tipo === 'pistas' && (
        <span className="bubble-tag">
          <Icone nome="bulb" />
          Modo pistas
        </span>
      )}
      <p className="trecho-texto">{mensagem.texto}</p>
      <Citacoes citacoes={mensagem.citacoes} />
      {duvida && <DuvidaEnviada status={duvida} />}
      {!duvida && mensagem.tipo === 'nao_encontrado' && mensagem.id !== undefined && (
        <div className="fr-bubble-actions">
          <Botao variante="contorno" pequeno onClick={() => aoPedirDuvida(mensagem.id as number)}>
            Enviar dúvida ao professor
          </Botao>
        </div>
      )}
      {mensagem.id !== undefined &&
        (mensagem.tipo === 'resposta' || mensagem.tipo === 'pistas') && (
          <AvaliarResposta mensagemId={mensagem.id} inicial={mensagem.avaliacao ?? ''} />
        )}
    </li>
  );
}

/** O texto do professor e o resumo das regras do tutor, num modal como no protótipo (TUT-RF-10). */
function PoliticaDeUso({
  politica,
  modoPistas,
  professor,
}: {
  politica: string;
  modoPistas: boolean;
  professor?: string;
}) {
  const [aberta, setAberta] = useState(false);
  return (
    <>
      <button type="button" className="link-btn" onClick={() => setAberta(true)}>
        <Icone nome="shield-lock" />
        Política de uso de IA
      </button>
      {aberta && (
        <Modal
          titulo="Política de uso de IA"
          subtitulo={professor ? `Definida por Prof. ${professor}` : undefined}
          aoFechar={() => setAberta(false)}
        >
          <p className="policy-text trecho-texto">
            {politica.trim() || 'O professor ainda não escreveu uma política para esta disciplina.'}
          </p>
          <h3 className="strong">Regras do tutor</h3>
          <ul className="policy-list">
            <li>
              <Icone nome="file-text" />
              Responde só com o material desta disciplina, sempre com a página citada.
            </li>
            <li>
              <Icone nome="bulb" />
              {modoPistas
                ? 'Em exercícios, dá pistas em vez da resposta pronta.'
                : 'O modo pistas está desligado nesta disciplina.'}
            </li>
            <li>
              <Icone nome="lock" />
              Fica pausado durante as provas.
            </li>
          </ul>
        </Modal>
      )}
    </>
  );
}

/** A escolha da disciplina, como no protótipo: só as que têm material pronto para o tutor. */
function EscolhaDaDisciplina({ disciplinaId }: { disciplinaId: number }) {
  const navegar = useNavigate();
  const comTutor = useDisciplinas('', 'com-tutor').data ?? [];
  const atual = useDisciplina(disciplinaId).data;
  const opcoes =
    comTutor.some((d) => d.id === disciplinaId) || !atual ? comTutor : [atual, ...comTutor];
  if (opcoes.length < 2) return null;
  return (
    <div className="tutor-select">
      <label htmlFor="tutor-disciplina" className="fr-label">
        Disciplina
      </label>
      <span className="fr-select-wrap">
        <select
          id="tutor-disciplina"
          className="fr-select"
          value={disciplinaId}
          onChange={(evento) => navegar(`/disciplinas/${evento.target.value}/tutor`)}
        >
          {opcoes.map((d) => (
            <option key={d.id} value={d.id}>
              {d.nome}
            </option>
          ))}
        </select>
      </span>
    </div>
  );
}

export function PaginaTutor() {
  const disciplinaId = Number(useParams().id);
  const tutor = useTutor(disciplinaId);
  const minhasDuvidas = useQuery({
    queryKey: ['minhas-duvidas', disciplinaId],
    queryFn: () => listarMinhasDuvidas(disciplinaId),
  });
  const clienteDeDados = useQueryClient();
  const [previa, setPrevia] = useState<DuvidaEmPrevia | null>(null);
  const [erroDaDuvida, setErroDaDuvida] = useState('');
  const [enviandoDuvida, setEnviandoDuvida] = useState(false);

  async function pedirDuvida(mensagemId: number) {
    setErroDaDuvida('');
    try {
      setPrevia({ mensagemId, texto: await previaDaDuvida(mensagemId) });
    } catch (falha) {
      setErro(mensagemDeErro(falha));
    }
  }

  async function confirmarDuvida() {
    if (!previa) return;
    setEnviandoDuvida(true);
    try {
      await enviarDuvida(previa.mensagemId);
      setPrevia(null);
      setAnuncio('Dúvida enviada ao professor, sem o seu nome.');
      await clienteDeDados.invalidateQueries({ queryKey: ['minhas-duvidas', disciplinaId] });
    } catch (falha) {
      setErroDaDuvida(mensagemDeErro(falha));
    } finally {
      setEnviandoDuvida(false);
    }
  }

  const statusDasDuvidas = new Map(
    (minhasDuvidas.data ?? []).map((duvida) => [duvida.mensagem_id, duvida.status]),
  );
  const disciplina = useDisciplina(disciplinaId).data;
  const [novas, setNovas] = useState<MensagemNaTela[]>([]);
  const [pergunta, setPergunta] = useState('');
  const [erro, setErro] = useState('');
  const [anuncio, setAnuncio] = useState('');
  const [usadasNestaVisita, setUsadasNestaVisita] = useState(0);
  const [enviando, setEnviando] = useState(false);
  const campo = useRef<HTMLInputElement>(null);
  const perguntasEnviadas = useRef(0);

  const titulo = disciplina ? `Tutor de ${disciplina.nome}` : 'Tutor';
  const mensagens = [...(tutor.data?.mensagens.map(daConversaGuardada) ?? []), ...novas];

  function atualizarResposta(chave: string, mudar: (m: MensagemNaTela) => MensagemNaTela) {
    setNovas((atuais) => atuais.map((m) => (m.chave === chave ? mudar(m) : m)));
  }

  async function perguntar(texto: string) {
    const limpo = texto.trim();
    if (enviando) return;
    if (!limpo) {
      setErro('Escreva uma pergunta antes de enviar.');
      campo.current?.focus();
      return;
    }
    perguntasEnviadas.current += 1;
    const chave = `nova-${perguntasEnviadas.current}`;
    const chaveDaResposta = `resposta-${chave}`;
    setErro('');
    setPergunta('');
    setEnviando(true);
    setAnuncio('O tutor está respondendo…');
    setNovas((atuais) => [
      ...atuais,
      { chave: `pergunta-${chave}`, autor: 'aluno', texto: limpo, citacoes: [] },
      { chave: chaveDaResposta, autor: 'tutor', texto: '', citacoes: [], respondendo: true },
    ]);

    let textoDaResposta = '';
    const aoReceber = (evento: EventoDoTutor) => {
      if (evento.evento === 'inicio') {
        setUsadasNestaVisita((usadas) => usadas + 1);
      } else if (evento.evento === 'texto') {
        textoDaResposta += evento.dados.texto;
        const parcial = textoDaResposta;
        atualizarResposta(chaveDaResposta, (m) => ({ ...m, texto: parcial }));
      } else if (evento.evento === 'citacao') {
        const citacao = evento.dados;
        atualizarResposta(chaveDaResposta, (m) => ({ ...m, citacoes: [...m.citacoes, citacao] }));
      } else if (evento.evento === 'fim') {
        const tipo = evento.dados.tipo;
        const id = evento.dados.mensagem_id;
        atualizarResposta(chaveDaResposta, (m) => ({ ...m, id, tipo, respondendo: false }));
        setAnuncio(`O tutor respondeu: ${textoDaResposta.trim()}`);
      } else {
        const aviso = evento.dados.mensagem;
        atualizarResposta(chaveDaResposta, (m) => ({
          ...m,
          texto: aviso,
          tipo: 'erro',
          citacoes: [],
          respondendo: false,
        }));
        setAnuncio(aviso);
      }
    };

    try {
      await perguntarAoTutor(disciplinaId, limpo, aoReceber);
    } catch (falha) {
      // Recusada antes da resposta (limite, prova, provedor fora do ar): nada foi guardado.
      setNovas((atuais) => atuais.filter((m) => !m.chave.endsWith(chave)));
      setPergunta(limpo);
      setErro(mensagemDeErro(falha));
      setAnuncio('');
      if (falha instanceof ErroDaApi && falha.status === 423) {
        // O professor ligou o modo prova: a tela passa a mostrar o aviso de pausa.
        void tutor.refetch().then(() => {
          setNovas([]);
          setUsadasNestaVisita(0);
        });
      }
    } finally {
      setEnviando(false);
      campo.current?.focus();
    }
  }

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    void perguntar(pergunta);
  }

  return (
    <div className="page page--tutor">
      <div className="tutor-head">
        <div>
          <h1 className="page-title">{titulo}</h1>
          <p className="page-sub">
            Respostas só com o material
            {disciplina ? ` do Prof. ${disciplina.professor_nome}` : ' da disciplina'}, sempre com a
            página citada.
          </p>
        </div>
        <EscolhaDaDisciplina disciplinaId={disciplinaId} />
      </div>

      {tutor.isPending && (
        <p role="status" className="muted">
          Carregando o tutor…
        </p>
      )}
      {tutor.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível abrir o tutor desta disciplina. Tente de novo em instantes.
        </p>
      )}

      {tutor.data && (
        <>
          <div className="tutor-status">
            {tutor.data.modo_pistas && (
              <Selo tom="destaque" pilula icone="bulb">
                Modo pistas ligado
              </Selo>
            )}
            {tutor.data.pausado && (
              <Selo tom="perigo" icone="lock">
                Modo prova
              </Selo>
            )}
            <PoliticaDeUso
              politica={tutor.data.politica}
              modoPistas={tutor.data.modo_pistas}
              professor={disciplina?.professor_nome}
            />
          </div>

          {tutor.data.pausado ? (
            <section className="panel tutor-locked" aria-labelledby="titulo-pausa">
              <span className="empty-state-icon">
                <Icone nome="lock" />
              </span>
              <h2 id="titulo-pausa" className="section-title">
                O tutor está pausado durante a prova
              </h2>
              <p className="muted">
                O professor ativou o modo prova nesta disciplina. O tutor volta a responder quando a
                prova terminar.
              </p>
            </section>
          ) : (
            <>
              {mensagens.length === 0 ? (
                <section className="tutor-log" aria-labelledby="titulo-vazio">
                  <div className="tutor-empty">
                    <span className="empty-state-icon">
                      <Icone nome="message-circle" />
                    </span>
                    <h2 id="titulo-vazio" className="section-title">
                      Pergunte sobre {disciplina?.nome ?? 'a disciplina'}
                    </h2>
                    <p className="muted">
                      O tutor só usa o material publicado pelo professor e mostra a página de onde
                      tirou cada resposta. Quando o assunto não estiver no material, ele avisa, e
                      você pode mandar a dúvida para o professor sem se identificar.
                    </p>
                  </div>
                </section>
              ) : (
                <ol aria-label="Conversa com o tutor" className="tutor-log">
                  {mensagens.map((mensagem) => (
                    <Mensagem
                      key={mensagem.chave}
                      mensagem={mensagem}
                      aoPedirDuvida={(id) => void pedirDuvida(id)}
                      duvida={
                        mensagem.id === undefined ? undefined : statusDasDuvidas.get(mensagem.id)
                      }
                    />
                  ))}
                </ol>
              )}

              <div className="composer">
                {mensagens.length === 0 && tutor.data.sugestoes.length > 0 && (
                  <ul aria-label="Sugestões de pergunta" className="suggestions">
                    {tutor.data.sugestoes.map((sugestao) => (
                      <li key={sugestao}>
                        <button
                          type="button"
                          className="chip-btn"
                          onClick={() => void perguntar(sugestao)}
                        >
                          {sugestao}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
                <form onSubmit={aoEnviar} noValidate className="composer-form">
                  <label htmlFor="pergunta" className="sr-only">
                    Sua pergunta
                  </label>
                  <input
                    id="pergunta"
                    ref={campo}
                    className="fr-input"
                    value={pergunta}
                    onChange={(evento) => {
                      setPergunta(evento.target.value);
                      setErro('');
                    }}
                    maxLength={LIMITE_DE_CARACTERES}
                    autoComplete="off"
                    placeholder={`Pergunte sobre ${disciplina?.nome ?? 'a disciplina'}`}
                  />
                  <Botao
                    type="submit"
                    className="composer-send"
                    icone="send"
                    aria-label="Enviar pergunta"
                    disabled={enviando}
                  />
                </form>
                {erro && (
                  <p role="alert" className="composer-error">
                    {erro}
                  </p>
                )}
                <p className="small muted composer-meta">
                  <span>
                    {tutor.data.uso.usadas + usadasNestaVisita} de {tutor.data.uso.limite} perguntas
                    hoje
                  </span>{' '}
                  · As dúvidas chegam ao professor sem o seu nome.
                </p>
              </div>
            </>
          )}
        </>
      )}

      {previa && (
        <PreviaDaDuvida
          previa={previa}
          aoFechar={() => setPrevia(null)}
          aoEnviar={() => void confirmarDuvida()}
          enviando={enviandoDuvida}
          erro={erroDaDuvida}
        />
      )}

      {/* A resposta aparece aos poucos na conversa; o leitor de tela recebe só a versão final. */}
      <p data-testid="anuncio-do-tutor" aria-live="polite" className="sr-only">
        {anuncio}
      </p>
    </div>
  );
}
