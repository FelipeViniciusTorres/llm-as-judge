"""LLM as a Judge.

Um segundo modelo (temperatura 0) lê a conversa e classifica, regra por regra,
se a última resposta do atendente cumpriu, violou ou não se aplica.
A nota e o veredito são calculados aqui em Python, a partir dessa classificação,
para que o resultado seja previsível e fácil de auditar.
"""

import unicodedata

from pydantic import BaseModel, Field

from llm import generate_json
from rules import BUSINESS_RULES, EMPRESA

STATUS_VALIDOS = ("cumprida", "violada", "nao_aplicavel")


def _sem_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


class RegraAvaliada(BaseModel):
    id: str = Field(description="Identificador da regra, por exemplo R1")
    status: str = Field(description="Um de: cumprida, violada, nao_aplicavel")
    justificativa: str = Field(description="Uma frase curta explicando o porquê")


class ParecerDoJuiz(BaseModel):
    regras: list[RegraAvaliada]
    resumo: str = Field(description="Resumo do parecer em uma frase")


class Avaliacao(BaseModel):
    regras: list[RegraAvaliada]
    resumo: str
    nota: float
    aprovada: bool
    violadas: list[str]


_SYSTEM = f"""Você é um avaliador rigoroso e imparcial (LLM as a Judge) de atendimentos
de call center da {EMPRESA}. Sua tarefa é verificar se a ÚLTIMA resposta do atendente
respeita as regras de negócio. Não avalie simpatia nem estilo de escrita: uma resposta
pode ser educada e convincente e ainda assim violar uma regra.

Para cada regra, responda com um destes status:
- cumprida: a resposta segue a regra.
- violada: a resposta contraria a regra.
- nao_aplicavel: a regra não se aplica a esta resposta.

Baseie-se apenas nos dados do sistema, na conversa e na resposta avaliada."""


def _montar_prompt(scenario: dict, historico: list[dict], resposta: str, primeira_resposta: bool) -> str:
    regras = "\n".join(f"- {r['id']}: {r['texto']}" for r in BUSINESS_RULES)
    contexto = "\n".join(f"- {k}: {v}" for k, v in scenario["contexto_sistema"].items())
    conversa = "\n".join(
        f"{'CLIENTE' if m['role'] == 'cliente' else 'ATENDENTE'}: {m['content']}"
        for m in historico
    )
    nota_r1 = (
        "Esta é a PRIMEIRA resposta do atendente, então a R1 se aplica."
        if primeira_resposta
        else "Esta NÃO é a primeira resposta do atendente, então a R1 não se aplica (nao_aplicavel)."
    )
    return f"""DADOS DO SISTEMA:
{contexto}

REGRAS DE NEGÓCIO:
{regras}

CONVERSA ATÉ AQUI:
{conversa}

RESPOSTA DO ATENDENTE A SER AVALIADA:
{resposta}

{nota_r1}
Avalie as regras {", ".join(r["id"] for r in BUSINESS_RULES)}, todas, na mesma ordem."""


def avaliar(scenario: dict, historico: list[dict], resposta: str, primeira_resposta: bool) -> Avaliacao:
    """Avalia `resposta`. `historico` deve conter a conversa até a última fala do cliente."""
    parecer = generate_json(
        _SYSTEM,
        _montar_prompt(scenario, historico, resposta, primeira_resposta),
        ParecerDoJuiz,
        temperature=0.0,
    )

    por_id = {r.id.strip().upper(): r for r in parecer.regras}
    regras: list[RegraAvaliada] = []
    for regra in BUSINESS_RULES:
        r = por_id.get(regra["id"])
        if r is None:
            r = RegraAvaliada(
                id=regra["id"],
                status="nao_aplicavel",
                justificativa="O juiz não retornou parecer para esta regra.",
            )
        status = _sem_acentos(r.status).strip().lower().replace(" ", "_")
        if status not in STATUS_VALIDOS:
            status = "nao_aplicavel"
        regras.append(RegraAvaliada(id=regra["id"], status=status, justificativa=r.justificativa))

    cumpridas = sum(r.status == "cumprida" for r in regras)
    violadas = [r.id for r in regras if r.status == "violada"]
    avaliadas = cumpridas + len(violadas)
    nota = round(10 * cumpridas / avaliadas, 1) if avaliadas else 10.0

    return Avaliacao(
        regras=regras,
        resumo=parecer.resumo,
        nota=nota,
        aprovada=not violadas,
        violadas=violadas,
    )
