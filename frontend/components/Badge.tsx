"use client";

import type { ReactNode } from "react";

type BadgeTone = "neutral" | "success" | "warning" | "danger";

export default function Badge({
  tone = "neutral",
  children,
}: {
  tone?: BadgeTone;
  children: ReactNode;
}) {
  const map: Record<BadgeTone, string> = {
    neutral: "bg-background/40 ring-1 ring-foreground/15 text-foreground",
    success: "bg-emerald-500/15 ring-1 ring-emerald-500/30 text-emerald-200",
    warning: "bg-amber-500/15 ring-1 ring-amber-500/30 text-amber-200",
    danger: "bg-rose-500/15 ring-1 ring-rose-500/30 text-rose-200",
  };

  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs ${map[tone]}`}>
      {children}
    </span>
  );
}

