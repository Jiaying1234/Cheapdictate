import threading
import time
import tkinter as tk
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from threading import Event
from tkinter import messagebox, ttk

from src.history import Transcription, load_transcriptions, save_transcription
from src.hotkey import RightShiftHotkey
from src.paster import paste_text
from src.recorder import record_audio
from src.transcriber import transcribe_audio
from src.usage_tracker import (
    audio_time_left,
    format_audio_time,
    record_usage,
    total_words_today,
    word_count,
)


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
        self.usage_info = ttk.Label(frame)
        self.usage_info.pack(anchor=tk.W, pady=(4, 0))

        self.hotkey = RightShiftHotkey(
            on_press=lambda: self.root.after(0, self.start_recording),
            on_release=lambda: self.root.after(0, self.stop_recording),
        )
        self.hotkey.start()
        root.protocol("WM_DELETE_WINDOW", self.close)

        history_header = ttk.Frame(frame)
        history_header.pack(fill=tk.X, pady=(18, 4))
        ttk.Label(history_header, text="Latest transcriptions").pack(side=tk.LEFT)
        self.daily_words = tk.Label(
            history_header,
            justify=tk.CENTER,
            padx=8,
            pady=3,
            relief=tk.GROOVE,
            borderwidth=1,
            text="Today\n0 words",
        )
        self.daily_words.pack(side=tk.RIGHT)

        history_frame = ttk.Frame(frame)
        history_frame.pack(fill=tk.BOTH, expand=True)

        self.history_canvas = tk.Canvas(
            history_frame, borderwidth=0, highlightthickness=0
        )
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(
            history_frame, orient=tk.VERTICAL, command=self.history_canvas.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        self.history_content = ttk.Frame(self.history_canvas)
        self.history_window = self.history_canvas.create_window(
            (0, 0), window=self.history_content, anchor=tk.NW
        )
        self.history_content.bind(
            "<Configure>",
            lambda _event: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")
            ),
        )
        self.history_canvas.bind("<Configure>", self._resize_history)
        self.history_text_labels: list[tk.Label] = []
        self.refresh_history()
        self.refresh_usage()

    def refresh_history(self) -> None:
        for child in self.history_content.winfo_children():
            child.destroy()
        self.history_text_labels = []
        transcriptions = load_transcriptions()
        for index, transcription in enumerate(transcriptions):
            row = ttk.Frame(self.history_content, padding=(4, 7))
            row.pack(fill=tk.X)
            time_label = ttk.Label(row, text=self._format_time(transcription))
            time_label.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 12))
            text_label = tk.Label(
                row,
                text=transcription["text"],
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=420,
                background=self.history_canvas.cget("background"),
                borderwidth=0,
            )
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.history_text_labels.append(text_label)
            if index < len(transcriptions) - 1:
                ttk.Separator(self.history_content, orient=tk.HORIZONTAL).pack(
                    fill=tk.X
                )
        self._resize_history()

    def _resize_history(self, _event: tk.Event | None = None) -> None:
        width = self.history_canvas.winfo_width()
        self.history_canvas.itemconfigure(self.history_window, width=width)
        wraplength = max(120, width - 110)
        for label in self.history_text_labels:
            label.configure(wraplength=wraplength)

    @staticmethod
    def _format_time(transcription: Transcription) -> str:
        if not transcription["timestamp"]:
            return "--"
        timestamp = datetime.fromisoformat(transcription["timestamp"])
        return timestamp.strftime("%I:%M%p").lstrip("0").lower()

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
            remaining_seconds = record_usage(
                duration, words=word_count(transcription)
            )
            paste_text(transcription)
        except Exception as error:
            self.root.after(0, self._show_error, str(error))
            return

        self.root.after(
            0,
            self._show_transcription,
            transcription,
            duration,
            remaining_seconds,
        )

    def _set_status(self, text: str) -> None:
        self.root.after(0, self.status.configure, {"text": text})

    def refresh_usage(self) -> None:
        remaining_seconds = audio_time_left()
        self.usage_info.configure(
            text=f"Audio time left today: {format_audio_time(remaining_seconds)}"
        )
        self.daily_words.configure(text=f"Today\n{total_words_today():,} words")

    def _show_transcription(
        self, transcription: str, duration: float, remaining_seconds: int
    ) -> None:
        self.refresh_history()
        self._processing = False
        self.recording_time.configure(text=f"Recording time: {duration:.2f} seconds")
        self.usage_info.configure(
            text=f"Audio time left today: {format_audio_time(remaining_seconds)}"
        )
        self.daily_words.configure(text=f"Today\n{total_words_today():,} words")
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
