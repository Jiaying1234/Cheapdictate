from pathlib import Path
from threading import Event
import time

import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16_000
CHANNELS = 1


def record_audio(output_path: Path, stop_event: Event) -> Path:
    """Record until stop_event is set and save the audio as a WAV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sf.SoundFile(
        output_path,
        mode="w",
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        subtype="PCM_16",
    ) as audio_file:
        def capture_audio(
            audio_data: object,
            _frame_count: int,
            _time_info: object,
            _status: object,
        ) -> None:
            audio_file.write(audio_data)

        # Capture mono audio at a speech-friendly sample rate until release.
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            callback=capture_audio,
        ):
            while not stop_event.wait(0.05):
                time.sleep(0)

    return output_path
