import { useQuery } from '@tanstack/react-query';

import { obterAvisoDePrivacidade } from '../../api/cliente';
import { Botao } from '../../componentes/Botao';
import { Icone } from '../../componentes/Icone';
import { Modal } from '../../componentes/Modal';
import { useConfirmarCienciaDoAviso } from './sessao';

/**
 * Aviso de privacidade (ACE-RF-08), no modal do protótipo: aparece na primeira entrada do aluno e
 * a cada nova versão, e só some quando ele confirma que leu. Não fecha com Esc de propósito.
 */
export function AvisoDePrivacidade() {
  const aviso = useQuery({ queryKey: ['aviso-privacidade'], queryFn: obterAvisoDePrivacidade });
  const confirmar = useConfirmarCienciaDoAviso();

  if (!aviso.data) {
    return null;
  }

  return (
    <Modal titulo={aviso.data.titulo} subtitulo="Leia antes de começar">
      <ul className="list">
        {aviso.data.itens.map((item) => (
          <li key={item.titulo} className="list-row">
            <div>
              <h3 className="strong">{item.titulo}</h3>
              <p className="small muted">{item.texto}</p>
            </div>
          </li>
        ))}
      </ul>
      {confirmar.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível registrar a sua confirmação. Tente de novo.
        </p>
      )}
      <div className="fr-bubble-actions">
        <Botao disabled={confirmar.isPending} onClick={() => confirmar.mutate(aviso.data.versao)}>
          Entendi
        </Botao>
      </div>
    </Modal>
  );
}
