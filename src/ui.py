import threading
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox, ttk

from src.history import load_transcriptions, save_transcription
from src.recorder import record_audio
from src.transcriber import transcribe_audio


class TranscriptionWindow:
    """Display transcriptions and let the user start a recording."""

    def __init__(
        self,
        root: tk.Tk,
        api_key: str,
        audio_path: Path,
        on_transcription: Callable[[str], None] | None = None,
    ) -> None:
        self.root = root
        self.api_key = api_key
        self.audio_path = audio_path
        self.on_transcription = on_transcription

        root.title("Cheapdictate")
        root.geometry("620x420")
        root.minsize(480, 320)

        frame = ttk.Frame(root, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Cheapdictate", font=("Segoe UI", 18, "bold")).pack(
            anchor=tk.W
        )
        self.status = ttk.Label(frame, text="Ready to record.")
        self.status.pack(anchor=tk.W, pady=(4, 12))

        self.record_button = ttk.Button(
            frame, text="Record and transcribe", command=self.start_recording
        )
        self.record_button.pack(anchor=tk.W)

        ttk.Label(frame, text="Latest transcriptions").pack(anchor=tk.W, pady=(18, 4))
        history_frame = ttk.Frame(frame)
        history_frame.pack(fill=tk.BOTH, expand=True)

        self.history = tk.Listbox(history_frame, activestyle="none")
        self.history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(
            history_frame, orient=tk.VERTICAL, command=self.history.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history.configure(yscrollcommand=scrollbar.set)
        self.refresh_history()

    def refresh_history(self) -> None:
        self.history.delete(0, tk.END)
        for transcription in load_transcriptions():
            self.history.insert(tk.END, transcription)

    def start_recording(self) -> None:
        self.record_button.configure(state=tk.DISABLED)
        self.status.configure(text="Recording for 10 seconds...")
        threading.Thread(target=self._record_and_transcribe, daemon=True).start()

    def _record_and_transcribe(self) -> None:
        try:
            record_audio(self.audio_path)
            self._set_status("Transcribing with Groq...")
            transcription = transcribe_audio(self.audio_path, self.api_key)
            save_transcription(transcription)
        except Exception as error:
            self.root.after(0, self._show_error, str(error))
            return

        self.root.after(0, self._show_transcription, transcription)

    def _set_status(self, text: str) -> None:
        self.root.after(0, self.status.configure, {"text": text})

    def _show_transcription(self, transcription: str) -> None:
        self.refresh_history()
        self.status.configure(text="Transcription complete.")
        self.record_button.configure(state=tk.NORMAL)
        if self.on_transcription:
            self.on_transcription(transcription)

    def _show_error(self, message: str) -> None:
        self.status.configure(text="Something went wrong.")
        self.record_button.configure(state=tk.NORMAL)
        messagebox.showerror("Cheapdictate error", message, parent=self.root)
