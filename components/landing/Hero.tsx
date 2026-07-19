import Image from "next/image";

const proofChips = [
  "7-agent pipeline",
  "Character continuity across episodes",
  "Wan video generation",
  "Cliffhanger lead capture",
];

const liveStages = [
  { label: "Brand Brief Intake", status: "Done", tone: "text-brand-green" },
  { label: "Writers Room", status: "Active", tone: "text-brand-warm" },
  { label: "Cinematographer", status: "Queued", tone: "text-brand-cyan" },
  { label: "Visual Critic", status: "Standby", tone: "text-brand-magenta-light" },
];

interface HeroProps {
  readonly className?: string;
}

export default function Hero({ className = "" }: HeroProps) {
  return (
    <section className={`relative flex min-h-[92vh] items-center overflow-hidden pt-16 ${className}`}>
      <div className="absolute inset-0">
        <Image
          src="/images/landing/production.png"
          alt=""
          fill
          className="object-cover object-center"
          priority
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-brand-dark/20 via-brand-dark/55 to-brand-dark" />
        <div className="absolute inset-0 bg-gradient-to-r from-brand-dark/90 via-brand-dark/50 to-brand-dark/10" />
      </div>

      <div className="relative z-10 mx-auto grid w-full max-w-7xl gap-12 px-6 py-20 md:px-12 md:py-28 lg:grid-cols-[minmax(0,0.95fr)_minmax(360px,0.65fr)] lg:items-end">
        <div className="max-w-4xl">
          <p className="mb-4 inline-flex items-center rounded-full border border-brand-warm/35 bg-brand-warm/10 px-4 py-1.5 text-xs font-semibold uppercase text-brand-warm">
            B2B Short Drama Lead Generation
          </p>

          <h1 className="mt-6 text-5xl font-bold leading-[1.04] text-foreground sm:text-6xl md:text-7xl lg:text-8xl">
            One brief.
            <br />
            A complete drama campaign.
          </h1>

          <p className="mt-8 max-w-2xl text-lg leading-relaxed text-muted-foreground md:text-xl">
            Convertale turns a brand brief into scripted short drama episodes with a locked protagonist,
            Qwen-VL visual continuity critic, Wan-rendered shots, and a Cliffhanger gate that
            converts viewers into verified leads — automatically.
          </p>

          <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-center">
            <a
              href="#access"
              className="group inline-flex items-center justify-center rounded-md bg-brand-warm px-8 py-4 text-base font-semibold text-brand-ink transition-all hover:bg-brand-warm-light hover:shadow-xl hover:shadow-brand-warm/20"
            >
              Start a campaign
              <svg className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </a>
            <a
              href="#how-it-works"
              className="inline-flex items-center justify-center rounded-md border border-border bg-brand-surface/60 px-8 py-4 text-base font-semibold text-foreground backdrop-blur-sm transition-all hover:border-brand-cyan/50 hover:bg-brand-surface"
            >
              View workflow
            </a>
          </div>

          <div className="mt-12 flex flex-wrap gap-3">
            {proofChips.map((chip) => (
              <span
                key={chip}
                className="rounded-full border border-border/50 bg-brand-surface/70 px-4 py-2 text-sm font-medium text-muted-foreground backdrop-blur-sm"
              >
                {chip}
              </span>
            ))}
          </div>
        </div>

        <div className="hidden rounded-lg border border-border/70 bg-brand-card/75 p-4 shadow-2xl shadow-brand-dark/70 backdrop-blur-xl lg:block">
          <div className="mb-4 flex items-center justify-between border-b border-border/60 pb-3">
            <div>
              <p className="text-xs uppercase text-muted-foreground">Campaign board</p>
              <p className="mt-1 text-sm font-semibold text-foreground">Cold Brew — Morning Rush</p>
            </div>
            <span className="rounded-full bg-brand-green/15 px-3 py-1 text-xs font-semibold text-brand-green">
              Live
            </span>
          </div>
          <div className="space-y-3">
            {liveStages.map((stage) => (
              <div key={stage.label} className="grid grid-cols-[1fr_auto] items-center gap-4 rounded-md border border-border/50 bg-brand-dark/55 px-4 py-3">
                <span className="text-sm font-medium text-foreground">{stage.label}</span>
                <span className={`text-xs font-semibold ${stage.tone}`}>{stage.status}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 grid grid-cols-3 gap-3 text-center">
            {[
              ["3", "Episodes"],
              ["12", "Shots"],
              ["94", "Leads"],
            ].map(([value, label]) => (
              <div key={label} className="rounded-md border border-border/50 bg-brand-surface/60 p-3">
                <p className="text-xl font-bold text-brand-warm">{value}</p>
                <p className="mt-1 text-xs text-muted-foreground">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
