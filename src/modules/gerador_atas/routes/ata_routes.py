import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database import get_db

from modules.gerador_atas.schemas.ata_schemas import TranscricaoResponse
from modules.gerador_atas.services.ata_services import (
    gerar_ata_docx_service,
    transcrever_audio_service,
)

atas_router = APIRouter(prefix="/atas", tags=["atas"])


@atas_router.get("/health")
async def atas_health():
    """Health-check for the gerador_atas module."""
    return {"status": "ok", "module": "gerador_atas"}


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


@atas_router.post("/gerar-doc")
async def gerar_ata_doc(
    # Meeting transcript — either pasted text OR an uploaded audio file
    transcricao:     str        = Form(""),
    file:            UploadFile = File(None),
    # Manual meeting metadata
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
    """
    Generates an ATA (.docx) from a meeting transcription and manual metadata.

    Accepts either:
    - A pre-existing transcription via the `transcricao` form field, OR
    - An audio file via `file` which will be transcribed on the fly (requires GPU).

    Returns the .docx file as a binary attachment.
    """
    # --- Resolve transcription ---
    transcricao_id = None
    if transcricao.strip():
        pass  # Use provided text directly
    elif file is not None:
        content = await file.read()
        suffix = os.path.splitext(file.filename or ".wav")[1] or ".wav"
        try:
            transcricao, _, transcricao_id = await transcrever_audio_service(db, content, suffix=suffix)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transcription failed: {exc}",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie a transcrição ou um arquivo de áudio.",
        )

    # --- Generate DOCX via service ---
    try:
        docx_bytes, filename = await gerar_ata_docx_service(
            db=db,
            transcricao=transcricao,
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
            transcricao_id=transcricao_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATA generation failed: {exc}",
        )

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
