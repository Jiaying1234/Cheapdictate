import json
from pathlib import Path

SETTINGS_PATH = Path("data/settings.json")
DEFAULT_HOTKEY = "shift_r"

# These are the keys that can be selected in the settings window.
HOTKEY_OPTIONS = (
    "shift_r",
    "shift_l",
    "ctrl_r",
    "ctrl_l",
    "alt_r",
    "alt_l",
    "caps_lock",
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "f10",
    "f11",
    "f12",
)


def load_hotkey(path: Path = SETTINGS_PATH) -> str:
    """Load the selected hotkey, using the default only when no settings exist."""
    if not path.is_file():
        return DEFAULT_HOTKEY
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read settings: {path}") from error
    if not isinstance(settings, dict) or not isinstance(settings.get("hotkey"), str):
        raise RuntimeError(f"Invalid settings format: {path}")
    return settings["hotkey"]


def save_hotkey(hotkey: str, path: Path = SETTINGS_PATH) -> str:
    """Persist a hotkey selected from the available options."""
    normalized = hotkey
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(
            json.dumps({"hotkey": normalized}, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise RuntimeError(f"Could not save settings: {path}") from error
    return normalized
