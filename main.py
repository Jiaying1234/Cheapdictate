import os
import tkinter as tk
from pathlib import Path

from dotenv import load_dotenv

from src.ui import TranscriptionWindow


def main() -> None:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise RuntimeError("GROQ_API_KEY is missing from .env or the environment.")

    root = tk.Tk()
    TranscriptionWindow(root, api_key, Path("audio/recording.wav"))
    root.mainloop()


if __name__ == "__main__":
    main()
