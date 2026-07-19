"use client";

const footerLinks = [
  { label: "How It Works", href: "#how-it-works" },
  { label: "Features", href: "#product" },
  { label: "About", href: "#about" },
  { label: "Pricing", href: "#pricing" },
];

export default function Footer() {
  return (
    <footer className="border-t border-border/50 bg-brand-card">
      <div className="mx-auto max-w-7xl px-6 py-16 md:px-12">
        <div className="flex flex-col gap-12 md:flex-row md:justify-between">
          <div className="max-w-sm">
            <p className="text-lg font-bold">
              Convertale
            </p>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
              Autonomous B2B short drama video ad creation, powered by Qwen + Wan.
            </p>
          </div>

          <nav className="flex flex-wrap gap-x-8 gap-y-3">
            {footerLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-brand-warm"
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>

        <div className="mt-12 border-t border-border/50 pt-8">
          <p className="text-xs text-muted-foreground">
            &copy; 2026 Convertale. Built for the Qwen Cloud Hackathon.
          </p>
        </div>
      </div>
    </footer>
  );
}
