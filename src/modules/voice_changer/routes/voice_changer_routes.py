from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import Response, JSONResponse
from ..services.voice_changer_services import check_health, change_voice, get_audio_response

voice_changer_router = APIRouter(
    prefix="/voice-changer",
    tags=["Voice Changer"]
)

@voice_changer_router.get("/health")
def api_health():
    """Check the health of the target voice changer API."""
    result = check_health()
    return JSONResponse(content=result)

@voice_changer_router.post("/services/voice_change")
def api_change_voice(
    menu_item: str,
    file: UploadFile = File(...)
):
    """
    Change your voice for any purpose.
    Args:
        file (UploadFile): audio to voice change.
        menu_item (str): voice options (e.g., 'Girl')
    Returns:
        Dict - metadata
    """
    result = change_voice(menu_item, file)
    return JSONResponse(content=result)

@voice_changer_router.get("/services/get_audio_response")
def api_get_audio_response():
    """Get the resulting audio response from the previous voice change."""
    content = get_audio_response()
    return Response(content=content, media_type="audio/wav")  # Assuming wav, the client will handle it
