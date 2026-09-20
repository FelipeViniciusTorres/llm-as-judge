"""Regras de negócio e cenários do call center (tudo fictício, só para a demo).

Aqui está o "gabarito" que o juiz usa para avaliar o atendente.
Para mudar o comportamento esperado, edite BUSINESS_RULES e SCENARIOS.
"""

EMPRESA = "NetVia Internet"

BUSINESS_RULES = [
    {
        "id": "R1",
        "titulo": "Cumprimento e protocolo",
        "texto": (
            "Na primeira resposta do atendimento, cumprimentar o cliente pelo nome "
            "e informar o número de protocolo."
        ),
    },
    {
        "id": "R2",
        "titulo": "Consultar o status da região",
        "texto": (
            "Antes de orientar qualquer procedimento técnico, considerar o status "
            "da região informado pelo sistema."
        ),
    },
    {
        "id": "R3",
        "titulo": "Queda na região",
        "texto": (
            "Se houver queda ou manutenção na região, informar a previsão de "
            "normalização e NÃO pedir reinício do modem nem abrir visita técnica."
        ),
    },
    {
        "id": "R4",
        "titulo": "Sem queda: modem antes da visita",
        "texto": (
            "Se NÃO houver queda na região, orientar o reinício do modem "
            "(desligar da tomada por 30 segundos). Só abrir visita técnica se o "
            "cliente confirmar que o problema continua, com prazo de até 48 horas úteis."
        ),
    },
    {
        "id": "R5",
        "titulo": "Sem promessa de compensação",
        "texto": (
            "Nunca prometer desconto, reembolso ou crédito. Se o cliente pedir, "
            "informar que o pedido deve ser feito ao setor financeiro."
        ),
    },
]

RULE_BY_ID = {r["id"]: r for r in BUSINESS_RULES}

SCENARIOS = {
    "queda_regiao": {
        "nome": "Queda na região",
        "descricao": "Cliente sem sinal, mas há um rompimento de cabo no bairro dele.",
        "contexto_sistema": {
            "Cliente": "Marina Costa",
            "Protocolo": "PRT-48213",
            "Plano": "Fibra 500 Mega",
            "Status da região": "QUEDA em andamento (rompimento de cabo no bairro)",
            "Previsão de normalização": "hoje, até as 18h",
        },
        "falas_sugeridas": [
            "Oi, estou sem sinal de internet desde a manhã.",
            "Já reiniciei o modem duas vezes e nada. Manda um técnico aqui!",
            "Vou ficar o dia todo sem internet, vocês vão me dar desconto?",
        ],
    },
    "sem_queda": {
        "nome": "Sem queda: problema local",
        "descricao": "Cliente sem sinal e a região está normal, então o problema é local.",
        "contexto_sistema": {
            "Cliente": "Carlos Almeida",
            "Protocolo": "PRT-51907",
            "Plano": "Fibra 300 Mega",
            "Status da região": "Normal, sem ocorrências",
            "Previsão de normalização": "não se aplica",
        },
        "falas_sugeridas": [
            "Boa tarde, minha internet está sem sinal e a luz do modem está vermelha.",
            "Reiniciei e continua igual, sem sinal.",
            "Pode mandar um técnico?",
        ],
    },
    "pede_desconto": {
        "nome": "Cliente pede desconto",
        "descricao": "Região normal, mas o cliente quer compensação pelo tempo sem sinal.",
        "contexto_sistema": {
            "Cliente": "Renata Souza",
            "Protocolo": "PRT-60342",
            "Plano": "Fibra 500 Mega",
            "Status da região": "Normal, sem ocorrências",
            "Previsão de normalização": "não se aplica",
        },
        "falas_sugeridas": [
            "Estou sem sinal há dois dias, isso é um absurdo!",
            "Já reiniciei o modem e não resolveu.",
            "Quero desconto na fatura por esses dois dias sem internet.",
        ],
    },
}
