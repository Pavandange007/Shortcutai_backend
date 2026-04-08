"use client";

import type { JobStepKey, StepState } from "../lib/types";

const stepOrder: JobStepKey[] = [
  "silence_removal",
  "best_take",
  "captions",
  "export",
];

const stepLabels: Record<JobStepKey, string> = {
  silence_removal: "Intelligent Silence Removal",
  best_take: "Retake Analyzer (Best Take)",
  captions: "Frame-Perfect Captions",
  export: "Timeline Export (Rough Cut)",
};

function stateToTone(state: StepState): "neutral" | "success" | "warning" | "danger" {
  if (state === "done") return "success";
  if (state === "running") return "warning";
  if (state === "failed") return "danger";
  return "neutral";
}

function stateToDot(state: StepState): string {
  if (state === "done") return "bg-emerald-400";
  if (state === "running") return "bg-amber-400";
  if (state === "failed") return "bg-rose-400";
  return "bg-foreground/30";
}

export default function JobProgress({
  statusByStep,
}: {
  statusByStep: Partial<Record<JobStepKey, StepState>>;
}) {
  return (
    <ol className="flex flex-col gap-3">
      {stepOrder.map((key, idx) => {
        const state = statusByStep[key] ?? "pending";
        const isLast = idx === stepOrder.length - 1;
        const tone = stateToTone(state);

        return (
          <li key={key} className="flex items-start gap-3">
            <div className="relative mt-1 flex h-6 w-6 shrink-0 items-center justify-center">
              <span className={`h-2.5 w-2.5 rounded-full ${stateToDot(state)}`} />
              {!isLast ? (
                <span
                  className="absolute left-1/2 top-6 h-9 -translate-x-1/2 border-l border-foreground/10"
                  aria-hidden="true"
                />
              ) : null}
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-semibold">
                  {stepLabels[key]}
                </span>
                <span
                  className={[
                    "inline-flex items-center rounded-full px-2.5 py-1 text-xs ring-1 ring-foreground/15",
                    tone === "success" ? "bg-emerald-500/15 text-emerald-200 ring-emerald-500/30" : "",
                    tone === "warning" ? "bg-amber-500/15 text-amber-200 ring-amber-500/30" : "",
                    tone === "danger" ? "bg-rose-500/15 text-rose-200 ring-rose-500/30" : "",
                    tone === "neutral" ? "bg-foreground/10 text-foreground/70 ring-foreground/15" : "",
                  ].join(" ")}
                >
                  {state === "pending"
                    ? "Pending"
                    : state === "running"
                      ? "Running"
                      : state === "done"
                        ? "Done"
                        : "Failed"}
                </span>
              </div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

