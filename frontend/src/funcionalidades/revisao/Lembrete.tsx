import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';

import { obterLembrete, salvarLembrete, type Lembrete } from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { Icone } from '../../componentes/Icone';

function Formulario({ inicial }: { inicial: Lembrete }) {
  const clienteDeDados = useQueryClient();
  const [ligado, setLigado] = useState(inicial.ligado);
  const [horario, setHorario] = useState(inicial.horario);
  const salvar = useMutation({
    mutationFn: () => salvarLembrete({ ligado, horario }),
    onSuccess: (salvo) => clienteDeDados.setQueryData(['lembrete'], salvo),
  });

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault();
    salvar.mutate();
  }

  return (
    <form className="stack" onSubmit={aoEnviar}>
      <div className="switch-row">
        <div className="switch-text">
          <label htmlFor="lembrete-ligado" className="strong">
            Lembrete diário por e-mail
          </label>
          <p id="lembrete-ajuda" className="small muted">
            Só chega nos dias em que há cartões para revisar.
          </p>
        </div>
        <input
          id="lembrete-ligado"
          type="checkbox"
          className="switch"
          checked={ligado}
          aria-describedby="lembrete-ajuda"
          onChange={(e) => setLigado(e.target.checked)}
        />
      </div>
      <div className="fr-field">
        <label htmlFor="lembrete-horario" className="fr-label">
          Horário do lembrete
        </label>
        <input
          id="lembrete-horario"
          type="time"
          className="fr-input"
          value={horario}
          disabled={!ligado}
          onChange={(e) => setHorario(e.target.value)}
        />
      </div>
      <div className="row row--end">
        <p role="status" className="small muted">
          {salvar.isSuccess ? 'Lembrete salvo.' : ''}
        </p>
        <Botao type="submit" variante="contorno" pequeno disabled={salvar.isPending}>
          Salvar lembrete
        </Botao>
      </div>
      {salvar.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível salvar o lembrete. Tente de novo.
        </p>
      )}
    </form>
  );
}

/** O lembrete diário da revisão, desligado por padrão (REV-RF-09). */
export function LembreteDaRevisao() {
  const lembrete = useQuery({ queryKey: ['lembrete'], queryFn: obterLembrete });
  return (
    <section className="panel stack" aria-labelledby="titulo-lembrete">
      <h2 id="titulo-lembrete" className="card-heading">
        <Icone nome="clock" />
        Lembrete da revisão
      </h2>
      {lembrete.data ? (
        <Formulario inicial={lembrete.data} />
      ) : (
        <p className="small muted">
          {lembrete.isError ? 'Não foi possível carregar.' : 'Carregando…'}
        </p>
      )}
    </section>
  );
}
