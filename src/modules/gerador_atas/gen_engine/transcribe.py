import gc
import os
import time

import torch
import whisperx
from dotenv import find_dotenv, load_dotenv
from whisperx.diarize import DiarizationPipeline
from openai import AsyncOpenAI

_ = load_dotenv(dotenv_path=find_dotenv())

OPENAI_KEY = os.getenv("OPENAI_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_KEY não encontrada no .env")

client = AsyncOpenAI(api_key=OPENAI_KEY)

import asyncio
import logging

logger = logging.getLogger(__name__)

# --- Singleton Models Cache ---
_WHISPER_MODELS = {
    "model": None,
    "model_a": None,
    "metadata": None,
    "diarize_model": None,
}

# Semaphore to strictly allow exactly 1 concurrent GPU inference
_whisper_lock = asyncio.Semaphore(1)


def _load_models_lazy():
    """Carrega os modelos para VRAM de forma preguiçosa caso ainda não existam."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    compute_type_env = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    compute_type = compute_type_env if device == "cuda" else "int8"
    
    model_size = os.getenv("WHISPER_MODEL_SIZE", "small")
    model_dir = "src/model/"
    
    if _WHISPER_MODELS["model"] is None:
        logger.info(f"Carregando WhisperX ({model_size}) na VRAM pela primeira vez com {compute_type}...")
        _WHISPER_MODELS["model"] = whisperx.load_model(
            model_size,
            device,
            compute_type=compute_type,
            language="pt",
            download_root=model_dir,
        )
    if _WHISPER_MODELS["model_a"] is None:
        logger.info("Carregando modelo de Alinhamento na VRAM...")
        _WHISPER_MODELS["model_a"], _WHISPER_MODELS["metadata"] = whisperx.load_align_model(
            language_code="pt", device=device
        )
    if _WHISPER_MODELS["diarize_model"] is None:
        hf_token = os.getenv("HF_KEY")
        if not hf_token:
            logger.warning("HF_KEY (Hugging Face Token) não encontrado. A diarização pode falhar em modelos privados.")
        
        logger.info("Carregando pipeline de Diarização na VRAM...")
        try:
            _WHISPER_MODELS["diarize_model"] = DiarizationPipeline(token=hf_token, device=device)
        except Exception as e:
            logger.error(f"Falha ao carregar DiarizationPipeline: {e}")
            if "AutoModel" in str(e):
                logger.error("Dica: Este erro geralmente indica termos de uso não aceitos no Hugging Face "
                             "ou falta da biblioteca 'accelerate'. Verifique os requisitos do modelo.")
            raise RuntimeError(f"Erro ao inicializar Diarização: {e}")

async def transcribeX(audio_file: str) -> tuple[str, float]:
    """
    Transcribes an audio file using WhisperX with speaker diarization.
    Protected by purely sequential execution (asyncio.Semaphore) to avoid CUDA OOM.
    """
    start_model = time.time()
    
    async with _whisper_lock:
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            batch_size = int(os.getenv("WHISPER_BATCH_SIZE", "1"))
            
            # Load if not loaded
            _load_models_lazy()
            
            # Run inference synchronously within threadpool if needed, but since Torch is blocking,
            # we are relying on lock to prevent crashes. A proper threadpool wrapping is ok but Semaphore rules.
            audio = whisperx.load_audio(audio_file)
            
            result = _WHISPER_MODELS["model"].transcribe(audio, batch_size=batch_size, language="pt")
            
            result = whisperx.align(
                result["segments"],
                _WHISPER_MODELS["model_a"],
                _WHISPER_MODELS["metadata"],
                audio,
                device,
                return_char_alignments=False,
            )
            
            diarize_segments = _WHISPER_MODELS["diarize_model"](audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)

            linhas = []
            for seg in result["segments"]:
                start = seg.get("start", 0)
                end = seg.get("end", 0)
                speaker = seg.get("speaker", "UNKNOWN")
                text = seg.get("text", "").strip()
                linhas.append(f"[{start:.2f} - {end:.2f}] {speaker}: {text}")

            transcricao_texto = "\n".join(linhas)
            elapsed = time.time() - start_model
            return transcricao_texto, elapsed
        finally:
            # Limpeza ativa para evitar VRAM fragmentation e CUDA OOM 
            if device == "cuda":
                gc.collect()
                torch.cuda.empty_cache()


async def transcribe_api(audio_path: str) -> tuple[str, float]:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")

    start = time.time()

    with open(audio_path, "rb") as audio_file:
        transcription = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="pt",
        )

    elapsed = time.time() - start
    return transcription.text, elapsed