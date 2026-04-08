"use client";

type InputProps = {
  value: string;
  onChange: (next: string) => void;
  placeholder?: string;
  disabled?: boolean;
  type?: "text" | "password" | "email";
};

export default function Input({
  value,
  onChange,
  placeholder,
  disabled,
  type = "text",
}: InputProps) {
  return (
    <input
      className="h-11 w-full rounded-xl bg-background/30 px-4 text-sm ring-1 ring-foreground/15 placeholder:text-foreground/50 focus:outline-none focus:ring-foreground/40 disabled:cursor-not-allowed disabled:opacity-60"
      value={value}
      type={type}
      placeholder={placeholder}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

