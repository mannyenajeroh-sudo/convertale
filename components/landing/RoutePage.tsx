import Image from "next/image";
import Link from "next/link";

interface RoutePageFeature {
  readonly title: string;
  readonly description: string;
}

interface RoutePageProps {
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly image: string;
  readonly features: readonly RoutePageFeature[];
  readonly ctaLabel?: string;
}

export default function RoutePage({
  eyebrow,
  title,
  description,
  image,
  features,
  ctaLabel = "Start a production",
}: RoutePageProps) {
  return (
    <main className="min-h-screen bg-brand-dark pt-16">
      <section className="relative overflow-hidden py-24 md:py-32">
        <div className="absolute inset-0">
          <Image src={image} alt="" fill className="object-cover opacity-35" sizes="100vw" />
          <div className="absolute inset-0 bg-gradient-to-r from-brand-dark via-brand-dark/85 to-brand-dark/45" />
          <div className="absolute inset-0 bg-gradient-to-b from-brand-dark/40 via-transparent to-brand-dark" />
        </div>

        <div className="relative z-10 mx-auto grid max-w-7xl gap-12 px-6 md:px-12 lg:grid-cols-[0.95fr_0.75fr] lg:items-end">
          <div>
            <p className="mb-4 inline-flex rounded-full border border-brand-warm/30 bg-brand-warm/10 px-4 py-1.5 text-xs font-semibold uppercase text-brand-warm">
              {eyebrow}
            </p>
            <h1 className="max-w-4xl text-5xl font-bold leading-[1.05] text-foreground md:text-7xl">
              {title}
            </h1>
            <p className="mt-8 max-w-2xl text-lg leading-relaxed text-muted-foreground md:text-xl">
              {description}
            </p>
            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Link
                href="/#access"
                className="inline-flex items-center justify-center rounded-md bg-brand-warm px-8 py-4 text-base font-semibold text-brand-ink transition-colors hover:bg-brand-warm-light"
              >
                {ctaLabel}
              </Link>
              <Link
                href="/showcase"
                className="inline-flex items-center justify-center rounded-md border border-border bg-brand-surface/70 px-8 py-4 text-base font-semibold text-foreground transition-colors hover:border-brand-cyan hover:text-brand-cyan"
              >
                View showcase
              </Link>
            </div>
          </div>

          <div className="rounded-lg border border-border/70 bg-brand-card/80 p-5 backdrop-blur-xl">
            <div className="mb-4 border-b border-border/60 pb-4">
              <p className="text-xs font-semibold uppercase text-muted-foreground">Screen modules</p>
              <p className="mt-2 text-xl font-bold text-foreground">{eyebrow}</p>
            </div>
            <div className="space-y-3">
              {features.map((feature, index) => (
                <div key={feature.title} className="rounded-md border border-border/60 bg-brand-dark/55 p-4">
                  <div className="mb-2 flex items-center gap-3">
                    <span className="grid h-8 w-8 place-items-center rounded-md border border-brand-cyan/35 bg-brand-cyan/10 text-xs font-bold text-brand-cyan">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <h2 className="text-base font-bold text-foreground">{feature.title}</h2>
                  </div>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
