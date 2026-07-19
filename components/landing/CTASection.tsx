import Image from "next/image";
import { Show, SignInButton, SignUpButton } from "@clerk/nextjs";
import Link from "next/link";

export default function CTASection() {
  return (
    <section id="access" className="relative overflow-hidden py-24 md:py-32">
      <div className="absolute inset-0">
        <Image
          src="/images/landing/cta-clapperboard.png"
          alt=""
          fill
          className="object-cover"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-brand-dark/60 via-brand-dark/70 to-brand-dark" />
      </div>

      <div className="relative z-10 mx-auto max-w-4xl px-6 text-center md:px-12">
        <h2 className="text-4xl font-bold tracking-tight text-foreground md:text-6xl">
          Ready to run your
          <br />
          next franchise?
        </h2>
        <p className="mt-6 text-lg text-muted-foreground md:text-xl">
          Start with a premise. Leave with an auditable production pipeline, finished media, and a
          distribution package.
        </p>
        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Show when="signed-out">
            <SignUpButton mode="modal">
              <button className="group inline-flex items-center justify-center rounded-md bg-brand-warm px-10 py-4 text-lg font-semibold text-brand-ink transition-all hover:bg-brand-warm-light hover:shadow-xl hover:shadow-brand-warm/20">
                Start Free
                <svg className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
                </svg>
              </button>
            </SignUpButton>
            <SignInButton mode="modal">
              <button className="inline-flex items-center justify-center rounded-md border border-border bg-brand-surface/50 px-10 py-4 text-lg font-semibold text-foreground backdrop-blur-sm transition-all hover:border-brand-cyan/50 hover:bg-brand-surface">
                Sign In
              </button>
            </SignInButton>
          </Show>
          <Show when="signed-in">
            <Link
              href="/dashboard"
              className="group inline-flex items-center justify-center rounded-md bg-brand-warm px-10 py-4 text-lg font-semibold text-brand-ink transition-all hover:bg-brand-warm-light hover:shadow-xl hover:shadow-brand-warm/20"
            >
              Go to Dashboard
              <svg className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </Link>
          </Show>
        </div>
      </div>
    </section>
  );
}
