type Props = {
  valor: number;
  maximo?: number;
  /** Texto embaixo da barra, como "3 de 8 cartões". */
  rotulo?: string;
  /** Nome da barra para leitores de tela; sem ele, vale o rótulo. */
  rotuloAcessivel?: string;
};

/** Barra de progresso do design system (classe fr-progress do protótipo). */
export function Progresso({ valor, maximo = 100, rotulo, rotuloAcessivel }: Props) {
  const porcentagem =
    maximo > 0 ? Math.max(0, Math.min(100, Math.round((valor / maximo) * 100))) : 0;
  return (
    <div className="fr-progress">
      <div
        className="fr-progress-track"
        role="progressbar"
        aria-valuenow={valor}
        aria-valuemin={0}
        aria-valuemax={maximo}
        aria-label={rotuloAcessivel ?? rotulo}
      >
        <div className="fr-progress-fill" style={{ width: `${porcentagem}%` }} />
      </div>
      {rotulo && <span className="fr-progress-label">{rotulo}</span>}
    </div>
  );
}
