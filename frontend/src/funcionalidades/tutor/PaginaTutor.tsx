import { useQuery } from '@tanstack/react-query';
import { useRef, useState, type FormEvent } from 'react';
import { useParams } from 'react-router';

import {
  avaliarResposta,
  ErroDaApi,
  listarMinhasDuvidas,
  perguntarAoTutor,
  type AvaliacaoDaResposta,
  type CitacaoDoTutor,
  type EventoDoTutor,
  type MensagemDoTutor,
  type TipoDeMensagem,
} from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { useDisciplinas } from '../disciplinas/consultas';
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
    <ul aria-label="Fontes da resposta" className="mt-2 flex flex-wrap gap-2">
      {citacoes.map((citacao) => (
        <li key={citacao.ordem}>
          <a
            href={`/api/materiais/${citacao.material_id}/arquivo?pagina=${citacao.pagina}#page=${citacao.pagina}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex min-h-12 items-center rounded-lg border border-line-control bg-surface px-3 text-sm font-bold text-ink underline"
          >
            [{citacao.ordem}] {citacao.rotulo}
            <span className="sr-only"> (abre o material em nova aba)</span>
          </a>
        </li>
      ))}
    </ul>
  );
}

const OPCOES_DE_AVALIACAO = [
  { valor: 'util', rotulo: 'Útil' },
  { valor: 'nao_util', rotulo: 'Não útil' },
  { valor: 'incorreta', rotulo: 'Incorreta' },
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
    <div className="mt-2">
      <div role="group" aria-label="Avaliar resposta" className="flex flex-wrap gap-2">
        {OPCOES_DE_AVALIACAO.map((opcao) => (
          <Botao
            key={opcao.valor}
            variante="secundario"
            aria-pressed={atual === opcao.valor}
            disabled={salvando}
            onClick={() => void marcar(opcao.valor)}
          >
            {opcao.rotulo}
          </Botao>
        ))}
      </div>
      <p role="status" className="mt-1 text-sm text-ink-muted">
        {aviso}
      </p>
    </div>
  );
}

type StatusDaDuvida = 'aberta' | 'respondida';

/** A nota da dúvida enviada ao professor, com o status dela (DUV-RF-08). */
function DuvidaEnviada({ status }: { status: StatusDaDuvida }) {
  return (
    <div className="mt-2 text-sm">
      <p className="font-bold text-success-text">Dúvida enviada ao professor, sem o seu nome.</p>
      <p className="text-ink-muted">
        {status === 'respondida'
          ? 'O professor marcou como respondida em aula.'
          : 'Aguardando o professor tratar em aula.'}
      </p>
    </div>
  );
}

function Mensagem({ mensagem, duvida }: { mensagem: MensagemNaTela; duvida?: StatusDaDuvida }) {
  if (mensagem.autor === 'aluno') {
    return (
      <li className="ml-auto max-w-[85%] rounded-lg bg-accent-soft p-3 text-ink">
        <span className="sr-only">Você: </span>
        <p className="whitespace-pre-wrap">{mensagem.texto}</p>
      </li>
    );
  }
  const erro = mensagem.tipo === 'erro';
  return (
    <li
      className={`max-w-[85%] rounded-lg border p-3 ${
        erro ? 'border-danger bg-danger-soft text-danger-text' : 'border-line bg-surface text-ink'
      }`}
    >
      <span className="sr-only">Tutor: </span>
      {mensagem.tipo === 'pistas' && (
        <p className="mb-1 text-xs font-bold uppercase text-accent">Modo pistas</p>
      )}
      <p className="whitespace-pre-wrap">
        {mensagem.texto || (mensagem.respondendo ? 'O tutor está respondendo…' : '')}
      </p>
      <Citacoes citacoes={mensagem.citacoes} />
      {duvida && <DuvidaEnviada status={duvida} />}
      {mensagem.id !== undefined &&
        (mensagem.tipo === 'resposta' || mensagem.tipo === 'pistas') && (
          <AvaliarResposta mensagemId={mensagem.id} inicial={mensagem.avaliacao ?? ''} />
        )}
    </li>
  );
}

/** O texto do professor e o resumo das regras do tutor, abertos por um botão (TUT-RF-10). */
function PoliticaDeUso({ politica, modoPistas }: { politica: string; modoPistas: boolean }) {
  const [aberta, setAberta] = useState(false);
  return (
    <div>
      <Botao
        variante="secundario"
        aria-expanded={aberta}
        aria-controls="politica-de-uso"
        onClick={() => setAberta((valor) => !valor)}
      >
        Política de uso de IA
      </Botao>
      {aberta && (
        <section
          id="politica-de-uso"
          aria-labelledby="titulo-politica"
          className="mt-2 rounded-lg border border-line bg-surface p-4 text-ink"
        >
          <h2 id="titulo-politica" className="text-lg font-bold">
            Política de uso de IA
          </h2>
          <p className="mt-1 whitespace-pre-wrap">
            {politica.trim() || 'O professor ainda não escreveu uma política para esta disciplina.'}
          </p>
          <h3 className="mt-3 font-bold">Regras do tutor</h3>
          <ul className="list-disc pl-5">
            <li>Responde só com o material desta disciplina, sempre com a página citada.</li>
            <li>
              {modoPistas
                ? 'Em exercícios, dá pistas em vez da resposta pronta.'
                : 'O modo pistas está desligado nesta disciplina.'}
            </li>
            <li>Fica pausado durante as provas.</li>
          </ul>
        </section>
      )}
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
  const statusDasDuvidas = new Map(
    (minhasDuvidas.data ?? []).map((duvida) => [duvida.mensagem_id, duvida.status]),
  );
  const disciplina = useDisciplinas('').data?.find((d) => d.id === disciplinaId);
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
    <main id="conteudo" className="mx-auto flex max-w-3xl flex-col gap-4 p-4">
      <div>
        <h1 className="text-2xl font-extrabold text-ink">{titulo}</h1>
        <p className="text-ink-muted">
          Respostas só com o material da disciplina, sempre com a página citada.
        </p>
      </div>

      {tutor.isPending && (
        <p role="status" className="text-ink-muted">
          Carregando o tutor…
        </p>
      )}
      {tutor.isError && (
        <p role="alert" className="text-danger-text">
          Não foi possível abrir o tutor desta disciplina. Tente de novo em instantes.
        </p>
      )}

      {tutor.data && (
        <>
          <PoliticaDeUso politica={tutor.data.politica} modoPistas={tutor.data.modo_pistas} />
          {tutor.data.modo_pistas && (
            <p className="w-fit rounded-full bg-accent-soft px-3 py-1 text-sm font-bold text-ink">
              Modo pistas ligado
            </p>
          )}

          {tutor.data.pausado ? (
            <section
              aria-labelledby="titulo-pausa"
              className="rounded-lg border border-line bg-surface p-4 text-ink"
            >
              <h2 id="titulo-pausa" className="text-lg font-bold">
                O tutor está pausado durante a prova
              </h2>
              <p className="text-ink-muted">
                O professor ativou o modo prova nesta disciplina. O tutor volta a responder quando a
                prova terminar.
              </p>
            </section>
          ) : (
            <>
              {mensagens.length === 0 ? (
                <section aria-labelledby="titulo-vazio" className="text-ink">
                  <h2 id="titulo-vazio" className="text-lg font-bold">
                    Pergunte sobre {disciplina?.nome ?? 'a disciplina'}
                  </h2>
                  <p className="text-ink-muted">
                    O tutor só usa o material publicado pelo professor e mostra a página de onde
                    tirou cada resposta.
                  </p>
                  {tutor.data.sugestoes.length > 0 && (
                    <ul aria-label="Sugestões de pergunta" className="mt-3 flex flex-wrap gap-2">
                      {tutor.data.sugestoes.map((sugestao) => (
                        <li key={sugestao}>
                          <Botao variante="secundario" onClick={() => void perguntar(sugestao)}>
                            {sugestao}
                          </Botao>
                        </li>
                      ))}
                    </ul>
                  )}
                </section>
              ) : (
                <ol aria-label="Conversa com o tutor" className="flex flex-col gap-3">
                  {mensagens.map((mensagem) => (
                    <Mensagem
                      key={mensagem.chave}
                      mensagem={mensagem}
                      duvida={
                        mensagem.id === undefined ? undefined : statusDasDuvidas.get(mensagem.id)
                      }
                    />
                  ))}
                </ol>
              )}

              <form onSubmit={aoEnviar} noValidate className="flex flex-col gap-2">
                <label htmlFor="pergunta" className="text-sm font-bold text-ink">
                  Sua pergunta
                </label>
                <div className="flex gap-2">
                  <input
                    id="pergunta"
                    ref={campo}
                    value={pergunta}
                    onChange={(evento) => {
                      setPergunta(evento.target.value);
                      setErro('');
                    }}
                    maxLength={LIMITE_DE_CARACTERES}
                    autoComplete="off"
                    placeholder={`Pergunte sobre ${disciplina?.nome ?? 'a disciplina'}`}
                    className="min-h-12 min-w-0 flex-1 rounded-lg border border-line-control bg-surface px-3 text-ink"
                  />
                  <Botao type="submit" disabled={enviando}>
                    Enviar pergunta
                  </Botao>
                </div>
                {erro && (
                  <p role="alert" className="text-danger-text">
                    {erro}
                  </p>
                )}
                <p className="text-sm text-ink-muted">
                  {tutor.data.uso.usadas + usadasNestaVisita} de {tutor.data.uso.limite} perguntas
                  hoje
                </p>
              </form>
            </>
          )}
        </>
      )}

      {/* A resposta aparece aos poucos na conversa; o leitor de tela recebe só a versão final. */}
      <p data-testid="anuncio-do-tutor" aria-live="polite" className="sr-only">
        {anuncio}
      </p>
    </main>
  );
}
