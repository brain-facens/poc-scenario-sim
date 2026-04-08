import os
import tempfile
from datetime import datetime

from dotenv import find_dotenv, load_dotenv
from sqlalchemy.orm import Session

from modules.gerador_atas.gen_engine.ata_engine import estruturar_ata
from modules.gerador_atas.gen_engine.ata_utils import (
    MESES,
    _ano_por_extenso,
    _parse_hora,
    normalizar_lista_participantes,
)
from modules.gerador_atas.gen_engine.docx_builder import gerar_ata_docx
from modules.gerador_atas.models.ata_model import AtaModel, TranscricaoModel

from typing import Optional
from core.pagination import paginate_and_filter
_ = load_dotenv(dotenv_path=find_dotenv())

def get_atas_service(db: Session, page: int = 1, limit: int = 10, numero_ata: Optional[str] = None, tema: Optional[str] = None):
    filters = {"numero_ata": numero_ata, "tema": tema}
    return paginate_and_filter(
        db=db,
        model=AtaModel,
        page=page,
        limit=limit,
        filters=filters,
        default_order_by=AtaModel.created_at.desc()
    )


async def gerar_ata_docx_service(
    db: Session,
    transcricao: str,
    numero_ata: str,
    orgao: str,
    sala: str,
    hora_inicio_raw: str,
    hora_fim_raw: str,
    participantes: str,
    ausentes: str,
    condutor: str,
    secretario: str,
    info_adicional: str,
    transcricao_id: str | None = None,
) -> tuple[bytes, str]:
    """
    Orchestrates the full ATA generation pipeline:
      1. Parses the manual meeting data.
      2. Calls the LLM pipeline (estruturar_ata).
      3. Generates and returns the DOCX bytes.

    Returns:
        Tuple of (docx_bytes, suggested_filename).
    """
    # --- Parse hora ---
    hora_inicio, minutos_inicio = _parse_hora(hora_inicio_raw)
    hora_fim, minutos_fim = _parse_hora(hora_fim_raw)

    hoje = datetime.now()
    dia = str(hoje.day)
    mes = MESES[hoje.month]
    n_ano = _ano_por_extenso(hoje.year)

    participantes_list = normalizar_lista_participantes(participantes)
    ausentes_list = normalizar_lista_participantes(ausentes) if ausentes.strip() else []

    dados_manuais = {
        "numero_ata":      numero_ata,
        "orgao":           orgao,
        "sala":            sala,
        "dia":             dia,
        "mes":             mes,
        "n_ano":           n_ano,
        "hora_inicio":     hora_inicio,
        "minutos_inicio":  minutos_inicio,
        "hora_fim":        hora_fim,
        "minutos_fim":     minutos_fim,
        "participantes":   ", ".join(participantes_list),
        "ausentes":        ", ".join(ausentes_list),
        "condutor":        condutor,
        "secretario":      secretario,
        "info_adicional":  info_adicional,
    }

    # --- LLM pipeline ---
    llm_data = await estruturar_ata(transcricao, dados_manuais)

    # --- Build DOCX ---
    docx_bytes = gerar_ata_docx(
        numero_ata=numero_ata,
        orgao=orgao,
        tema=llm_data["tema"],
        introducao=llm_data["resumo"],
        topicos=llm_data["assuntos_discutidos"],
        deliberacoes=llm_data["deliberacoes"],
        condutor=condutor,
        secretario=secretario,
        hora_fim=hora_fim,
        minutos_fim=minutos_fim,
        participantes=participantes_list,
    )

    # --- Save to DB ---
    ata_record = AtaModel(
        numero_ata=numero_ata,
        orgao=orgao,
        sala=sala,
        dia=dia,
        mes=mes,
        n_ano=n_ano,
        hora_inicio=hora_inicio,
        minutos_inicio=minutos_inicio,
        hora_fim=hora_fim,
        minutos_fim=minutos_fim,
        participantes="; ".join(participantes_list),
        ausentes="; ".join(ausentes_list),
        condutor=condutor,
        secretario=secretario,
        tema=llm_data.get("tema", ""),
        resumo=llm_data.get("resumo", ""),
        assuntos_discutidos="; ".join(llm_data.get("assuntos_discutidos", [])),
        deliberacoes="; ".join(llm_data.get("deliberacoes", [])),
        transcricao_id=transcricao_id
    )
    db.add(ata_record)
    db.commit()

    filename = f"ATA_{numero_ata.replace('/', '-')}.docx"
    return docx_bytes, filename


async def transcrever_audio_service(db: Session, audio_bytes: bytes, suffix: str = ".wav") -> tuple[str, float, str]:
    """
    Writes uploaded audio bytes to a temp file, runs WhisperX transcription,
    saves the transaction to the DB, and returns (transcription_text, elapsed_seconds, transcricao_id).

    Note: WhisperX requires a CUDA-capable GPU. Import is intentionally lazy
    so the server can start even without a GPU (transcription endpoint will
    fail at call time rather than startup).
    """
    from modules.gerador_atas.gen_engine.transcribe import transcribe_api, transcribeX

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    transcribe_backend = os.getenv("TRANSCRIBE_BACKEND", "local").strip().lower()

    try:
        if transcribe_backend == "openai":
            transcricao, elapsed = await transcribe_api(tmp_path)
        else:
            transcricao, elapsed = await transcribeX(tmp_path)
    finally:
        os.remove(tmp_path)

    # --- Save to DB ---
    trans_record = TranscricaoModel(
        transcricao=transcricao,
        elapsed_seconds=elapsed
    )
    db.add(trans_record)
    db.commit()
    db.refresh(trans_record)

    return transcricao, elapsed, trans_record.id
