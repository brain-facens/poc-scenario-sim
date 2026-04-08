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

def transcribeX(audio_file: str) -> tuple[str, float]:
    """
    Transcribes an audio file using WhisperX with speaker diarization.

    Args:
        audio_file: Absolute path to the audio file.

    Returns:
        Tuple of (transcription_text, elapsed_seconds).
    """
    start_model = time.time()
    device = "cuda"
    batch_size = 4
    compute_type = "float16"

    model_dir = "src/model/"
    model = whisperx.load_model(
        "turbo",
        device,
        compute_type=compute_type,
        language="pt",
        download_root=model_dir,
    )

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size, language="pt")
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    model_a, metadata = whisperx.load_align_model(language_code="pt", device=device)
    result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )

    del model_a
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    diarize_model = DiarizationPipeline(token=os.getenv("HF_KEY"), device=device)
    diarize_segments = diarize_model(audio)
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