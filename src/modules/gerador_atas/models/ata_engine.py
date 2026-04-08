"""
gen_engine.py – Pipeline de geração de ATAs com suporte a fallback local.

BackendMode.OPENAI  → usa OpenAI sempre
BackendMode.LOCAL   → usa Ollama local sempre
BackendMode.AUTO    → tenta OpenAI; em caso de cota esgotada (insufficient_quota)
                      ou erro de autenticação, recai automaticamente para local
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
    PROMPT_RELEVANCIA_REUNIAO,
    PROMPT_TOPICOS,
    PROMPT_VALIDADOR,
)

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LLM_LOG_FILE = LOG_DIR / "ata_llm_calls.jsonl"
relv = False

def _append_llm_log(payload: dict) -> None:
    """Grava uma linha JSON por chamada de LLM."""
    try:
        with LLM_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning("Falha ao gravar log de LLM: %s", e)

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

_ = load_dotenv(dotenv_path=find_dotenv())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class BackendMode(str, Enum):
    """Estratégia de execução dos agentes LLM."""
    OPENAI = "openai"   # Força OpenAI
    LOCAL  = "local"    # Força Ollama local
    AUTO   = "auto"     # OpenAI com fallback automático para local


@dataclass(frozen=True)
class BackendConfig:
    """Configuração de cliente + modelos para um backend específico."""
    client:      AsyncOpenAI
    model_large: str   # agentes de texto livre (corretor, intro, validador)
    model_small: str   # agentes de raciocínio (tópicos, deliberações)
    name:        str   # label para logs


def _build_backends() -> tuple[BackendConfig, BackendConfig]:
    """Constrói as configurações de OpenAI e local."""

    openai_config = BackendConfig(
        client=AsyncOpenAI(api_key=os.getenv("OPENAI_KEY")),
        model_large="gpt-4.1-mini",
        model_small="gpt-5-mini",   
        name="OpenAI",
    )

    local_config = BackendConfig(
        client=AsyncOpenAI(
        base_url="http://172.16.51.162:11434/v1/",
        api_key="ollama",  
    ),
        model_large="qwen3.5:latest",
        model_small="qwen3.5:latest",
        name="Local (Ollama)",
    )

    return openai_config, local_config


BACKEND_OPENAI, BACKEND_LOCAL = _build_backends()

# Erros que indicam que a cota/credencial OpenAI está indisponível
_QUOTA_ERRORS = (
    "insufficient_quota",
    "quota_exceeded",
    "billing_hard_limit_reached",
)


# ---------------------------------------------------------------------------
# Helper de chamada com fallback
# ---------------------------------------------------------------------------

def _coerce_message_content_to_text(content) -> str:
    """
    Normaliza o content retornado pelo modelo para texto.
    Compatível com str, dict, list e None.
    """
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False)

    if isinstance(content, list):
        partes: list[str] = []
        for item in content:
            if isinstance(item, str):
                partes.append(item)
            elif isinstance(item, dict):
                if "text" in item and isinstance(item["text"], str):
                    partes.append(item["text"])
                else:
                    partes.append(json.dumps(item, ensure_ascii=False))
            elif item is None:
                continue
            else:
                partes.append(str(item))
        return "\n".join(partes).strip()

    if content is None:
        return ""

    return str(content).strip()


async def _completion(
    *,
    cfg: BackendConfig,
    fallback: BackendConfig | None,
    messages: list[dict],
    reasoning: bool = False,
    agent_name: str = "desconhecido",
) -> str:
    """
    Executa uma chamada chat.completions usando `cfg`.
    Se `fallback` for fornecido e a chamada falhar por cota/auth, retenta
    com `fallback` automaticamente.
    """
    model = cfg.model_small if reasoning else cfg.model_large
    kwargs: dict = dict(model=model, messages=messages)
    if reasoning:
        kwargs["reasoning_effort"] = "high"

    prompt_text = "\n\n".join(
        f"[{m.get('role', 'user')}]\n{m.get('content', '')}" for m in messages
    )
    started_at = datetime.utcnow().isoformat() + "Z"
    t0 = time.time()

    try:
        logger.debug("[%s|%s] Chamando modelo '%s'…", agent_name, cfg.name, model)
        resp = await cfg.client.chat.completions.create(**kwargs)

        raw_content = resp.choices[0].message.content
        content = _coerce_message_content_to_text(raw_content)
        duration = round(time.time() - t0, 3)

        _append_llm_log({
            "timestamp": started_at,
            "agent": agent_name,
            "backend": cfg.name,
            "model": model,
            "reasoning": reasoning,
            "prompt_chars": len(prompt_text),
            "response_chars": len(content),
            "duration_seconds": duration,
            "prompt": prompt_text,
            "response": content,
            "status": "success",
        })

        return content

    except (RateLimitError, AuthenticationError) as exc:
        duration = round(time.time() - t0, 3)

        _append_llm_log({
            "timestamp": started_at,
            "agent": agent_name,
            "backend": cfg.name,
            "model": model,
            "reasoning": reasoning,
            "prompt_chars": len(prompt_text),
            "duration_seconds": duration,
            "prompt": prompt_text,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "status": "error",
        })

        is_quota = any(code in str(exc).lower() for code in _QUOTA_ERRORS)
        is_auth = isinstance(exc, AuthenticationError)

        if (is_quota or is_auth) and fallback is not None:
            logger.warning(
                "[%s|%s] Falha (%s). Redirecionando para backend '%s'…",
                agent_name, cfg.name, type(exc).__name__, fallback.name,
            )
            return await _completion(
                cfg=fallback,
                fallback=None,
                messages=messages,
                reasoning=reasoning,
                agent_name=agent_name,
            )

        logger.error("[%s|%s] Sem fallback disponível. Erro: %s", agent_name, cfg.name, exc)
        raise

    except Exception as exc:
        duration = round(time.time() - t0, 3)

        _append_llm_log({
            "timestamp": started_at,
            "agent": agent_name,
            "backend": cfg.name,
            "model": model,
            "reasoning": reasoning,
            "prompt_chars": len(prompt_text),
            "duration_seconds": duration,
            "prompt": prompt_text,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "status": "error",
        })

        logger.error("[%s|%s] Erro inesperado: %s", agent_name, cfg.name, exc)
        raise

def _resolve_backends(mode: BackendMode) -> tuple[BackendConfig, BackendConfig | None]:
    """Retorna (cfg_principal, cfg_fallback) conforme o modo."""
    if mode == BackendMode.OPENAI:
        return BACKEND_OPENAI, None
    if mode == BackendMode.LOCAL:
        return BACKEND_LOCAL, None
    # AUTO → OpenAI com fallback para local
    return BACKEND_OPENAI, BACKEND_LOCAL

# ---------------------------------------------------------------------------
# Agentes
# ---------------------------------------------------------------------------
async def validar_reuniao(
        transcricao: str,
        cfg: BackendConfig,
        fallback: BackendConfig | None,
) -> str:
    logger.info("[Validador Reuniao] Enviando (%d chars)...", len(transcricao))
    prompt = PROMPT_RELEVANCIA_REUNIAO.format(
        transcricao=transcricao,
    )

    result = await _completion(
        cfg=cfg, fallback=fallback,
        messages=[{"role": "user", "content": prompt}],
        reasoning=False,
        agent_name="Reuniao"
    )
    logger.info("[Validador Reuniao] Concluido (%d chars).", len(result))
    if result.strip() == "True":
        return True
    else:
        return False


async def corrigir_transcricao(
    transcricao: str,
    dados_manuais: str,
    cfg: BackendConfig,
    fallback: BackendConfig | None,
) -> str:
    """Corrige erros de transcrição e normaliza o texto."""
    logger.info("[Corretor] Enviando (%d chars)…", len(transcricao))
    prompt = PROMPT_CORRETOR.format(
        transcricao=transcricao,
        dados_manuais=dados_manuais,
    )
    result = await _completion(
        cfg=cfg, fallback=fallback,
        messages=[{"role": "user", "content": prompt}],
        reasoning=False,
        agent_name="Corretor",
    )
    logger.info("[Corretor] Concluído (%d chars).", len(result))
    return result


async def gerar_introducao(
    transcricao: str,
    dados_manuais: str,
    cfg: BackendConfig,
    fallback: BackendConfig | None,
) -> str:
    """Gera o parágrafo de introdução e extrai o tema da reunião."""
    logger.info("[Introdução] Gerando…")
    prompt = PROMPT_INTRODUCAO.format(
        transcricao=transcricao,
        dados_manuais=dados_manuais,
    )
    result = await _completion(
        cfg=cfg, fallback=fallback,
        messages=[{"role": "user", "content": prompt}],
        reasoning=False,
        agent_name="Introdução",
    )
    logger.info("[Introdução] Concluída (%d chars).", len(result))
    return result


async def gerar_topicos(
    transcricao: str,
    dados_manuais: str,
    cfg: BackendConfig,
    fallback: BackendConfig | None,
) -> str:
    """Extrai os tópicos discutidos na reunião (raciocínio ativo)."""
    logger.info("[Tópicos] Gerando…")
    prompt = PROMPT_TOPICOS.format(
        transcricao=transcricao,
        dados_manuais=dados_manuais,
    )
    result = await _completion(
        cfg=cfg, fallback=fallback,
        messages=[{"role": "user", "content": prompt}],
        reasoning=True,
        agent_name="Topicos"
    )
    logger.info("[Tópicos] Concluídos (%d chars).", len(result))
    return result


async def gerar_deliberacoes(
    transcricao: str,
    dados_manuais: str,
    cfg: BackendConfig,
    fallback: BackendConfig | None,
) -> str:
    """Extrai as deliberações e encaminhamentos da reunião (raciocínio ativo)."""
    logger.info("[Deliberações] Gerando…")
    prompt = PROMPT_DELIBERACOES.format(
        transcricao=transcricao,
        dados_manuais=dados_manuais,
    )
    result = await _completion(
        cfg=cfg, fallback=fallback,
        messages=[{"role": "user", "content": prompt}],
        reasoning=True,
        agent_name="Deliberações"
    )
    logger.info("[Deliberações] Concluídas (%d chars).", len(result))
    return result


async def validar_ata(
    transcricao_corrigida: str,
    dados_manuais: str,
    participantes: list[str],
    topicos: list[str],
    deliberacoes: list[str],
    cfg: BackendConfig,
    fallback: BackendConfig | None,
) -> dict:
    """
    Valida e consolida participantes, tópicos e deliberações.
    Retorna um dict com as três listas já refinadas.
    """
    logger.info("[Validador] Validando ATA…")
    prompt = PROMPT_VALIDADOR.format(
        transcricao=transcricao_corrigida,
        dados_manuais=dados_manuais,
        participantes=", ".join(participantes),
        topicos="\n".join(f"- {t}" for t in topicos),
        deliberacoes="\n".join(f"- {d}" for d in deliberacoes),
    )

    raw = await _completion(
        cfg=cfg,
        fallback=fallback,
        messages=[{"role": "user", "content": prompt}],
        reasoning=True,
        agent_name="Validador",
    )

    try:
        raw_text = str(raw).replace("```json", "").replace("```", "").strip()
        resultado = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning("[Validador] JSON inválido retornado — usando dados originais.")
        resultado = {
            "participantes": participantes,
            "topicos": topicos,
            "deliberacoes": deliberacoes,
        }

    logger.info("[Validador] Concluído.")
    return resultado


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

DEFAULT_BACKEND_MODE = BackendMode(os.getenv("BACKEND_MODE", "local").strip().lower())


async def estruturar_ata(
    transcricao: str,
    dados_manuais: dict,
    *,
    mode=DEFAULT_BACKEND_MODE,
) -> dict:
    """
    Orquestra todos os agentes e retorna a estrutura completa da ATA.

    Args:
        transcricao:   Texto bruto da transcrição da reunião.
        dados_manuais: Metadados complementares (data, local, participantes…).
        mode:          Estratégia de backend (OPENAI | LOCAL | AUTO).

    Returns:
        dict com tema, resumo, assuntos_discutidos, deliberacoes,
        participantes e ausentes.
    """
    cfg, fallback = _resolve_backends(mode)
    logger.info("▶ Pipeline iniciado | backend=%s | fallback=%s",
                cfg.name, fallback.name if fallback else "nenhum")

    inicio_total = time.time()
    dados_str    = "\n".join(f"{k}: {v}" for k, v in dados_manuais.items())
    
    # ── 1. Correção ──────────────────────────────────────────────────────────
    t0 = time.time()
    relv = await validar_reuniao(
        transcricao, cfg, fallback
    )
    logger.info("Validando Reunião: %.1fs", time.time() - t0)

    if relv:
        transcricao_corrigida = await corrigir_transcricao(
            transcricao, dados_str, cfg, fallback
        )
        logger.info("⏱ Correção: %.1fs", time.time() - t0)

        t0 = time.time()
        introducao_raw, topicos_raw, deliberacoes_raw = await asyncio.gather(
            gerar_introducao(transcricao_corrigida, dados_str, cfg, fallback),
            gerar_topicos(transcricao_corrigida, dados_str, cfg, fallback),
            gerar_deliberacoes(transcricao_corrigida, dados_str, cfg, fallback),
        )
        logger.info("⏱ Agentes paralelos: %.1fs", time.time() - t0)

        tema = ""
        introducao_partes: list[str] = []
        for linha in introducao_raw.strip().splitlines():
            if linha.startswith("Tema da Reunião:"):
                tema = linha.replace("Tema da Reunião:", "").strip()
            elif linha.strip():
                introducao_partes.append(linha.strip())
        introducao = "\n".join(introducao_partes)

        topicos_list = [t.strip("•-– ").strip() for t in topicos_raw.splitlines() if t.strip()]
        deliberacoes_list = [d.strip("•-– ").strip() for d in deliberacoes_raw.splitlines() if d.strip()]

        participantes_raw = dados_manuais.get("participantes", "")
        participantes_list: list[str] = (
            participantes_raw
            if isinstance(participantes_raw, list)
            else [p.strip() for p in participantes_raw.split(",") if p.strip()]
        )

        t0 = time.time()
        validado = await validar_ata(
            transcricao_corrigida=transcricao_corrigida,
            dados_manuais=dados_str,
            participantes=participantes_list,
            topicos=topicos_list,
            deliberacoes=deliberacoes_list,
            cfg=cfg,
            fallback=fallback,
        )
        logger.info("Validação: %.1fs", time.time() - t0)

        logger.info("Pipeline concluído | TOTAL: %.1fs", time.time() - inicio_total)

        return {
            "ok": True,
            "tema": tema,
            "resumo": introducao,
            "assuntos_discutidos": validado["topicos"],
            "deliberacoes": validado["deliberacoes"],
            "participantes": validado["participantes"],
            "ausentes": dados_manuais.get("ausentes", ""),
        }
    else:
        logger.info("Não foi possível validar a reunião")
        return {
            "ok": False,
            "erro": "Erro: Gravação muito curta ou erro durante a gravação"
        }
