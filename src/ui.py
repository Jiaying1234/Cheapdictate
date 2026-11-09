import threading
import time
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from threading import Event
from tkinter import messagebox, ttk

from src.history import load_transcriptions, save_transcription
from src.hotkey import RightShiftHotkey
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
        self._recording = False
        self._processing = False
        self._stop_recording = Event()
        self._recording_started_at = 0.0
        self._timer_job: str | None = None

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

        ttk.Label(
            frame,
            text="Hold Right Shift to record, then release to transcribe.",
        ).pack(anchor=tk.W)
        self.recording_time = ttk.Label(frame, text="Recording time: 0.00 seconds")
        self.recording_time.pack(anchor=tk.W, pady=(4, 12))

        self.hotkey = RightShiftHotkey(
            on_press=lambda: self.root.after(0, self.start_recording),
            on_release=lambda: self.root.after(0, self.stop_recording),
        )
        self.hotkey.start()
        root.protocol("WM_DELETE_WINDOW", self.close)

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
        if self._recording or self._processing:
            return

        self._recording = True
        self._processing = True
        self._stop_recording.clear()
        self._recording_started_at = time.perf_counter()
        self.status.configure(text="Recording...")
        self._update_recording_time()
        threading.Thread(
            target=self._record_and_transcribe,
            daemon=True,
        ).start()

    def stop_recording(self) -> None:
        if self._recording:
            self._recording = False
            self._stop_recording.set()

    def _update_recording_time(self) -> None:
        if not self._recording:
            return
        elapsed = time.perf_counter() - self._recording_started_at
        self.recording_time.configure(text=f"Recording time: {elapsed:.2f} seconds")
        self._timer_job = self.root.after(50, self._update_recording_time)

    def _record_and_transcribe(self) -> None:
        try:
            record_audio(self.audio_path, self._stop_recording)
            duration = time.perf_counter() - self._recording_started_at
            self._set_status("Transcribing with Groq...")
            transcription = transcribe_audio(self.audio_path, self.api_key)
            save_transcription(transcription)
        except Exception as error:
            self.root.after(0, self._show_error, str(error))
            return

        self.root.after(0, self._show_transcription, transcription, duration)

    def _set_status(self, text: str) -> None:
        self.root.after(0, self.status.configure, {"text": text})

    def _show_transcription(self, transcription: str, duration: float) -> None:
        self.refresh_history()
        self._processing = False
        self.recording_time.configure(text=f"Recording time: {duration:.2f} seconds")
        self.status.configure(text="Transcription complete.")
        if self.on_transcription:
            self.on_transcription(transcription)

    def _show_error(self, message: str) -> None:
        self._recording = False
        self._processing = False
        if self._timer_job is not None:
            self.root.after_cancel(self._timer_job)
            self._timer_job = None
        self.status.configure(text="Something went wrong.")
        messagebox.showerror("Cheapdictate error", message, parent=self.root)

    def close(self) -> None:
        self.hotkey.stop()
        self._stop_recording.set()
        if self._timer_job is not None:
            self.root.after_cancel(self._timer_job)
        self.root.destroy()
