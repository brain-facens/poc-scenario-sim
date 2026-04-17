import os
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from core.pagination import PaginatedResponse
from database import get_db
from modules.gerador_atas.schemas.ata_schemas import AtaData, TranscricaoResponse
from modules.gerador_atas.services.ata_services import (
    create_ata_queue_service,
    get_atas_service,
    transcrever_audio_service,
)

atas_router = APIRouter(prefix="/atas", tags=["atas"])


@atas_router.get("/health")
async def atas_health():
    """Health-check for the gerador_atas module."""
    return {"status": "ok", "module": "gerador_atas"}


@atas_router.get("/", response_model=PaginatedResponse[AtaData])
def get_atas(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    numero_ata: Optional[str] = Query(None, description="Filter by ata number"),
    tema: Optional[str] = Query(None, description="Filter by theme")
):
    """
    Returns a paginated list of atas in the database, with optional filtering.
    """
    return get_atas_service(db, page=page, limit=limit, numero_ata=numero_ata, tema=tema)


@atas_router.post("/transcrever", response_model=TranscricaoResponse)
async def transcrever_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Transcribes an uploaded audio file using WhisperX with speaker diarization.

    Returns the raw (corrected) transcription text which can then be fed into
    the /atas/gerar-doc endpoint.

    Requires a CUDA-capable GPU.
    """
    content = await file.read()
    suffix = os.path.splitext(file.filename or ".wav")[1] or ".wav"

    try:
        transcricao, elapsed, _ = await transcrever_audio_service(db, content, suffix=suffix)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {exc}",
        )

    return TranscricaoResponse(transcricao=transcricao, elapsed_seconds=elapsed)


from fastapi import BackgroundTasks
from fastapi.responses import FileResponse

from modules.gerador_atas.models.ata_model import TranscricaoModel


@atas_router.post("/gerar-doc", response_model=AtaData)
async def gerar_ata_doc(
    background_tasks: BackgroundTasks,
    transcricao:     str        = Form(""),
    file:            UploadFile = File(None),
    numero_ata:      str        = Form(...),
    orgao:           str        = Form(...),
    sala:            str        = Form(...),
    hora_inicio_raw: str        = Form(...),
    hora_fim_raw:    str        = Form(...),
    participantes:   str        = Form(...),
    ausentes:        str        = Form(""),
    condutor:        str        = Form(...),
    secretario:      str        = Form(...),
    info_adicional:  str        = Form(""),
    db: Session = Depends(get_db),
):
    transcricao_id = None
    audio_bytes = None
    audio_suffix = ".wav"

    if transcricao.strip():
        # Texto colado diretamente — salva já e entra na fila normal
        t_model = TranscricaoModel(transcricao=transcricao.strip(), elapsed_seconds=0.0)
        db.add(t_model)
        db.commit()
        db.refresh(t_model)
        transcricao_id = t_model.id

    elif file is not None:
        # Áudio: lê os bytes aqui (antes de retornar), mas NÃO transcreve ainda
        audio_bytes = await file.read()
        audio_suffix = os.path.splitext(file.filename or ".wav")[1] or ".wav"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie a transcrição ou um arquivo de áudio.",
        )

    try:
        ata_record = await create_ata_queue_service(
            db=db,
            background_tasks=background_tasks,
            numero_ata=numero_ata,
            orgao=orgao,
            sala=sala,
            hora_inicio_raw=hora_inicio_raw,
            hora_fim_raw=hora_fim_raw,
            participantes=participantes,
            ausentes=ausentes,
            condutor=condutor,
            secretario=secretario,
            info_adicional=info_adicional,
            transcricao_id=transcricao_id,   # None se veio áudio
            audio_bytes=audio_bytes,          # bytes se veio áudio
            audio_suffix=audio_suffix,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATA generation failed: {exc}",
        )

    return ata_record  # retorna imediatamente com status TRANSCRIBING ou DOING/STALE


@atas_router.get("/{ata_id}", response_model=AtaData)
def get_ata_by_id(ata_id: str, db: Session = Depends(get_db)):
    """Retrieves a specific ATA by ID."""
    from modules.gerador_atas.services.ata_services import get_ata_by_id_service
    ata = get_ata_by_id_service(db, ata_id)
    if not ata:
        raise HTTPException(status_code=404, detail="ATA not found")
    return ata


@atas_router.get("/{ata_id}/download")
def download_ata(ata_id: str, db: Session = Depends(get_db)):
    """Downloads the generated DOCX for a given ATA ID."""
    from modules.gerador_atas.services.ata_services import get_ata_by_id_service
    ata = get_ata_by_id_service(db, ata_id)
    if not ata or not ata.file_path or not os.path.exists(ata.file_path):
        raise HTTPException(status_code=404, detail="Document not available or not yet generated")
    
    filename = os.path.basename(ata.file_path)
    return FileResponse(
        path=ata.file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )
