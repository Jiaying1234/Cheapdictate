# Cheapdictate

Hold a key, speak, release. Your words are transcribed by AI and typed
into whatever box you're using.

## Who it's for
People who think faster than they type and don't want to pay for a
dictation subscription.

## Problem
- Speaking is much faster than typing, and talking through thoughts
  often sparks new ideas.
- Wispr Flow does this, but costs $12/month. Its free plan allows only
  2,000 words/week, while an hour of continuous talking is roughly
  7,800 to 9,000 words.

## Solution
A dictation tool built on free cloud AI APIs. Groq offers Whisper Large V3 turbo
with a free limit of 28,800 audio seconds/day (about 8 hours of recording
per day).

For a dictation tool, Whisper Large v3 Turbo is the clear winner because it directly solves the biggest technical hurdle of interactive dictation: latency.
When users speak, they expect words to appear on the screen almost instantly. Large v3 Turbo’s 4-layer decoder architecture allows it to generate text 4× to 5× faster than the original Large v3, drastically reducing the time between the end of a spoken sentence and the finalized text output.

Catch: Groq bills every request as a minimum of 10 seconds, so every
short clips waste quota. I can consider displaying the recorded time then.

## V1 (what's in)
- Hold a chosen key to record, release to transcribe
- Groq API does the transcription
- Transcription shown in the app's own window
- Transcription automatically pasted into the active typing box
  (search bar, ChatGPT, etc.)
- Shows word count of each transcription and audio time left today
- Setting to change the hold-to-record key

## NOT in V1 (maybe V2)
- Second AI call to clean up text and add punctuation
- Mac/Linux support, other languages, offline mode

## Milestones
- **M1: Groq connected.** Send a sample audio file, get text back in the terminal. **Done.**
- **M2: Microphone recording.** Record from the mic and save a short clip. **Done.**
- **M3: Transcribe my own voice.** Record, then transcribe, then print. **Done.**
- **M4: Simple interface.** A window that displays the transcription output. **Done.**
- **M5: Hold-to-record key.** Hold right Shift to record, release to transcribe,
  and show the recording time to two decimal places. **Done.**
- **M6: Auto-paste.** Transcription is pasted into the active text box. **Done.**
- **M7: Usage details.** Interface shows word count and audio time left today. Each request counts as max(audio seconds, 10), matching Groq’s billing (verified on the Usage page).
- **M8: Key setting.** User can change the hold-to-record key.

## Run M5

From the project directory, set `GROQ_API_KEY` in `.env` using `.env.example` as
a template, then run:

```powershell
.\venv\Scripts\python.exe main.py
```

The app opens a window. Hold **right Shift** to record from the default
microphone, then release it to save the clip as `audio\recording.wav`, send it
to Groq's `whisper-large-v3-turbo` model, paste the transcription into the
currently focused text box, and show the transcription. The recording time is
shown to two decimal places. The latest 10 transcriptions are saved in
`data\transcriptions.json`; older entries are automatically removed.

The audio file is currently saved. Every recording overwrites the same
`audio\recording.wav` file, so only the most recent audio clip is kept. Audio
files are ignored by Git and are not uploaded to the repository.
