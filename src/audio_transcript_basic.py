

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from pydub import AudioSegment, effects, silence
from faster_whisper import WhisperModel


SUPPORTED_AUDIO = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}


def prepare_audio(
    input_path: Path,
    output_dir: Path,
    trim_silence: bool = True,
    min_silence_len: int = 500,
    silence_thresh_offset: int = 16,
) -> Path:
    
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")

    if input_path.suffix.lower() not in SUPPORTED_AUDIO:
        raise ValueError(
            f"Unsupported file type: {input_path.suffix}. "
            f"Supported: {', '.join(sorted(SUPPORTED_AUDIO))}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    audio = AudioSegment.from_file(input_path)

    
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16_000)
    audio = effects.normalize(audio)

    if trim_silence:
        threshold = audio.dBFS - silence_thresh_offset
        chunks = silence.split_on_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=threshold,
            keep_silence=200,
        )
        if chunks:
            audio = sum(chunks, AudioSegment.empty())

    wav_path = output_dir / f"{input_path.stem}_prepared.wav"
    audio.export(wav_path, format="wav")
    return wav_path


def transcribe_audio(
    wav_path: Path,
    model_size: str = "tiny",
    language: Optional[str] = None,
    beam_size: int = 5,
) -> tuple[str, list[dict]]:
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe(
        str(wav_path),
        language=language,
        beam_size=beam_size,
        vad_filter=True,
    )

    transcript_segments = []
    text_parts = []

    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue

        transcript_segments.append(
            {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": text,
            }
        )
        text_parts.append(text)

    transcript = " ".join(text_parts).strip()

    detected_language = getattr(info, "language", None)
    if detected_language:
        print(f"Detected language: {detected_language}")

    return transcript, transcript_segments


def save_transcript(
    input_path: Path,
    output_dir: Path,
    transcript: str,
    segments: list[dict],
) -> Path:
    
    output_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = output_dir / f"{input_path.stem}_transcript.txt"

    lines = ["TRANSCRIPT", "==========", transcript, "", "SEGMENTS", "========"]

    for segment in segments:
        lines.append(
            f"[{segment['start']:>6.2f}s - {segment['end']:>6.2f}s] {segment['text']}"
        )

    transcript_path.write_text("\n".join(lines), encoding="utf-8")
    return transcript_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Basic audio transcription utility.")
    parser.add_argument("audio_file", type=Path, help="Path to input audio file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("transcripts"),
        help="Folder for prepared audio and transcript output.",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Optional language code, e.g. es, en, da, hu. Leave empty for auto-detect.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="tiny",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size. tiny is fastest; larger models are more accurate.",
    )
    parser.add_argument(
        "--no-trim",
        action="store_true",
        help="Disable simple silence trimming before transcription.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    prepared_audio = prepare_audio(
        input_path=args.audio_file,
        output_dir=args.output_dir,
        trim_silence=not args.no_trim,
    )

    transcript, segments = transcribe_audio(
        wav_path=prepared_audio,
        model_size=args.model,
        language=args.language,
    )

    transcript_path = save_transcript(
        input_path=args.audio_file,
        output_dir=args.output_dir,
        transcript=transcript,
        segments=segments,
    )

    print(f"Prepared audio: {prepared_audio}")
    print(f"Transcript saved: {transcript_path}")


if __name__ == "__main__":
    main()
