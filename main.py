import os
from pathlib import Path

from dotenv import load_dotenv

from src.recorder import record_audio
from src.transcriber import MODEL, transcribe_audio


def main() -> None:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise RuntimeError("GROQ_API_KEY is missing from .env or the environment.")

    # Record the user's voice before sending the audio to Groq.
    output_path = Path("audio/recording.wav")
    print("Recording for 10 seconds...")
    record_audio(output_path)
    print(f"Saved recording to {output_path}")

    # Transcribe the saved recording and print the returned text.
    print(f"Transcribing with Groq {MODEL}...")
    print(transcribe_audio(output_path, api_key))


if __name__ == "__main__":
    main()
