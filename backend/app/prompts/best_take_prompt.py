from __future__ import annotations

from typing import Sequence


SYSTEM_PROMPT = """You are a professional video editor and line producer.
You will be given multiple transcript takes for the same scene.

Task: Select the single best take (highest overall quality) based on:
- Energy & delivery (engagement, confidence, momentum)
- Clarity & pacing (easy to follow, correct emphasis, minimal awkward pauses)
- Fewest mistakes (filler words, stumbles, self-corrections, obvious errors)

Output rules:
- Return STRICT JSON only (no markdown, no extra text).
- JSON schema:
  {
    "best_index": number,
    "explanation": string
  }
- best_index must be an integer referencing the provided take index (0..N-1).
"""


def build_best_take_prompt(takes: Sequence[str]) -> str:
    lines = [SYSTEM_PROMPT, "", "Transcript takes:"]
    for idx, take in enumerate(takes):
        lines.append(f"- Take {idx}: {take}")

    lines.append(
        ""
        "Choose the best take index. If there is a tie, prefer the take with fewer mistakes."
    )
    return "\n".join(lines)

