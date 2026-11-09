import json
from datetime import date
from pathlib import Path

DAILY_AUDIO_LIMIT_SECONDS = 28_800
MINIMUM_BILLED_SECONDS = 10
USAGE_PATH = Path("data/usage.json")


def word_count(text: str) -> int:
    """Return the number of whitespace-separated words in a transcription."""
    return len(text.split())


def record_usage(
    duration_seconds: float, path: Path = USAGE_PATH, words: int = 0
) -> int:
    """Record one request and return the remaining daily audio seconds."""
    if duration_seconds < 0:
        raise ValueError("Recording duration cannot be negative.")
    if words < 0:
        raise ValueError("Word count cannot be negative.")

    today = date.today().isoformat()
    used_seconds, total_words = _load_usage(path, today)
    billed_seconds = max(duration_seconds, MINIMUM_BILLED_SECONDS)
    used_seconds += billed_seconds
    total_words += words
    _save_usage(path, today, used_seconds, total_words)
    return max(0, int(DAILY_AUDIO_LIMIT_SECONDS - used_seconds))


def audio_time_left(path: Path = USAGE_PATH) -> int:
    """Return the remaining daily audio allowance in whole seconds."""
    used_seconds, _ = _load_usage(path, date.today().isoformat())
    return max(0, int(DAILY_AUDIO_LIMIT_SECONDS - used_seconds))


def total_words_today(path: Path = USAGE_PATH) -> int:
    """Return the total number of transcribed words for today."""
    _, total_words = _load_usage(path, date.today().isoformat())
    return total_words


def format_audio_time(seconds: int) -> str:
    """Format seconds as hours and minutes."""
    hours, remainder = divmod(max(0, seconds), 3600)
    minutes = remainder // 60
    return f"{hours}h {minutes}m"


def _load_usage(path: Path, today: str) -> tuple[float, int]:
    if not path.is_file():
        return 0.0, 0

    try:
        contents = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read usage history: {path}") from error

    if (
        not isinstance(contents, dict)
        or not isinstance(contents.get("date"), str)
        or not isinstance(contents.get("used_seconds"), (int, float))
        or isinstance(contents["used_seconds"], bool)
        or contents["used_seconds"] < 0
        or (
            "total_words" in contents
            and (
                not isinstance(contents["total_words"], int)
                or isinstance(contents["total_words"], bool)
                or contents["total_words"] < 0
            )
        )
    ):
        raise RuntimeError(f"Invalid usage history format: {path}")

    if contents["date"] != today:
        return 0.0, 0
    return float(contents["used_seconds"]), int(contents.get("total_words", 0))


def _save_usage(
    path: Path, today: str, used_seconds: float, total_words: int
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(
            json.dumps(
                {
                    "date": today,
                    "used_seconds": used_seconds,
                    "total_words": total_words,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise RuntimeError(f"Could not save usage history: {path}") from error
