import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

from src.transcriber import MODEL, transcribe_audio

AUDIO_PATH = Path("audio/sample.wav")
SAMPLE_TEXT = "squirtle is my favourite pokemon"


def create_sample_audio(audio_path: Path) -> None:
    """Create the M1 sample speech file using Windows text-to-speech."""
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    escaped_path = str(audio_path.resolve()).replace("'", "''")
    powershell_script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile('{escaped_path}')
$synth.Speak('{SAMPLE_TEXT}')
$synth.Dispose()
"""
    # Windows includes the speech synthesizer, so M1 needs no extra audio package.
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            powershell_script,
        ],
        check=True,
    )


def main() -> None:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from .env or the environment.")

    if not AUDIO_PATH.exists():
        create_sample_audio(AUDIO_PATH)

    print(f"Transcribing {AUDIO_PATH} with Groq {MODEL}...")
    print(transcribe_audio(AUDIO_PATH, api_key))


if __name__ == "__main__":
    main()
