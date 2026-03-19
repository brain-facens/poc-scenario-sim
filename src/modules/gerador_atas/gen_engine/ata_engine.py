import asyncio
import logging
import os

from dotenv import find_dotenv, load_dotenv
from openai import AsyncOpenAI

from modules.gerador_atas.gen_engine.prompts.ata_prompts import (
    PROMPT_CORRETOR,
    PROMPT_DELIBERACOES,
    PROMPT_INTRODUCAO,
    PROMPT_TOPICOS,
)

_ = load_dotenv(dotenv_path=find_dotenv())

client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))
MODEL = "gpt-4o-mini"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def corrigir_transcricao(transcricao: str, dados_manuais: str) -> str:
    prompt_formatado = PROMPT_CORRETOR.format(
        transcricao=transcricao,
        dados_manuais=dados_manuais,
    )
    logger.info("Enviando transcrição para correção (%d chars)...", len(transcricao))
    response = await client.chat.completions.create(
        model=MODEL,
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
        model=MODEL,
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
        model=MODEL,
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
        model=MODEL,
        messages=[{"role": "user", "content": prompt_formatado}],
    )
    deliberacoes = response.choices[0].message.content.strip()
    logger.info("Deliberações geradas (%d chars).", len(deliberacoes))
    return deliberacoes


async def estruturar_ata(transcricao: str, dados_manuais: dict) -> dict:
    """
    Full LLM pipeline: corrects transcription then concurrently generates
    introducao, topicos, and deliberacoes sections.

    Args:
        transcricao: Raw or pre-processed transcription text.
        dados_manuais: Dict with meeting metadata (participantes, sala, etc.)

    Returns:
        Dict with keys: tema, resumo, assuntos_discutidos, deliberacoes,
        participantes, ausentes.
    """
    dados_str = "\n".join(f"{k}: {v}" for k, v in dados_manuais.items())

    transcricao_corrigida = await corrigir_transcricao(transcricao, dados_str)

    introducao_raw, topicos_raw, deliberacoes_raw = await asyncio.gather(
        gerar_introducao(transcricao_corrigida, dados_str),
        gerar_topicos(transcricao_corrigida, dados_str),
        gerar_deliberacoes(transcricao_corrigida, dados_str),
    )

    # Parse tema out of the introduction block
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

    return {
        "tema": tema,
        "resumo": introducao,
        "assuntos_discutidos": topicos_list,
        "deliberacoes": deliberacoes_list,
        "participantes": dados_manuais.get("participantes", ""),
        "ausentes": dados_manuais.get("ausentes", ""),
    }
