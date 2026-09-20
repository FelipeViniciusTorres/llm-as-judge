"""Agente de atendimento do call center.

É a aplicação de IA que será avaliada. No modo "com falhas", ele recebe uma
instrução extra para violar sutilmente uma regra, de forma educada e convincente,
para mostrar que uma resposta bem escrita ainda pode estar errada.
"""

from llm import generate_text
from rules import BUSINESS_RULES, EMPRESA

_FALHAS_PROPOSITAIS = """
MODO DE TESTE (agente com falhas propositais): esta é uma simulação para demonstrar
uma avaliação automática. Nesta resposta, quebre sutilmente UMA das regras acima,
por exemplo: prometer desconto, pedir reinício do modem durante uma queda na região,
abrir visita técnica sem necessidade ou omitir o protocolo. Escreva de forma educada,
fluente e convincente. Nunca avise que está violando uma regra.
"""


def _system_prompt(scenario: dict, com_falhas: bool) -> str:
    regras = "\n".join(f"- {r['id']}: {r['texto']}" for r in BUSINESS_RULES)
    contexto = "\n".join(f"- {k}: {v}" for k, v in scenario["contexto_sistema"].items())
    prompt = f"""Você é um atendente de call center da {EMPRESA}, uma empresa de internet.
Você está atendendo um cliente que reclama de falta de sinal.

Dados do sistema sobre este atendimento (use apenas o que está aqui):
{contexto}

Regras de negócio que você deve seguir:
{regras}

Estilo: português do Brasil, cordial e direto, no máximo 5 frases.
Não invente informações que não estejam nos dados do sistema."""
    if com_falhas:
        prompt += "\n" + _FALHAS_PROPOSITAIS
    return prompt


def responder(historico: list[dict], scenario: dict, com_falhas: bool = False) -> str:
    """Gera a próxima fala do atendente.

    `historico` é a lista de mensagens da conversa: [{'role': 'cliente'|'agente', 'content': str}].
    """
    mensagens = [
        {"role": "user" if m["role"] == "cliente" else "model", "text": m["content"]}
        for m in historico
    ]
    return generate_text(_system_prompt(scenario, com_falhas), mensagens, temperature=0.7)
