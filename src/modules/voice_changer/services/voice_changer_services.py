import requests
from fastapi import UploadFile, HTTPException
from typing import Dict, Any

BASE_URL = "https://voice-changer-8ut4.onrender.com"

def check_health() -> Any:
    try:
        response = requests.get(f"{BASE_URL}/")
        response.raise_for_status()
        # Fast API endpoints might return text or JSON, let's gracefully handle both
        try:
            return response.json()
        except Exception:
            return {"status": response.text}
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error connecting to Voice Changer API: {str(e)}")

def change_voice(menu_item: str, file: UploadFile) -> Dict[str, Any]:
    url = f"{BASE_URL}/v1/voice_changer/services/voice_change"
    params = {"menu_item": menu_item}
    
    try:
        # Read the file content
        file_content = file.file.read()
        files = {"file": (file.filename, file_content, file.content_type)}
        
        response = requests.post(url, params=params, files=files)
        response.raise_for_status()
        file.file.seek(0)
        return response.json()
    except requests.RequestException as e:
        status_code = e.response.status_code if e.response is not None else 502
        detail = e.response.text if e.response is not None else str(e)
        file.file.seek(0)
        raise HTTPException(status_code=status_code, detail=f"Voice Changer API error: {detail}")

def get_audio_response() -> bytes:
    url = f"{BASE_URL}/v1/voice_changer/services/get_audio_response"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        status_code = e.response.status_code if e.response is not None else 502
        detail = e.response.text if e.response is not None else str(e)
        raise HTTPException(status_code=status_code, detail=f"Voice Changer API error: {detail}")
