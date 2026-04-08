"use client";

import { getApiBaseUrl } from "@/lib/api-client";

export default function VideoPreview({
  roughCutUrl,
  title = "Rough Cut",
}: {
  roughCutUrl?: string;
  title?: string;
}) {
  const videoSrc =
    roughCutUrl && roughCutUrl.startsWith("http")
      ? roughCutUrl
      : roughCutUrl
        ? `${getApiBaseUrl()}${roughCutUrl}`
        : undefined;

  return (
    <section className="rounded-3xl bg-background/10 p-4 ring-1 ring-foreground/10">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold">{title}</h2>
        <span className="text-xs text-foreground/60">
          {roughCutUrl ? "Ready" : "Preview will appear after export"}
        </span>
      </div>

      {videoSrc ? (
        <video
          controls
          src={videoSrc}
          className="w-full rounded-2xl ring-1 ring-foreground/10"
        />
      ) : (
        <div className="flex min-h-[220px] items-center justify-center rounded-2xl border border-foreground/10 bg-background/20 p-6 text-sm text-foreground/60">
          No video yet.
        </div>
      )}
    </section>
  );
}

