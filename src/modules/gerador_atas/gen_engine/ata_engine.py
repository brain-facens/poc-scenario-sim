"""
gen_engine.py – Pipeline de geração de ATAs com suporte a fallback local.
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from openai import AsyncOpenAI, AuthenticationError, RateLimitError

from modules.gerador_atas.gen_engine.prompts.ata_prompts_completo import (
    PROMPT_CORRETOR,
    PROMPT_DELIBERACOES,
    PROMPT_INTRODUCAO,
    PROMPT_TOPICOS,
    PROMPT_VALIDADOR,
)

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

_ = load_dotenv(dotenv_path=find_dotenv())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LLM_LOG_FILE = LOG_DIR / "ata_llm_calls.jsonl"

MIN_TRANSCRICAO_CHARS = 10


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BackendConfig:
    client:      AsyncOpenAI
    model_large: str
    model_small: str
    name:        str


BACKEND_OPENAI = BackendConfig(
    client=AsyncOpenAI(
        api_key=os.getenv("OPENAI_KEY"),
        max_retries=1,
        timeout=86400,
    ),
    model_large="gpt-4.1-mini",
    model_small="gpt-5.4-nano",
    name="OpenAI",
)

BACKEND_LOCAL = BackendConfig(
    client=AsyncOpenAI(
        base_url="http://172.16.51.162:11434/v1/",
        api_key="ollama",
        max_retries=0,
        timeout=86400,
    ),
    model_large="qwen3.5:latest",
    model_small="qwen3.5:latest",
    name="Local (Ollama)",
)

_MODE = os.getenv("BACKEND_MODE", "local").strip().lower()

if _MODE == "openai":
    _CFG, _FALLBACK = BACKEND_OPENAI, None
elif _MODE == "auto":
    _CFG, _FALLBACK = BACKEND_OPENAI, BACKEND_LOCAL
else: 
    _CFG, _FALLBACK = BACKEND_LOCAL, None

logger.info("Backend: %s | Fallback: %s", _CFG.name, _FALLBACK.name if _FALLBACK else "nenhum")

_QUOTA_ERRORS = ("insufficient_quota", "quota_exceeded", "billing_hard_limit_reached")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _append_llm_log(payload: dict) -> None:
    try:
        with LLM_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning("Falha ao gravar log de LLM: %s", e)


def _to_text(content) -> str:
    """Normaliza o conteúdo retornado pelo modelo para string."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False)
    if isinstance(content, list):
        partes = []
        for item in content:
            if isinstance(item, str):
                partes.append(item)
            elif isinstance(item, dict):
                partes.append(item.get("text") or json.dumps(item, ensure_ascii=False))
            elif item is not None:
                partes.append(str(item))
        return "\n".join(partes).strip()
    return str(content).strip() if content is not None else ""


async def _completion(
    *,
    cfg: BackendConfig,
    fallback: BackendConfig | None,
    messages: list[dict],
    reasoning: bool = False,
    agent_name: str = "desconhecido",
) -> str:
    model = cfg.model_small if reasoning else cfg.model_large
    kwargs: dict = dict(model=model, messages=messages)

    # reasoning_effort é exclusivo da OpenAI — não enviar para Ollama
    if reasoning and cfg.name == "OpenAI":
        kwargs["reasoning_effort"] = "high"

    prompt_text = "\n\n".join(
        f"[{m.get('role', 'user')}]\n{m.get('content', '')}" for m in messages
    )
    started_at = datetime.utcnow().isoformat() + "Z"
    t0 = time.time()

    try:
        resp = await cfg.client.chat.completions.create(**kwargs)
        content = _to_text(resp.choices[0].message.content)
        duration = round(time.time() - t0, 3)

        _append_llm_log({
            "timestamp": started_at, "agent": agent_name, "backend": cfg.name,
            "model": model, "reasoning": reasoning,
            "prompt_chars": len(prompt_text), "response_chars": len(content),
            "duration_seconds": duration, "prompt": prompt_text,
            "response": content, "status": "success",
        })
        return content

    except (RateLimitError, AuthenticationError) as exc:
        _append_llm_log({
            "timestamp": started_at, "agent": agent_name, "backend": cfg.name,
            "model": model, "reasoning": reasoning,
            "prompt_chars": len(prompt_text),
            "duration_seconds": round(time.time() - t0, 3),
            "prompt": prompt_text, "error_type": type(exc).__name__,
            "error_message": str(exc), "status": "error",
        })

        is_quota = any(code in str(exc).lower() for code in _QUOTA_ERRORS)
        if (is_quota or isinstance(exc, AuthenticationError)) and fallback:
            logger.warning("[%s] Redirecionando para '%s'…", agent_name, fallback.name)
            return await _completion(
                cfg=fallback, fallback=None,
                messages=messages, reasoning=reasoning,
                agent_name=agent_name,
            )

        logger.error("[%s] Sem fallback. Erro: %s", agent_name, exc)
        raise

    except Exception as exc:
        _append_llm_log({
            "timestamp": started_at, "agent": agent_name, "backend": cfg.name,
            "model": model, "reasoning": reasoning,
            "prompt_chars": len(prompt_text),
            "duration_seconds": round(time.time() - t0, 3),
            "prompt": prompt_text, "error_type": type(exc).__name__,
            "error_message": str(exc), "status": "error",
        })
        logger.error("[%s] Erro inesperado: %s", agent_name, exc)
        raise


# ---------------------------------------------------------------------------
# Agentes
# ---------------------------------------------------------------------------

async def corrigir_transcricao(transcricao: str, dados_manuais: str) -> str:
    logger.info("[Corretor] Enviando (%d chars)…", len(transcricao))
    result = await _completion(
        cfg=_CFG, fallback=_FALLBACK,
        messages=[{"role": "user", "content": PROMPT_CORRETOR.format(
            transcricao=transcricao, dados_manuais=dados_manuais,
        )}],
        reasoning=False, agent_name="Corretor",
    )
    logger.info("[Corretor] Concluído (%d chars).", len(result))
    return result


async def gerar_introducao(transcricao: str, dados_manuais: str) -> str:
    logger.info("[Introdução] Gerando…")
    result = await _completion(
        cfg=_CFG, fallback=_FALLBACK,
        messages=[{"role": "user", "content": PROMPT_INTRODUCAO.format(
            transcricao=transcricao, dados_manuais=dados_manuais,
        )}],
        reasoning=False, agent_name="Introdução",
    )
    logger.info("[Introdução] Concluída (%d chars).", len(result))
    return result


async def gerar_topicos(transcricao: str, dados_manuais: str) -> str:
    logger.info("[Tópicos] Gerando…")
    result = await _completion(
        cfg=_CFG, fallback=_FALLBACK,
        messages=[{"role": "user", "content": PROMPT_TOPICOS.format(
            transcricao=transcricao, dados_manuais=dados_manuais,
        )}],
        reasoning=True, agent_name="Topicos",
    )
    logger.info("[Tópicos] Concluídos (%d chars).", len(result))
    return result


async def gerar_deliberacoes(transcricao: str, dados_manuais: str) -> str:
    logger.info("[Deliberações] Gerando…")
    result = await _completion(
        cfg=_CFG, fallback=_FALLBACK,
        messages=[{"role": "user", "content": PROMPT_DELIBERACOES.format(
            transcciricao=transcricao, dados_manuais=dados_manuais,
        )}],
        reasoning=True, agent_name="Deliberações",
    )
    logger.info("[Deliberações] Concluídas (%d chars).", len(result))
    return result


async def validar_ata(
    transcricao_corrigida: str,
    dados_manuais: str,
    participantes: list[str],
    topicos: list[str],
    deliberacoes: list[str],
) -> dict:
    logger.info("[Validador] Validando ATA…")
    raw = await _completion(
        cfg=_CFG, fallback=_FALLBACK,
        messages=[{"role": "user", "content": PROMPT_VALIDADOR.format(
            transcricao=transcricao_corrigida,
            dados_manuais=dados_manuais,
            participantes=", ".join(participantes),
            topicos="\n".join(f"- {t}" for t in topicos),
            deliberacoes="\n".join(f"- {d}" for d in deliberacoes),
        )}],
        reasoning=True, agent_name="Validador",
    )
    try:
        resultado = json.loads(raw.replace("```json", "").replace("```", "").strip())
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning("[Validador] JSON inválido — usando dados originais.")
        resultado = {"participantes": participantes, "topicos": topicos, "deliberacoes": deliberacoes}

    logger.info("[Validador] Concluído.")
    return resultado


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

async def estruturar_ata(transcricao: str, dados_manuais: dict) -> dict:
    """
    Orquestra todos os agentes e retorna a estrutura completa da ATA.
    Backend definido pela variável BACKEND_MODE no .env (local | openai | auto).
    """
    logger.info("▶ Pipeline iniciado | backend=%s | fallback=%s",
                _CFG.name, _FALLBACK.name if _FALLBACK else "nenhum")

    inicio_total = time.time()
    dados_str = "\n".join(f"{k}: {v}" for k, v in dados_manuais.items())

    # ── 1. Validação por tamanho ─────────────────────────────────────────────
    chars = len(transcricao.strip())
    logger.info("Validação: %d chars (mínimo: %d)", chars, MIN_TRANSCRICAO_CHARS)

    if chars < MIN_TRANSCRICAO_CHARS:
        return {"ok": False, "erro": "Erro: Gravação muito curta ou erro durante a gravação"}

    # ── 2. Correção ──────────────────────────────────────────────────────────
    t0 = time.time()
    transcricao_corrigida = await corrigir_transcricao(transcricao, dados_str)
    logger.info("⏱ Correção: %.1fs", time.time() - t0)

    # ── 3. Agentes paralelos ─────────────────────────────────────────────────
    t0 = time.time()
    introducao_raw, topicos_raw, deliberacoes_raw = await asyncio.gather(
        gerar_introducao(transcricao_corrigida, dados_str),
        gerar_topicos(transcricao_corrigida, dados_str),
        gerar_deliberacoes(transcricao_corrigida, dados_str),
    )
    logger.info("⏱ Agentes paralelos: %.1fs", time.time() - t0)

    # Extrai tema e introdução
    tema = ""
    introducao_partes = []
    for linha in introducao_raw.strip().splitlines():
        if linha.startswith("Tema da Reunião:"):
            tema = linha.replace("Tema da Reunião:", "").strip()
        elif linha.strip():
            introducao_partes.append(linha.strip())

    topicos_list      = [t.strip("•-– ").strip() for t in topicos_raw.splitlines()      if t.strip()]
    deliberacoes_list = [d.strip("•-– ").strip() for d in deliberacoes_raw.splitlines() if d.strip()]

    participantes_raw = dados_manuais.get("participantes", "")
    participantes_list = (
        participantes_raw if isinstance(participantes_raw, list)
        else [p.strip() for p in participantes_raw.split(",") if p.strip()]
    )

    # ── 4. Validação da ATA ──────────────────────────────────────────────────
    t0 = time.time()
    validado = await validar_ata(
        transcricao_corrigida=transcricao_corrigida,
        dados_manuais=dados_str,
        participantes=participantes_list,
        topicos=topicos_list,
        deliberacoes=deliberacoes_list,
    )
    logger.info("⏱ Validação: %.1fs", time.time() - t0)
    logger.info("✅ Pipeline concluído | TOTAL: %.1fs", time.time() - inicio_total)

    return {
        "ok": True,
        "tema": tema,
        "resumo": "\n".join(introducao_partes),
        "assuntos_discutidos": validado["topicos"],
        "deliberacoes": validado["deliberacoes"],
        "participantes": validado["participantes"],
        "ausentes": dados_manuais.get("ausentes", ""),
    }