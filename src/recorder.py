from pathlib import Path

import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16_000
CHANNELS = 1


def record_audio(output_path: Path, duration_seconds: int = 10) -> Path:
    """Record microphone audio for a fixed duration and save it as a WAV file."""
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than zero.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Capture mono audio at a speech-friendly sample rate.
    recording = sd.rec(
        int(duration_seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
    )
    sd.wait()
    sf.write(output_path, recording, SAMPLE_RATE)
    return output_path
