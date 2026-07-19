import Image from "next/image";

const steps = [
  {
    number: "01",
    title: "Concept lock",
    owner: "Executive Producer",
    description:
      "Capture the premise, audience, tone, season shape, episode targets, and production constraints.",
    output: "Series brief",
  },
  {
    number: "02",
    title: "World build",
    owner: "Show Bible",
    description:
      "Create the canon: characters, locations, plot threads, visual style, facts, and world rules.",
    output: "Memory graph",
  },
  {
    number: "03",
    title: "Episode plan",
    owner: "Writers' room",
    description:
      "Break each episode into beats, scenes, dialogue, storyboards, shots, and generation prompts.",
    output: "Shot list",
  },
  {
    number: "04",
    title: "Render pass",
    owner: "Production crew",
    description:
      "Fan out Wan/HappyHorse video jobs while voice, score, and assembly agents run in parallel.",
    output: "Episode cut",
  },
  {
    number: "05",
    title: "Publish package",
    owner: "Distribution",
    description:
      "Score quality, check continuity, create trailers and shorts, then prepare SEO and upload records.",
    output: "Live franchise",
  },
];

interface HowItWorksProps {
  readonly className?: string;
}

export default function HowItWorks({ className = "" }: HowItWorksProps) {
  return (
    <section id="how-it-works" className={`relative overflow-hidden py-24 md:py-32 ${className}`}>
      <div className="absolute inset-0">
        <Image
          src="/images/landing/pipeline-studio.png"
          alt=""
          fill
          className="object-cover opacity-35"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-brand-dark/75 via-brand-dark/90 to-brand-dark" />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl px-6 md:px-12">
        <div className="mb-16 grid gap-8 lg:grid-cols-[0.95fr_0.8fr] lg:items-end">
          <div>
            <p className="mb-3 inline-flex items-center rounded-full border border-brand-warm/30 bg-brand-warm/10 px-4 py-1.5 text-xs font-semibold uppercase text-brand-warm">
              Updated production workflow
            </p>
            <h2 className="mt-4 text-4xl font-bold text-foreground md:text-5xl">
              Every episode moves through one auditable production line.
            </h2>
          </div>
          <p className="text-lg leading-relaxed text-muted-foreground">
            The workflow mirrors a real studio: development, writers&apos; room, production, post,
            continuity review, and publishing. Agent jobs leave a visible trail at every stage.
          </p>
        </div>

        <div className="rounded-lg border border-border/70 bg-brand-card/80 backdrop-blur-xl">
          <div className="grid border-b border-border/70 px-5 py-4 text-xs font-semibold uppercase text-muted-foreground md:grid-cols-[120px_1fr_150px]">
            <span>Stage</span>
            <span className="hidden md:block">Workstream</span>
            <span className="hidden md:block">Output</span>
          </div>
          {steps.map((step) => (
            <div
              key={step.number}
              className="grid gap-4 border-b border-border/50 px-5 py-5 last:border-b-0 md:grid-cols-[120px_1fr_150px] md:items-center"
            >
              <div className="flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-md border border-brand-cyan/40 bg-brand-cyan/10 text-sm font-bold text-brand-cyan">
                  {step.number}
                </span>
                <span className="text-xs font-semibold uppercase text-muted-foreground md:hidden">
                  {step.output}
                </span>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-brand-warm">{step.owner}</p>
                <h3 className="mt-1 text-xl font-bold text-foreground">{step.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {step.description}
                </p>
              </div>
              <div className="hidden md:block">
                <span className="rounded-md border border-brand-warm/30 bg-brand-warm/10 px-3 py-2 text-sm font-semibold text-brand-warm">
                  {step.output}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
