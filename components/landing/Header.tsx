"use client";

import { useState } from "react";
import { Show, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";
import Link from "next/link";

const navLinks = [
  { label: "How It Works", href: "#how-it-works" },
  { label: "Features", href: "#product" },
  { label: "Pricing", href: "#pricing" },
  { label: "About", href: "#about" },
];

interface HeaderProps {
  readonly className?: string;
}

export default function Header({ className = "" }: HeaderProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className={`fixed top-0 right-0 left-0 z-50 border-b border-border/50 bg-brand-dark/75 backdrop-blur-xl ${className}`}>
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 md:px-12">
        <Link href="/" className="flex items-center gap-3 text-lg font-bold text-foreground">
          <span className="grid h-8 w-8 place-items-center rounded-md border border-brand-warm/40 bg-brand-warm/15 text-xs text-brand-warm">
            CV
          </span>
          <span>Convertale</span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-brand-warm"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <Show when="signed-out">
            <SignInButton mode="modal">
              <button className="text-sm font-medium text-foreground transition-colors hover:text-brand-warm">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="inline-flex items-center rounded-md bg-brand-warm px-5 py-2 text-sm font-semibold text-brand-ink transition-all hover:bg-brand-warm-light hover:shadow-lg hover:shadow-brand-warm/20">
                Start
              </button>
            </SignUpButton>
          </Show>
          <Show when="signed-in">
            <UserButton />
          </Show>
        </div>

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-md p-2 text-muted-foreground hover:text-foreground md:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-expanded={mobileOpen}
          aria-label="Toggle navigation"
        >
          <svg
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            {mobileOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5" />
            )}
          </svg>
        </button>
      </div>

      {mobileOpen && (
        <div className="border-t border-border/50 bg-brand-dark/95 backdrop-blur-xl md:hidden">
          <nav className="flex flex-col gap-1 px-6 py-4">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-brand-surface hover:text-brand-warm"
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <div className="mt-2 flex flex-col gap-2 border-t border-border/50 pt-4">
              <Show when="signed-out">
                <SignInButton mode="modal">
                  <button className="w-full rounded-md border border-border px-5 py-2.5 text-sm font-medium text-foreground transition-all hover:bg-brand-surface">
                    Sign In
                  </button>
                </SignInButton>
                <SignUpButton mode="modal">
                  <button className="w-full rounded-md bg-brand-warm px-5 py-2.5 text-sm font-semibold text-brand-ink transition-all hover:bg-brand-warm-light">
                    Start
                  </button>
                </SignUpButton>
              </Show>
              <Show when="signed-in">
                <div className="flex items-center gap-2 px-3 py-2">
                  <UserButton />
                  <span className="text-sm text-muted-foreground">Your account</span>
                </div>
              </Show>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
