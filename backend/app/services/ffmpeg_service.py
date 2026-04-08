from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from app.models.schemas import CaptionLine


def ms_to_ass_time(ms: int) -> str:
    """
    Convert milliseconds to ASS timestamp (H:MM:SS.CS).

    Args:
        ms: Milliseconds.

    Returns:
        ASS timestamp string.
    """

    ms = max(0, int(ms))
    centiseconds = int(round(ms / 10.0))
    hours = centiseconds // 360000
    centiseconds %= 360000
    minutes = centiseconds // 6000
    centiseconds %= 6000
    seconds = centiseconds // 100
    cs = centiseconds % 100
    return f"{hours}:{minutes:02d}:{seconds:02d}.{cs:02d}"


def _escape_ass_text(text: str) -> str:
    # Minimal escaping to avoid override tags breaking rendering.
    return (
        text.replace("\\", "\\\\")
        .replace("{", "")
        .replace("}", "")
        .replace("\n", r"\N")
    )


def burn_in_captions(
    video_path: Path,
    captions: list[CaptionLine],
    output_path: Path,
    *,
    font_name: str = "Arial",
    font_size: int = 48,
) -> None:
    """
    Burn captions into the video using FFmpeg + ASS subtitles.

    Args:
        video_path: Input video file.
        captions: Caption lines with word-accurate timestamps.
        output_path: Output MP4 file path.
        font_name: Font used by ASS.
        font_size: Font size in ASS points.
    """

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    ass_lines: list[str] = []
    ass_lines.append("[Script Info]")
    ass_lines.append("ScriptType: v4.00+")
    ass_lines.append("PlayResX: 1920")
    ass_lines.append("PlayResY: 1080")
    ass_lines.append("WrapStyle: 0")
    ass_lines.append("")
    ass_lines.append("[V4+ Styles]")
    ass_lines.append(
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
    )
    # PrimaryColour is &HAABBGGRR (ASS). We'll use white text with a subtle shadow.
    ass_lines.append(
        f"Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,0,2,20,20,60,1"
    )
    ass_lines.append("")
    ass_lines.append("[Events]")
    ass_lines.append(
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    )

    for line in captions:
        start = ms_to_ass_time(line.start_ms)
        end = ms_to_ass_time(line.end_ms)
        text = _escape_ass_text(line.text)
        ass_lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    ass_text = "\n".join(ass_lines)

    # Use a temp file because FFmpeg expects a real path.
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".ass",
        delete=False,
    ) as f:
        ass_path = Path(f.name)
        f.write(ass_text)

    try:
        ass_path_str = str(ass_path).replace("\\", "/")
        video_path_str = str(video_path).replace("\\", "/")
        output_path_str = str(output_path).replace("\\", "/")

        if not shutil_which("ffmpeg"):
            raise FileNotFoundError("FFmpeg executable not found in PATH.")

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path_str,
            "-vf",
            f"subtitles={ass_path_str}",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "veryfast",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            output_path_str,
        ]

        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    finally:
        try:
            os.remove(ass_path)
        except OSError:
            pass


def shutil_which(cmd: str) -> bool:
    """
    Lightweight `shutil.which` wrapper (keeps imports local). Returns bool.
    """

    import shutil

    return shutil.which(cmd) is not None


def export_rough_cut(
    video_path: Path,
    keep_segments: list[tuple[int, int]],
    output_path: Path,
    *,
    crossfade_ms: int = 150,
) -> None:
    """
    Export a rough cut by stitching timeline keep segments.

    - Video: concatenated back-to-back.
    - Audio: optional crossfade via `acrossfade` between keep segments.

    Note:
        Video and audio are not frame-overlapped; audio length may be
        slightly shorter when crossfading. Crossfade duration is expected
        to be small (e.g., 100-200ms) for MVP.
    """

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not keep_segments:
        raise ValueError("keep_segments must not be empty.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    seg_count = len(keep_segments)
    crossfade_s = max(0.0, crossfade_ms / 1000.0)

    # Build a filter graph that trims each keep segment, then concatenates video
    # and mixes audio with optional crossfades.
    filters: list[str] = []
    for idx, (start_ms, end_ms) in enumerate(keep_segments):
        start_s = start_ms / 1000.0
        end_s = end_ms / 1000.0
        filters.append(
            f"[0:v]trim=start={start_s}:end={end_s},setpts=PTS-STARTPTS[v{idx}]"
        )
        filters.append(
            f"[0:a]atrim=start={start_s}:end={end_s},asetpts=PTS-STARTPTS[a{idx}]"
        )

    # Video concat
    v_inputs = "".join(f"[v{i}]" for i in range(seg_count))
    filters.append(
        f"{v_inputs}concat=n={seg_count}:v=1:a=0[vout]"
    )

    # Audio concat or acrossfade
    if seg_count == 1 or crossfade_s <= 0.0:
        a_inputs = "".join(f"[a{i}]" for i in range(seg_count))
        filters.append(
            f"{a_inputs}concat=n={seg_count}:v=0:a=1[aout]"
        )
    else:
        # Chain acrossfades: af1 combines a0+a1, af2 combines af1+a2, etc.
        filters.append(
            f"[a0][a1]acrossfade=d={crossfade_s}:c1=tri:c2=tri[af1]"
        )
        for i in range(2, seg_count):
            filters.append(
                f"[af{i-1}][a{i}]acrossfade=d={crossfade_s}:c1=tri:c2=tri[af{i}]"
            )
        filters.append(f"[af{seg_count-1}]anull[aout]")

    filter_complex = ";".join(filters)

    if not shutil_which("ffmpeg"):
        raise FileNotFoundError("FFmpeg executable not found in PATH.")

    video_path_str = str(video_path).replace("\\", "/")
    output_path_str = str(output_path).replace("\\", "/")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path_str,
        "-filter_complex",
        filter_complex,
        "-map",
        "[vout]",
        "-map",
        "[aout]",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "veryfast",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        output_path_str,
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

