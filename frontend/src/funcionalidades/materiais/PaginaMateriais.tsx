import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type DragEvent, type FormEvent } from 'react';
import { useParams } from 'react-router';

import {
  enviarMaterial,
  enviarNovaVersao,
  ErroDaApi,
  listarMateriaisDoProfessor,
  retirarMaterial,
  type MaterialDoProfessor,
} from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { useEu } from '../contas/sessao';
import { useDisciplinas } from '../disciplinas/consultas';
import { MateriaisDoAluno } from './MateriaisDoAluno';

const NAO_E_PDF = 'Envie um arquivo PDF. Slides podem ser exportados como PDF.';
/** Enquanto algum material processa, a lista se atualiza sozinha nesse intervalo. */
const INTERVALO_DE_ATUALIZACAO_EM_MS = 2000;

function ehPdf(arquivo: File): boolean {
  return arquivo.type === 'application/pdf' || arquivo.name.toLowerCase().endsWith('.pdf');
}

function motivo(erro: unknown): string {
  const corpo = erro instanceof ErroDaApi ? (erro.corpo as Record<string, string[]>) : undefined;
  const primeiro = corpo && Object.values(corpo).find((valor) => Array.isArray(valor));
  return primeiro?.[0] ?? 'Não foi possível enviar o material. Tente de novo.';
}

function situacao(material: MaterialDoProfessor): string {
  return material.status === 'processando' ? material.etapa_rotulo : material.status_rotulo;
}

function ItemDeMaterial({
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
  return (
    <li className="flex flex-wrap items-start justify-between gap-2 rounded-lg border border-line bg-surface p-4">
      <div>
        <p className="font-bold">
          Aula {material.aula_numero}: {material.aula_titulo}
          {material.versao > 1 && (
            <span className="ml-2 text-sm font-normal text-ink-muted">
              versão {material.versao}
            </span>
          )}
        </p>
        <p className={material.status === 'pronto' ? 'text-success-text' : 'text-ink-muted'}>
          {situacao(material)}
        </p>
        {material.paginas_sem_texto.length > 0 && (
          <p className="text-sm text-warning-text">
            Páginas sem texto: {material.paginas_sem_texto.join(', ')}
          </p>
        )}
        {material.erro && <p className="text-sm text-danger-text">{material.erro}</p>}
      </div>
      {ativo && (
        <div className="flex flex-wrap gap-2">
          {/* O campo de arquivo fica dentro do rótulo com cara de botão: teclado e leitor de tela. */}
          <label className="inline-flex min-h-12 cursor-pointer items-center rounded-lg border border-line-control bg-surface px-4 text-sm font-bold text-ink focus-within:outline focus-within:outline-2">
            Enviar nova versão
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
          <Botao
            variante="secundario"
            aria-label={`Retirar a aula ${material.aula_numero}`}
            disabled={ocupado}
            onClick={aoRetirar}
          >
            Retirar
          </Botao>
        </div>
      )}
    </li>
  );
}

/** A tela de materiais: a aluna vê e abre os prontos; o professor envia e acompanha. */
export function PaginaMateriais() {
  const disciplinaId = Number(useParams().id);
  const disciplina = useDisciplinas('').data?.find((d) => d.id === disciplinaId);
  const perfil = useEu().data?.perfil_ativo;
  if (perfil === 'aluno') {
    return (
      <div className="page">
        <h1 className="text-2xl font-extrabold">
          {disciplina ? `Materiais de ${disciplina.nome}` : 'Materiais da disciplina'}
        </h1>
        <MateriaisDoAluno disciplinaId={disciplinaId} />
      </div>
    );
  }
  return <MateriaisDoProfessor />;
}

/** Os materiais da disciplina para o professor: envio do PDF e etapas ao vivo (MAT-RF-01 a 03). */
function MateriaisDoProfessor() {
  const disciplinaId = Number(useParams().id);
  const disciplina = useDisciplinas('').data?.find((d) => d.id === disciplinaId);
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

  const [arquivo, setArquivo] = useState<File | null>(null);
  const [aulaNumero, setAulaNumero] = useState('');
  const [aulaTitulo, setAulaTitulo] = useState('');
  const [erro, setErro] = useState('');

  function escolher(escolhido: File | undefined) {
    setErro('');
    enviar.reset();
    setArquivo(escolhido ?? null);
  }

  function aoSoltar(evento: DragEvent) {
    evento.preventDefault();
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

  return (
    <div className="page">
      <h1 className="text-2xl font-extrabold">
        {disciplina ? `Materiais de ${disciplina.nome}` : 'Materiais da disciplina'}
      </h1>

      <form
        onSubmit={aoEnviar}
        noValidate
        className="flex flex-col gap-3 rounded-lg border border-line bg-surface p-4"
      >
        <h2 className="text-lg font-bold">Enviar o PDF de uma aula</h2>
        <div
          data-testid="area-de-envio"
          onDragOver={(evento) => evento.preventDefault()}
          onDrop={aoSoltar}
          className="rounded-lg border-2 border-dashed border-line-strong p-4"
        >
          <label htmlFor="arquivo" className="block font-bold">
            Arquivo PDF da aula
          </label>
          <p className="text-sm text-ink-muted">Arraste o PDF para cá ou escolha o arquivo.</p>
          <input
            id="arquivo"
            type="file"
            accept="application/pdf,.pdf"
            onChange={(evento) => escolher(evento.target.files?.[0])}
            className="mt-2 block min-h-12"
          />
          {arquivo && <p className="mt-1 text-sm">Arquivo escolhido: {arquivo.name}</p>}
        </div>
        <div className="flex flex-wrap gap-3">
          <div>
            <label htmlFor="aula-numero" className="block text-sm font-bold">
              Número da aula
            </label>
            <input
              id="aula-numero"
              type="number"
              min={1}
              max={999}
              value={aulaNumero}
              onChange={(evento) => setAulaNumero(evento.target.value)}
              className="mt-1 min-h-12 w-28 rounded-lg border border-line-control bg-surface px-3 text-ink"
            />
          </div>
          <div className="min-w-0 flex-1">
            <label htmlFor="aula-titulo" className="block text-sm font-bold">
              Título da aula
            </label>
            <input
              id="aula-titulo"
              value={aulaTitulo}
              maxLength={200}
              onChange={(evento) => setAulaTitulo(evento.target.value)}
              className="mt-1 min-h-12 w-full rounded-lg border border-line-control bg-surface px-3 text-ink"
            />
          </div>
        </div>
        <Botao type="submit" disabled={enviar.isPending} className="self-start">
          Enviar PDF
        </Botao>
        {aviso && (
          <p role="alert" className="text-danger-text">
            {aviso}
          </p>
        )}
      </form>

      <section aria-labelledby="titulo-lista" className="flex flex-col gap-2">
        <h2 id="titulo-lista" className="text-lg font-bold">
          Materiais enviados
        </h2>
        {materiais.isPending && (
          <p role="status" className="text-ink-muted">
            Carregando os materiais…
          </p>
        )}
        {materiais.isError && (
          <p role="alert" className="text-danger-text">
            Não foi possível carregar os materiais. Tente de novo em instantes.
          </p>
        )}
        {retirar.isError && (
          <p role="alert" className="text-danger-text">
            Não foi possível retirar o material. Tente de novo.
          </p>
        )}
        {materiais.data &&
          (materiais.data.length === 0 ? (
            <p className="text-ink-muted">Nenhum material enviado ainda.</p>
          ) : (
            <ul
              aria-label="Materiais da disciplina"
              aria-live="polite"
              className="flex flex-col gap-2"
            >
              {materiais.data.map((material) => (
                <ItemDeMaterial
                  key={material.id}
                  material={material}
                  ocupado={retirar.isPending || enviarVersao.isPending}
                  aoRetirar={() => retirar.mutate(material.id)}
                  aoEnviarVersao={(arquivo) => {
                    if (!ehPdf(arquivo)) {
                      setErro(NAO_E_PDF);
                      return;
                    }
                    setErro('');
                    enviarVersao.mutate({ id: material.id, arquivo });
                  }}
                />
              ))}
            </ul>
          ))}
      </section>
    </div>
  );
}
