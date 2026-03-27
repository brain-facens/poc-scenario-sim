import asyncio
import json
import logging
import os
import time

from dotenv import find_dotenv, load_dotenv
from openai import AsyncOpenAI

from modules.gerador_atas.gen_engine.prompts.ata_prompts import (
    PROMPT_CORRETOR,
    PROMPT_DELIBERACOES,
    PROMPT_INTRODUCAO,
    PROMPT_TOPICOS,
    PROMPT_VALIDADOR,
)

_ = load_dotenv(dotenv_path=find_dotenv())

client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))
MODEL_LARGE = "gpt-4.1-mini"
MODEL_TINY = "gpt-5-mini"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def corrigir_transcricao(transcricao: str, dados_manuais: str) -> str:
    prompt_formatado = PROMPT_CORRETOR.format(
        transcricao=transcricao,
        dados_manuais=dados_manuais,
    )
    logger.info("Enviando transcrição para correção (%d chars)...", len(transcricao))
    response = await client.chat.completions.create(
        model=MODEL_LARGE,
        messages=[{"role": "user", "content": prompt_formatado}],
    )
    transcricao_corrigida = response.choices[0].message.content.strip()
    logger.info("Correção concluída (%d chars).", len(transcricao_corrigida))
    return transcricao_corrigida


async def gerar_introducao(transcricao: str, dados_manuais: str) -> str:
    prompt_formatado = PROMPT_INTRODUCAO.format(
        transcricao=transcricao,
        dados_manuais=dados_manuais,
    )
    logger.info("Gerando introdução da ATA (%d chars)...", len(transcricao))
    response = await client.chat.completions.create(
        model=MODEL_LARGE,
        messages=[{"role": "user", "content": prompt_formatado}],
    )
    introducao = response.choices[0].message.content.strip()
    logger.info("Introdução gerada (%d chars).", len(introducao))
    return introducao


async def gerar_topicos(transcricao: str, dados_manuais: str) -> str:
    prompt_formatado = PROMPT_TOPICOS.format(
        transcricao=transcricao,
        dados_manuais=dados_manuais,
    )
    logger.info("Gerando tópicos da ATA (%d chars)...", len(transcricao))
    response = await client.chat.completions.create(
        model=MODEL_TINY,
        reasoning_effort="high",
        messages=[{"role": "user", "content": prompt_formatado}],
    )
    topicos = response.choices[0].message.content.strip()
    logger.info("Tópicos gerados (%d chars).", len(topicos))
    return topicos


async def gerar_deliberacoes(transcricao: str, dados_manuais: str) -> str:
    prompt_formatado = PROMPT_DELIBERACOES.format(
        transcricao=transcricao,
        dados_manuais=dados_manuais,
    )
    logger.info("Gerando deliberações da ATA (%d chars)...", len(transcricao))
    response = await client.chat.completions.create(
        model=MODEL_TINY,
        reasoning_effort="high",
        messages=[{"role": "user", "content": prompt_formatado}],
    )
    deliberacoes = response.choices[0].message.content.strip()
    logger.info("Deliberações geradas (%d chars).", len(deliberacoes))
    return deliberacoes


async def validar_ata(
    transcricao_corrigida: str,
    dados_manuais: str,
    participantes: list[str],
    topicos: list[str],
    deliberacoes: list[str],
) -> dict:
    prompt_formatado = PROMPT_VALIDADOR.format(
        transcricao=transcricao_corrigida,
        dados_manuais=dados_manuais,
        participantes=", ".join(participantes),
        topicos="\n".join(f"- {t}" for t in topicos),
        deliberacoes="\n".join(f"- {d}" for d in deliberacoes),
    )

    logger.info("Validando ATA gerada...")
    response = await client.chat.completions.create(
        model=MODEL_LARGE,
        messages=[{"role": "user", "content": prompt_formatado}],
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        resultado = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Validador retornou JSON inválido, usando dados originais.")
        resultado = {
            "participantes": participantes,
            "topicos": topicos,
            "deliberacoes": deliberacoes,
        }

    logger.info("Validação concluída.")
    return resultado


async def estruturar_ata(transcricao: str, dados_manuais: dict) -> dict:
    inicio_total = time.time()

    dados_str = "\n".join(f"{k}: {v}" for k, v in dados_manuais.items())

    # Correção
    inicio = time.time()
    transcricao_corrigida = await corrigir_transcricao(transcricao, dados_str)
    logger.info("⏱ Correção: %.1fs", time.time() - inicio)

    # Agentes paralelos
    inicio = time.time()
    introducao_raw, topicos_raw, deliberacoes_raw = await asyncio.gather(
        gerar_introducao(transcricao_corrigida, dados_str),
        gerar_topicos(transcricao_corrigida, dados_str),
        gerar_deliberacoes(transcricao_corrigida, dados_str),
    )
    logger.info("⏱ Agentes paralelos: %.1fs", time.time() - inicio)

    # Parse introdução
    linhas = introducao_raw.strip().splitlines()
    tema = ""
    introducao_partes = []
    for linha in linhas:
        if linha.startswith("Tema da Reunião:"):
            tema = linha.replace("Tema da Reunião:", "").strip()
        elif linha.strip():
            introducao_partes.append(linha.strip())
    introducao = "\n".join(introducao_partes)

    topicos_list = [t.strip("•-– ").strip() for t in topicos_raw.splitlines() if t.strip()]
    deliberacoes_list = [d.strip("•-– ").strip() for d in deliberacoes_raw.splitlines() if d.strip()]

    participantes_raw = dados_manuais.get("participantes", "")
    if isinstance(participantes_raw, list):
        participantes_list = participantes_raw
    else:
        participantes_list = [p.strip() for p in participantes_raw.split(",") if p.strip()]

    # Validação
    inicio = time.time()
    validado = await validar_ata(
        transcricao_corrigida=transcricao_corrigida,
        dados_manuais=dados_str,
        participantes=participantes_list,
        topicos=topicos_list,
        deliberacoes=deliberacoes_list,
    )
    logger.info("⏱ Validação: %.1fs", time.time() - inicio)

    logger.info("⏱ TOTAL PIPELINE: %.1fs", time.time() - inicio_total)

    return {
        "tema": tema,
        "resumo": introducao,
        "assuntos_discutidos": validado["topicos"],
        "deliberacoes": validado["deliberacoes"],
        "participantes": validado["participantes"],
        "ausentes": dados_manuais.get("ausentes", ""),
    }