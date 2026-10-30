"""
LLM client: structured outputs via OpenAI API, disk-based caching, async with semaphore,
and exponential backoff on rate limits.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Type, TypeVar

import openai
from pydantic import BaseModel

from . import config

T = TypeVar("T", bound=BaseModel)

_client: openai.AsyncOpenAI | None = None


def get_client() -> openai.AsyncOpenAI:
    global _client
    if _client is None:
        _client = openai.AsyncOpenAI(api_key=config.get_api_key())
    return _client


_semaphore: asyncio.Semaphore | None = None


def get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY)
    return _semaphore


# ── Token / cost tracking ────────────────────────────────────────────────────

_total_prompt_tokens: int = 0
_total_completion_tokens: int = 0

# Rough pricing (USD per 1K tokens) — update as needed
_PRICE_PER_1K = {
    "gpt-4.1": {"input": 0.002, "output": 0.008},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
}


def get_token_stats() -> dict[str, Any]:
    model = config.JUDGE_MODEL
    prices = _PRICE_PER_1K.get(model, {"input": 0.002, "output": 0.008})
    cost = (
        _total_prompt_tokens / 1000 * prices["input"]
        + _total_completion_tokens / 1000 * prices["output"]
    )
    return {
        "prompt_tokens": _total_prompt_tokens,
        "completion_tokens": _total_completion_tokens,
        "total_tokens": _total_prompt_tokens + _total_completion_tokens,
        "estimated_cost_usd": round(cost, 4),
    }


def _track_usage(usage: Any) -> None:
    global _total_prompt_tokens, _total_completion_tokens
    if usage:
        _total_prompt_tokens += getattr(usage, "prompt_tokens", 0)
        _total_completion_tokens += getattr(usage, "completion_tokens", 0)


# ── Disk cache ───────────────────────────────────────────────────────────────

def _cache_key(model: str, system: str, user: str) -> str:
    raw = json.dumps({"model": model, "system": system, "user": user}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _cache_path(key: str) -> Path:
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return config.CACHE_DIR / f"{key}.json"


def _read_cache(key: str) -> dict | None:
    p = _cache_path(key)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _write_cache(key: str, data: dict) -> None:
    _cache_path(key).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Core LLM call ────────────────────────────────────────────────────────────

async def llm_call(
    system: str,
    user: str,
    response_model: Type[T],
    model: str | None = None,
    use_cache: bool = True,
    details_log: list | None = None,
) -> T:
    """
    Make a structured LLM call with caching and backoff.
    Returns a parsed Pydantic model instance.
    """
    model = model or config.JUDGE_MODEL
    key = _cache_key(model, system, user)

    # ── Check cache ──────────────────────────────────────────────────────────
    if use_cache:
        cached = _read_cache(key)
        if cached is not None:
            parsed = response_model.model_validate(cached["result"])
            if details_log is not None:
                details_log.append({
                    "cached": True,
                    "key": key,
                    "model": model,
                    "result": cached["result"],
                })
            return parsed

    async with get_semaphore():
        result_dict, usage = await _call_with_backoff(model, system, user, response_model)

    _track_usage(usage)

    # ── Store cache ──────────────────────────────────────────────────────────
    if use_cache:
        _write_cache(key, {"result": result_dict, "model": model})

    if details_log is not None:
        details_log.append({
            "cached": False,
            "key": key,
            "model": model,
            "system_preview": system[:200],
            "user_preview": user[:400],
            "result": result_dict,
        })

    return response_model.model_validate(result_dict)


async def _call_with_backoff(
    model: str,
    system: str,
    user: str,
    response_model: Type[T],
    max_retries: int = 6,
) -> tuple[dict, Any]:
    """Call the OpenAI API with exponential backoff on rate-limit errors."""
    client = get_client()
    delay = 1.0
    last_exc: Exception | None = None

    for attempt in range(max_retries):
        try:
            response = await client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format=response_model,
                temperature=0,
            )
            parsed = response.choices[0].message.parsed
            result_dict = parsed.model_dump()
            return result_dict, response.usage

        except openai.RateLimitError as exc:
            last_exc = exc
            wait = delay * (2 ** attempt)
            print(f"  [rate limit] waiting {wait:.1f}s (attempt {attempt+1}/{max_retries})")
            await asyncio.sleep(wait)

        except openai.APIStatusError as exc:
            if exc.status_code in (429, 500, 502, 503, 504):
                last_exc = exc
                wait = delay * (2 ** attempt)
                await asyncio.sleep(wait)
            else:
                raise

    raise last_exc or RuntimeError("LLM call failed after retries")


# ── Embedding call ────────────────────────────────────────────────────────────

async def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings for a list of texts."""
    client = get_client()
    response = await client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=texts,
    )
    _track_usage(response.usage)
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
