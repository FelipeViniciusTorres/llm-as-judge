"""Script auxiliar (uso único) para capturar transcrições reais do agente e do juiz.

Roda o cenário "queda_regiao" duas vezes: uma com o atendente normal (deve
CUMPRIR as regras) e outra com o modo de falhas propositais (deve VIOLAR
alguma regra). O resultado é impresso em JSON para ser colado no material
da aula (`gerar_pdf.py`), assim o PDF não depende de chamar a API toda vez
que for gerado.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import agent
import judge
from rules import SCENARIOS

CENARIO = SCENARIOS["queda_regiao"]
FALA_CLIENTE = CENARIO["falas_sugeridas"][0]


def rodar(com_falhas: bool) -> dict:
    historico = [{"role": "cliente", "content": FALA_CLIENTE}]
    resposta = agent.responder(historico, CENARIO, com_falhas=com_falhas)
    avaliacao = judge.avaliar(CENARIO, historico, resposta, primeira_resposta=True)
    return {
        "com_falhas": com_falhas,
        "fala_cliente": FALA_CLIENTE,
        "resposta_atendente": resposta,
        "avaliacao": json.loads(avaliacao.model_dump_json()),
    }


if __name__ == "__main__":
    resultado = {
        "correto": rodar(com_falhas=False),
        "com_falha": rodar(com_falhas=True),
    }
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
