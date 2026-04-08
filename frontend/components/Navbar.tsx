import Link from "next/link";

export default function Navbar() {
  return (
    <header className="w-full border-b border-foreground/10 bg-background/20">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/upload" className="text-sm font-semibold tracking-wide">
          Shotcut AI
        </Link>

        <nav className="flex items-center gap-4 text-sm">
          <Link href="/upload" className="text-foreground/70 hover:text-foreground">
            Editor
          </Link>
        </nav>
      </div>
    </header>
  );
}

