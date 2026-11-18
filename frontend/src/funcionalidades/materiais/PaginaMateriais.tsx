import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRef, useState, type DragEvent, type FormEvent } from 'react';
import { Navigate, useParams } from 'react-router';

import {
  enviarMaterial,
  enviarNovaVersao,
  ErroDaApi,
  listarMateriaisDoProfessor,
  retirarMaterial,
  type MaterialDoProfessor,
} from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { Icone } from '../../componentes/Icone';
import { Progresso } from '../../componentes/Progresso';
import { Selo, type TomDoSelo } from '../../componentes/Selo';
import { useEu } from '../contas/sessao';
import { useDisciplina } from '../disciplinas/consultas';

const NAO_E_PDF = 'Envie um arquivo PDF. Slides podem ser exportados como PDF.';
/** Enquanto algum material processa, a lista se atualiza sozinha nesse intervalo. */
const INTERVALO_DE_ATUALIZACAO_EM_MS = 2000;
/** As etapas do processamento, na ordem, para a barra de progresso (MAT-RF-03). */
const ETAPAS: MaterialDoProfessor['etapa'][] = [
  'enviando',
  'lendo',
  'dividindo',
  'vetorizando',
  'pronto',
];
const TONS: Record<MaterialDoProfessor['status'], TomDoSelo> = {
  processando: 'neutro',
  pronto: 'sucesso',
  atencao: 'atencao',
  erro: 'perigo',
  retirado: 'neutro',
  substituido: 'neutro',
};
const DATA = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
});

function ehPdf(arquivo: File): boolean {
  return arquivo.type === 'application/pdf' || arquivo.name.toLowerCase().endsWith('.pdf');
}

function motivo(erro: unknown): string {
  const corpo = erro instanceof ErroDaApi ? (erro.corpo as Record<string, string[]>) : undefined;
  const primeiro = corpo && Object.values(corpo).find((valor) => Array.isArray(valor));
  return primeiro?.[0] ?? 'Não foi possível enviar o material. Tente de novo.';
}

/** "aula_05-pilhas.pdf" vira "Aula 05 pilhas": um ponto de partida para o título da aula. */
function tituloPeloArquivo(nome: string): string {
  const titulo = nome
    .replace(/\.pdf$/i, '')
    .replace(/[_-]+/g, ' ')
    .trim();
  return titulo ? titulo.charAt(0).toUpperCase() + titulo.slice(1) : '';
}

function SituacaoDoMaterial({ material }: { material: MaterialDoProfessor }) {
  if (material.status === 'processando') {
    const passo = Math.max(0, ETAPAS.indexOf(material.etapa)) + 1;
    return (
      <span className="material-status material-status--processing">
        <Progresso
          valor={passo}
          maximo={ETAPAS.length}
          rotulo={material.etapa_rotulo}
          rotuloAcessivel={`Processando a aula ${material.aula_numero}`}
        />
      </span>
    );
  }
  return (
    <span className="material-status">
      <Selo tom={TONS[material.status]} icone={material.status === 'pronto' ? 'check' : undefined}>
        {material.status_rotulo}
      </Selo>
      {material.paginas_sem_texto.length > 0 && (
        <span className="small muted">
          Páginas sem texto: {material.paginas_sem_texto.join(', ')}
        </span>
      )}
      {material.erro && <span className="small muted">{material.erro}</span>}
    </span>
  );
}

function LinhaDeMaterial({
  material,
  aoRetirar,
  aoEnviarVersao,
  ocupado,
}: {
  material: MaterialDoProfessor;
  aoRetirar: () => void;
  aoEnviarVersao: (arquivo: File) => void;
  ocupado: boolean;
}) {
  const ativo = material.status !== 'retirado' && material.status !== 'substituido';
  const paginas = `${material.paginas} ${material.paginas === 1 ? 'página' : 'páginas'}`;
  return (
    <li className="list-row">
      <span className="file-icon">
        <Icone nome="file-type-pdf" />
      </span>
      <span className="list-row-main">
        <span className="strong">
          Aula {material.aula_numero} · {material.aula_titulo}
          {material.versao > 1 && <span className="small muted"> · versão {material.versao}</span>}
        </span>
        <span className="small muted">
          {paginas} · enviado em {DATA.format(new Date(material.criado_em))}
        </span>
      </span>
      <SituacaoDoMaterial material={material} />
      {ativo && (
        <span className="row">
          {material.status === 'pronto' && (
            <a
              className="fr-icon-btn fr-icon-btn--sm"
              href={`/api/materiais/${material.id}/arquivo?pagina=1#page=1`}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`Ver a aula ${material.aula_numero} (PDF em nova aba)`}
            >
              <Icone nome="eye" />
            </a>
          )}
          {/* O campo de arquivo fica dentro do rótulo com cara de botão: teclado e leitor de tela. */}
          <label
            className="fr-icon-btn fr-icon-btn--sm campo-de-arquivo"
            title={`Enviar nova versão da aula ${material.aula_numero}`}
          >
            <Icone nome="refresh" />
            <input
              type="file"
              accept="application/pdf,.pdf"
              aria-label={`Enviar nova versão da aula ${material.aula_numero}`}
              disabled={ocupado}
              className="sr-only"
              onChange={(evento) => {
                const arquivo = evento.target.files?.[0];
                if (arquivo) aoEnviarVersao(arquivo);
                evento.target.value = '';
              }}
            />
          </label>
          <button
            type="button"
            className="fr-icon-btn fr-icon-btn--sm"
            aria-label={`Retirar a aula ${material.aula_numero}`}
            title={`Retirar a aula ${material.aula_numero}`}
            disabled={ocupado}
            onClick={aoRetirar}
          >
            <Icone nome="trash" />
          </button>
        </span>
      )}
    </li>
  );
}

/** A tela de materiais: a aluna vai para a página da disciplina; o professor envia e acompanha. */
export function PaginaMateriais() {
  const disciplinaId = Number(useParams().id);
  const perfil = useEu().data?.perfil_ativo;
  if (perfil === 'aluno') {
    // Os materiais da aluna ficam na página da disciplina, como no protótipo.
    return <Navigate to={`/disciplinas/${disciplinaId}`} replace />;
  }
  return <MateriaisDoProfessor />;
}

/**
 * Os materiais da disciplina para o professor, como no protótipo: o envio por arrastar ou escolher
 * o PDF e a lista com a etapa ao vivo de cada um (MAT-RF-01 a 03, MAT-RF-10 e 11).
 */
function MateriaisDoProfessor() {
  const disciplinaId = Number(useParams().id);
  const disciplina = useDisciplina(disciplinaId).data;
  const clienteDeDados = useQueryClient();
  const chave = ['materiais', disciplinaId];
  const materiais = useQuery({
    queryKey: chave,
    queryFn: () => listarMateriaisDoProfessor(disciplinaId),
    refetchInterval: (consulta) =>
      consulta.state.data?.some((m) => m.status === 'processando')
        ? INTERVALO_DE_ATUALIZACAO_EM_MS
        : false,
  });
  const recarregar = () => clienteDeDados.invalidateQueries({ queryKey: chave });
  const enviar = useMutation({
    mutationFn: (dados: { arquivo: File; aulaNumero: number; aulaTitulo: string }) =>
      enviarMaterial(disciplinaId, dados),
    onSuccess: recarregar,
  });
  const retirar = useMutation({ mutationFn: retirarMaterial, onSuccess: recarregar });
  const enviarVersao = useMutation({
    mutationFn: ({ id, arquivo }: { id: number; arquivo: File }) => enviarNovaVersao(id, arquivo),
    onSuccess: recarregar,
  });

  const seletor = useRef<HTMLInputElement>(null);
  const [arrastando, setArrastando] = useState(false);
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [aulaNumero, setAulaNumero] = useState('');
  const [aulaTitulo, setAulaTitulo] = useState('');
  const [erro, setErro] = useState('');

  const proximaAula = Math.max(0, ...(materiais.data ?? []).map((m) => m.aula_numero)) + 1;

  function escolher(escolhido: File | undefined) {
    setErro('');
    enviar.reset();
    setArquivo(escolhido ?? null);
    if (escolhido) {
      setAulaNumero(String(proximaAula));
      setAulaTitulo(tituloPeloArquivo(escolhido.name));
    }
  }

  function aoSoltar(evento: DragEvent) {
    evento.preventDefault();
    setArrastando(false);
    escolher(evento.dataTransfer.files[0]);
  }

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    if (!arquivo || !ehPdf(arquivo)) {
      setErro(NAO_E_PDF);
      return;
    }
    if (!aulaNumero || !aulaTitulo.trim()) {
      setErro('Informe o número e o título da aula.');
      return;
    }
    setErro('');
    enviar.mutate(
      { arquivo, aulaNumero: Number(aulaNumero), aulaTitulo: aulaTitulo.trim() },
      {
        onSuccess: () => {
          setArquivo(null);
          setAulaNumero('');
          setAulaTitulo('');
        },
      },
    );
  }

  const aviso =
    erro ||
    (enviar.isError ? motivo(enviar.error) : '') ||
    (enviarVersao.isError ? motivo(enviarVersao.error) : '');
  const lista = [...(materiais.data ?? [])].sort((a, b) => b.aula_numero - a.aula_numero);

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Materiais</h1>
          <p className="page-sub">
            {disciplina ? `${disciplina.nome} · ${disciplina.turma} · ` : ''}Os PDFs publicados aqui
            alimentam o tutor.
          </p>
        </div>
        <Botao icone="upload" onClick={() => seletor.current?.click()}>
          Enviar PDF
        </Botao>
      </div>

      <div
        data-testid="area-de-envio"
        className={arrastando ? 'dropzone is-over' : 'dropzone'}
        onDragOver={(evento) => {
          evento.preventDefault();
          setArrastando(true);
        }}
        onDragLeave={() => setArrastando(false)}
        onDrop={aoSoltar}
      >
        <span className="empty-state-icon">
          <Icone nome="cloud-upload" />
        </span>
        <p>
          Arraste um PDF para cá ou{' '}
          <button type="button" className="link-inline" onClick={() => seletor.current?.click()}>
            escolha um arquivo
          </button>
          .
        </p>
        <p className="small muted">Use PDFs com texto selecionável, de até 50 MB e 300 páginas.</p>
        <input
          ref={seletor}
          type="file"
          accept="application/pdf,.pdf"
          aria-label="Arquivo PDF da aula"
          tabIndex={-1}
          className="sr-only"
          onChange={(evento) => {
            escolher(evento.target.files?.[0]);
            evento.target.value = '';
          }}
        />
      </div>

      {arquivo && (
        <form onSubmit={aoEnviar} noValidate className="panel stack" aria-label="Publicar a aula">
          <p className="card-heading">
            <Icone nome="file-type-pdf" />
            Arquivo escolhido: {arquivo.name}
          </p>
          <div className="generator">
            <div className="fr-field generator-qtd">
              <label htmlFor="aula-numero" className="fr-label">
                Número da aula
              </label>
              <input
                id="aula-numero"
                className="fr-input"
                type="number"
                min={1}
                max={999}
                value={aulaNumero}
                onChange={(evento) => setAulaNumero(evento.target.value)}
              />
            </div>
            <div className="fr-field generator-aula">
              <label htmlFor="aula-titulo" className="fr-label">
                Título da aula
              </label>
              <input
                id="aula-titulo"
                className="fr-input"
                value={aulaTitulo}
                maxLength={200}
                onChange={(evento) => setAulaTitulo(evento.target.value)}
              />
            </div>
            <Botao type="submit" disabled={enviar.isPending}>
              Publicar aula
            </Botao>
            <Botao variante="contorno" onClick={() => escolher(undefined)}>
              Cancelar
            </Botao>
          </div>
        </form>
      )}
      {aviso && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          {aviso}
        </p>
      )}

      <section className="stack" aria-labelledby="titulo-lista">
        <h2 id="titulo-lista" className="section-title">
          Publicados{materiais.data ? ` (${materiais.data.length})` : ''}
        </h2>
        {materiais.isPending && (
          <p role="status" className="muted">
            Carregando os materiais…
          </p>
        )}
        {materiais.isError && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível carregar os materiais. Tente de novo em instantes.
          </p>
        )}
        {retirar.isError && (
          <p role="alert" className="notice notice--danger">
            <Icone nome="alert-triangle" />
            Não foi possível retirar o material. Tente de novo.
          </p>
        )}
        {materiais.data &&
          (lista.length === 0 ? (
            <ul className="panel list">
              <li className="list-row muted">Nenhum material enviado ainda.</li>
            </ul>
          ) : (
            <ul aria-label="Materiais da disciplina" aria-live="polite" className="panel list">
              {lista.map((material) => (
                <LinhaDeMaterial
                  key={material.id}
                  material={material}
                  ocupado={retirar.isPending || enviarVersao.isPending}
                  aoRetirar={() => retirar.mutate(material.id)}
                  aoEnviarVersao={(escolhido) => {
                    if (!ehPdf(escolhido)) {
                      setErro(NAO_E_PDF);
                      return;
                    }
                    setErro('');
                    enviarVersao.mutate({ id: material.id, arquivo: escolhido });
                  }}
                />
              ))}
            </ul>
          ))}
      </section>
    </div>
  );
}
