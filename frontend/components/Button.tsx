"use client";

import type { ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost";

export default function Button({
  variant = "primary",
  disabled,
  children,
  onClick,
  type = "button",
}: {
  variant?: ButtonVariant;
  disabled?: boolean;
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
}) {
  const base =
    "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";

  const styles: Record<ButtonVariant, string> = {
    primary:
      "bg-foreground text-background hover:opacity-90 focus:ring-foreground",
    secondary:
      "bg-background/30 text-foreground ring-1 ring-foreground/20 hover:bg-background/50 focus:ring-foreground/70",
    ghost: "text-foreground hover:bg-background/40 focus:ring-foreground/70",
  };

  return (
    <button
      type={type}
      className={`${base} ${styles[variant]} ${disabled ? "opacity-60 cursor-not-allowed" : ""}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

