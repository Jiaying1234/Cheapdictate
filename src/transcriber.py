from pathlib import Path

from groq import Groq

MODEL = "whisper-large-v3-turbo"


def transcribe_audio(audio_path: Path, api_key: str) -> str:
    """Send an audio file to Groq and return its transcription."""
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # The Groq client handles the multipart upload and Whisper request.
    client = Groq(api_key=api_key)
    with audio_path.open("rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(audio_path.name, audio_file.read()),
            model=MODEL,
        )

    text = transcription.text.strip()
    if not text:
        raise RuntimeError("Groq returned an empty transcription.")
    return text
