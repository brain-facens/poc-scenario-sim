import os
import tempfile
import asyncio
import traceback
from datetime import datetime, timedelta, timezone
from fastapi import BackgroundTasks

from dotenv import find_dotenv, load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import func

from modules.gerador_atas.gen_engine.ata_engine import estruturar_ata
from modules.gerador_atas.gen_engine.ata_utils import (
    MESES,
    _ano_por_extenso,
    _parse_hora,
    normalizar_lista_participantes,
)
from modules.gerador_atas.gen_engine.docx_builder import gerar_ata_docx
from modules.gerador_atas.models.ata_model import AtaModel, TranscricaoModel, AtaStatus

from typing import Optional
from core.pagination import paginate_and_filter
_ = load_dotenv(dotenv_path=find_dotenv())

def get_atas_service(db: Session, page: int = 1, limit: int = 10, numero_ata: Optional[str] = None, tema: Optional[str] = None, status: Optional[str] = None):
    filters = {"numero_ata": numero_ata, "tema": tema}
    if status is not None:
        filters["status"] = status
    return paginate_and_filter(
        db=db,
        model=AtaModel,
        page=page,
        limit=limit,
        filters=filters,
        default_order_by=AtaModel.created_at.desc()
    )


async def create_ata_queue_service(
    db: Session,
    background_tasks: BackgroundTasks,
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
    transcricao_id: str,
) -> AtaModel:
    hora_inicio, minutos_inicio = _parse_hora(hora_inicio_raw)
    hora_fim, minutos_fim = _parse_hora(hora_fim_raw)

    hoje = datetime.now()
    dia = str(hoje.day)
    mes = MESES[hoje.month]
    n_ano = _ano_por_extenso(hoje.year)

    participantes_list = normalizar_lista_participantes(participantes)
    ausentes_list = normalizar_lista_participantes(ausentes) if ausentes.strip() else []

    active_exists = (
        db.query(AtaModel).filter(AtaModel.status == AtaStatus.DOING).first()
        is not None
    )
    initial_status = AtaStatus.STALE if active_exists else AtaStatus.DOING

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
        info_adicional=info_adicional,
        transcricao_id=transcricao_id,
        status=initial_status,
    )
    db.add(ata_record)
    db.commit()
    db.refresh(ata_record)

    if initial_status == AtaStatus.DOING:
        background_tasks.add_task(run_ata_generation_task, ata_record.id)

    return ata_record


async def run_ata_generation_task(ata_id: str):
    from database import SessionLocal
    db = SessionLocal()
    try:
        ata_record = db.query(AtaModel).filter(AtaModel.id == ata_id).first()
        if not ata_record:
            return

        trans_record = db.query(TranscricaoModel).filter(TranscricaoModel.id == ata_record.transcricao_id).first()
        transcricao = trans_record.transcricao if trans_record else ""

        dados_manuais = {
            "numero_ata":      ata_record.numero_ata,
            "orgao":           ata_record.orgao,
            "sala":            ata_record.sala,
            "dia":             ata_record.dia,
            "mes":             ata_record.mes,
            "n_ano":           ata_record.n_ano,
            "hora_inicio":     ata_record.hora_inicio,
            "minutos_inicio":  ata_record.minutos_inicio,
            "hora_fim":        ata_record.hora_fim,
            "minutos_fim":     ata_record.minutos_fim,
            "participantes":   ata_record.participantes.replace(";", ", "),
            "ausentes":        ata_record.ausentes.replace(";", ", "),
            "condutor":        ata_record.condutor,
            "secretario":      ata_record.secretario,
            "info_adicional":  ata_record.info_adicional or "",
        }

        # --- LLM pipeline ---
        llm_data = await estruturar_ata(transcricao, dados_manuais)

        ata_record.tema = llm_data.get("tema", "")
        ata_record.resumo = llm_data.get("resumo", "")
        ata_record.assuntos_discutidos = "; ".join(llm_data.get("assuntos_discutidos", []))
        ata_record.deliberacoes = "; ".join(llm_data.get("deliberacoes", []))

        # --- Build DOCX ---
        participantes_list = [p.strip() for p in ata_record.participantes.split(";") if p.strip()]
        docx_bytes = gerar_ata_docx(
            numero_ata=ata_record.numero_ata,
            orgao=ata_record.orgao,
            tema=ata_record.tema,
            introducao=ata_record.resumo,
            topicos=llm_data.get("assuntos_discutidos", []),
            deliberacoes=llm_data.get("deliberacoes", []),
            condutor=ata_record.condutor,
            secretario=ata_record.secretario,
            hora_fim=ata_record.hora_fim,
            minutos_fim=ata_record.minutos_fim,
            participantes=participantes_list,
        )

        # Save DOCX to file
        os.makedirs("media/atas", exist_ok=True)
        filename = f"ATA_{ata_record.numero_ata.replace('/', '-')}_{ata_record.id}.docx"
        file_path = os.path.join("media", "atas", filename)
        
        with open(file_path, "wb") as f:
            data = docx_bytes.getvalue() if hasattr(docx_bytes, 'getvalue') else docx_bytes
            f.write(data)

        ata_record.file_path = file_path
        ata_record.status = AtaStatus.COMPLETE
        ata_record.updated_at = func.now()
        db.commit()

    except Exception:
        db.rollback()
        ata = db.query(AtaModel).filter(AtaModel.id == ata_id).first()
        if ata:
            ata.status = AtaStatus.INTERRUPTED
            ata.error = traceback.format_exc()
            db.commit()
    finally:
        db.close()


def get_ata_by_id_service(db: Session, ata_id: str):
    return db.query(AtaModel).filter(AtaModel.id == ata_id).first()


def cleanup_timed_out_atas(db: Session, timeout_minutes: int = 5):
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(minutes=timeout_minutes)
    
    timed_out = (
        db.query(AtaModel)
        .filter(
            AtaModel.status == AtaStatus.DOING,
            func.coalesce(AtaModel.updated_at, AtaModel.created_at) < threshold,
        )
        .all()
    )

    for item in timed_out:
        item.status = AtaStatus.INTERRUPTED
        item.error = "hard timeout error"

    db.commit()
    return len(timed_out)


async def process_stale_ata_queue(db: Session):
    active_job = db.query(AtaModel).filter(AtaModel.status == AtaStatus.DOING).first()
    if active_job:
        return None

    next_item = (
        db.query(AtaModel)
        .filter(AtaModel.status == AtaStatus.STALE)
        .order_by(AtaModel.created_at.asc())
        .first()
    )

    if next_item:
        next_item.status = AtaStatus.DOING
        db.commit()

        asyncio.create_task(run_ata_generation_task(next_item.id))
        return next_item.id

    return None


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
