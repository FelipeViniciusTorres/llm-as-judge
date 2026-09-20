"""Camada fina sobre um endpoint de LLM compatível com a API da OpenAI.

A chave, a URL base e o modelo vêm do arquivo .env (LLM_API_KEY, LLM_BASE_URL,
LLM_MODEL). Qualquer provedor compatível com a API de chat completions da
OpenAI funciona (ex.: um endpoint próprio servindo modelos Qwen).
"""

import json
import os
import re

import certifi
import httpx2
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = "qwen3-36-27b"
DEFAULT_BASE_URL = "https://hub-gpus-lab.usto.re/v1"
PLACEHOLDER_KEY = "cole_sua_chave_aqui"
NO_THINK_PREFIX = "/no_think\n"


class LLMConfigError(RuntimeError):
    """Chave da API ausente ou ainda com o valor de exemplo."""


def get_model_name() -> str:
    return os.getenv("LLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


_client = None


def _get_client() -> OpenAI:
    global _client
    key = os.getenv("LLM_API_KEY", "").strip()
    if not key or key == PLACEHOLDER_KEY:
        raise LLMConfigError(
            "Chave do LLM não configurada. Abra o arquivo .env e preencha "
            "LLM_API_KEY (e, se necessário, LLM_BASE_URL)."
        )
    if _client is None:
        base_url = os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
        # verify=certifi.where() evita o backend "truststore" do httpx2, que trava em
        # recursão infinita neste Windows/Python 3.13 (bug do truststore, não da rede).
        http_client = httpx2.Client(verify=certifi.where())
        _client = OpenAI(api_key=key, base_url=base_url, http_client=http_client)
    return _client


_ROLE_MAP = {"user": "user", "model": "assistant"}


def _to_openai_messages(system_instruction: str, messages: list[dict]) -> list[dict]:
    """Converte [{'role': 'user'|'model', 'text': '...'}] para o formato do chat completions."""
    out = [{"role": "system", "content": f"{NO_THINK_PREFIX}{system_instruction}"}]
    out += [{"role": _ROLE_MAP.get(m["role"], m["role"]), "content": m["text"]} for m in messages]
    return out


def _extrair_json(texto: str) -> str:
    """Remove cercas de código markdown (```json ... ```), caso o modelo as inclua."""
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", texto, re.DOTALL)
    return match.group(1) if match else texto.strip()


def generate_text(
    system_instruction: str,
    messages: list[dict],
    temperature: float = 0.6,
    max_tokens: int | None = None,
) -> str:
    args = {
        "model": get_model_name(),
        "messages": _to_openai_messages(system_instruction, messages),
        "temperature": temperature,
    }
    if max_tokens is not None:
        args["max_tokens"] = max_tokens
    response = _get_client().chat.completions.create(**args)
    return (response.choices[0].message.content or "").strip()


def generate_json(
    system_instruction: str,
    prompt: str,
    schema,
    temperature: float = 0.0,
    max_tokens: int | None = None,
):
    """Pede uma resposta estruturada e devolve uma instância do modelo pydantic `schema`."""
    instrucoes_formato = (
        "Responda APENAS com um JSON válido, sem markdown e sem texto fora do JSON, "
        f"seguindo exatamente este schema:\n{json.dumps(schema.model_json_schema(), ensure_ascii=False)}"
    )
    messages = [
        {"role": "system", "content": f"{NO_THINK_PREFIX}{system_instruction}\n\n{instrucoes_formato}"},
        {"role": "user", "content": prompt},
    ]
    client = _get_client()
    args = {
        "model": get_model_name(),
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens is not None:
        args["max_tokens"] = max_tokens
    try:
        response = client.chat.completions.create(
            **args,
            response_format={"type": "json_object"},
        )
    except Exception:
        # Nem todo provedor compatível com a API da OpenAI aceita response_format.
        response = client.chat.completions.create(**args)
    conteudo = _extrair_json(response.choices[0].message.content or "{}")
    return schema.model_validate_json(conteudo)

