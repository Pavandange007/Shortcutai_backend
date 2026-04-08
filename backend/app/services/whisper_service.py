from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Final

from app.core.config import settings
from app.models.schemas import TranscriptResponse, WordTiming

logger = logging.getLogger(__name__)

_MODEL_LOCK: Final[threading.Lock] = threading.Lock()
_MODEL = None


def _get_model():
    """
    Lazily load the faster-whisper model once per process.

    Returns:
        WhisperModel: The loaded model instance.
    """

    global _MODEL
    if _MODEL is not None:
        return _MODEL

    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL

        # Local import keeps scaffold usable even if the dependency isn't installed.
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except ModuleNotFoundError as e:
            raise RuntimeError(
                "faster-whisper is not installed. Install backend requirements first."
            ) from e

        device = settings.gpu_device
        compute_type = "float16"

        # CPU-only machines can't use float16 compute reliably.
        if device == "cpu":
            compute_type = "int8"
        elif device.startswith("cuda"):
            try:
                import torch  # type: ignore

                if not torch.cuda.is_available():
                    device = "cpu"
                    compute_type = "int8"
            except Exception:
                device = "cpu"
                compute_type = "int8"

        logger.info(
            "whisper: loading model %r device=%s compute_type=%s (first run may download GBs from Hugging Face)",
            settings.whisper_model_name,
            device,
            compute_type,
        )
        t0 = time.perf_counter()
        _MODEL = WhisperModel(
            settings.whisper_model_name,
            device=device,
            compute_type=compute_type,
        )
        logger.info(
            "whisper: model ready in %.1fs",
            time.perf_counter() - t0,
        )
        return _MODEL


def transcribe_with_word_timestamps(video_path: Path) -> TranscriptResponse:
    """
    Transcribe a video into word-level timestamps.

    Args:
        video_path: Path to an input video file.

    Returns:
        TranscriptResponse containing word timings in milliseconds.
    """

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    model = _get_model()

    try:
        size_mb = video_path.stat().st_size / (1024 * 1024)
        logger.info(
            "whisper: transcribing %s (%.1f MiB) — on CPU this can take several minutes",
            video_path.name,
            size_mb,
        )
        t0 = time.perf_counter()
        segments, info = model.transcribe(
            str(video_path),
            word_timestamps=True,
            vad_filter=True,
        )
        duration_s = getattr(info, "duration", None)
        if duration_s is not None:
            logger.info(
                "whisper: audio duration ~%.1fs; decoding/segmenting (progress logs every 15 segments)",
                float(duration_s),
            )
    except Exception as e:
        # fast-whisper can fail when FFmpeg can't decode the file.
        raise RuntimeError(f"Transcription failed: {e}") from e

    words: list[WordTiming] = []
    raw_parts: list[str] = []

    for segment_index, segment in enumerate(segments):
        if getattr(segment, "text", None):
            raw_parts.append(segment.text)

        if segment_index > 0 and segment_index % 15 == 0:
            logger.info(
                "whisper: still transcribing… segment_index=%d elapsed=%.0fs",
                segment_index,
                time.perf_counter() - t0,
            )

        segment_words = getattr(segment, "words", None) or []
        for w in segment_words:
            start_ms = int(round(float(w.start) * 1000))
            end_ms = int(round(float(w.end) * 1000))
            confidence = getattr(w, "probability", None)

            words.append(
                WordTiming(
                    text=str(getattr(w, "word", "")).strip(),
                    start_ms=start_ms,
                    end_ms=end_ms,
                    confidence=float(confidence) if confidence is not None else None,
                    segment_index=segment_index,
                )
            )

    raw_text = " ".join(raw_parts).strip()
    logger.info(
        "whisper: done %d words in %.1fs",
        len(words),
        time.perf_counter() - t0,
    )
    return TranscriptResponse(words=words, raw_text=raw_text)

