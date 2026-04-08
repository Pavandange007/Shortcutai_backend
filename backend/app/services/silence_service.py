from __future__ import annotations

from typing import Iterable

from app.models.schemas import SilenceSegment, TimelineSegment, WordTiming


def _word_ends_with_punctuation(word_text: str) -> bool:
    text = word_text.strip()
    if not text:
        return False
    return text[-1] in {".", "?", "!", ":", ";", ","}


def compute_silence_segments(
    words: list[WordTiming],
    *,
    min_gap_ms: int = 1000,
    max_gap_ms: int = 7000,
    preserve_punctuation_pauses: bool = True,
) -> list[SilenceSegment]:
    """
    Detect "cuttable" silences from word-to-word timestamp gaps.

    Heuristics:
    - Only consider gaps >= `min_gap_ms`.
    - Don't remove very large gaps (`max_gap_ms`) to avoid destroying scene structure.
    - Optionally preserve gaps adjacent to punctuation to keep natural prosody.

    Args:
        words: Word timings with millisecond accuracy.
        min_gap_ms: Minimum silence duration to be considered.
        max_gap_ms: Maximum silence duration eligible for removal.
        preserve_punctuation_pauses: If True, gaps next to punctuation are preserved.

    Returns:
        A list of SilenceSegment ranges (start_ms/end_ms) representing gaps.
    """

    if len(words) < 2:
        return []

    silences: list[SilenceSegment] = []

    for i in range(len(words) - 1):
        left = words[i]
        right = words[i + 1]
        gap_ms = right.start_ms - left.end_ms
        if gap_ms < min_gap_ms:
            continue
        if gap_ms > max_gap_ms:
            continue

        if preserve_punctuation_pauses:
            if _word_ends_with_punctuation(left.text) or _word_ends_with_punctuation(right.text):
                continue

        silences.append(SilenceSegment(start_ms=left.end_ms, end_ms=right.start_ms))

    # Merge adjacent/overlapping silences into stable ranges.
    merged: list[SilenceSegment] = []
    for sil in silences:
        if not merged:
            merged.append(sil)
            continue
        last = merged[-1]
        if sil.start_ms <= last.end_ms:
            merged[-1] = SilenceSegment(start_ms=last.start_ms, end_ms=max(last.end_ms, sil.end_ms))
        else:
            merged.append(sil)

    return merged


def build_speech_timeline(
    words: list[WordTiming],
    silences: Iterable[SilenceSegment],
    *,
    min_speech_segment_ms: int = 250,
) -> list[TimelineSegment]:
    """
    Convert word timestamps + detected silences into a timeline containing
    speech segments and removed-silence segments.

    Args:
        words: Word timings.
        silences: Silence segments detected from words.
        min_speech_segment_ms: Drop speech segments that are too small to be useful.

    Returns:
        TimelineSegment list spanning from first word start to last word end.
    """

    if not words:
        return []

    sorted_silences = sorted(silences, key=lambda s: s.start_ms)

    timeline: list[TimelineSegment] = []
    speech_start_ms = words[0].start_ms
    speech_end_ms = words[-1].end_ms

    for sil in sorted_silences:
        if sil.start_ms > speech_start_ms:
            if sil.start_ms - speech_start_ms >= min_speech_segment_ms:
                timeline.append(
                    TimelineSegment(
                        start_ms=speech_start_ms,
                        end_ms=sil.start_ms,
                        keep_audio=True,
                    )
                )
        timeline.append(
            TimelineSegment(
                start_ms=sil.start_ms,
                end_ms=sil.end_ms,
                keep_audio=False,
            )
        )
        speech_start_ms = max(speech_start_ms, sil.end_ms)

    if speech_end_ms > speech_start_ms and speech_end_ms - speech_start_ms >= min_speech_segment_ms:
        timeline.append(
            TimelineSegment(
                start_ms=speech_start_ms,
                end_ms=speech_end_ms,
                keep_audio=True,
            )
        )

    # If silences made the timeline empty-ish, return an all-speech fallback.
    if not any(seg.keep_audio for seg in timeline):
        timeline = [
            TimelineSegment(start_ms=words[0].start_ms, end_ms=words[-1].end_ms, keep_audio=True)
        ]

    return timeline

