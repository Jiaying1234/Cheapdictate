import json
from datetime import datetime
from pathlib import Path
from typing import TypedDict

HISTORY_PATH = Path("data/transcriptions.json")
MAX_TRANSCRIPTIONS = 10


class Transcription(TypedDict):
    text: str
    timestamp: str | None


def load_transcriptions(path: Path = HISTORY_PATH) -> list[Transcription]:
    """Load saved transcriptions, returning newest entries first."""
    if not path.is_file():
        return []

    try:
        contents = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read transcription history: {path}") from error

    if not isinstance(contents, list):
        raise RuntimeError(f"Invalid transcription history format: {path}")

    transcriptions: list[Transcription] = []
    for item in contents[:MAX_TRANSCRIPTIONS]:
        if isinstance(item, str):
            transcriptions.append({"text": item, "timestamp": None})
        elif (
            isinstance(item, dict)
            and isinstance(item.get("text"), str)
            and (item.get("timestamp") is None or isinstance(item.get("timestamp"), str))
        ):
            transcriptions.append(
                {"text": item["text"], "timestamp": item.get("timestamp")}
            )
        else:
            raise RuntimeError(f"Invalid transcription history format: {path}")
    return transcriptions


def save_transcription(
    transcription: str, path: Path = HISTORY_PATH
) -> list[Transcription]:
    """Save a transcription and delete entries beyond the latest ten."""
    transcriptions = [
        {
            "text": transcription,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        },
        *load_transcriptions(path),
    ][:MAX_TRANSCRIPTIONS]
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(
            json.dumps(transcriptions, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise RuntimeError(f"Could not save transcription history: {path}") from error
    return transcriptions
