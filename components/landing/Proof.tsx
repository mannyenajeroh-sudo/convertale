const personas = [
  {
    persona: "Independent creator",
    statement:
      "Launch a weekly animated or cinematic series without coordinating writers, editors, render operators, and publishing support.",
    signal: "1-person studio",
  },
  {
    persona: "Small studio team",
    statement:
      "Run parallel client concepts, keep each show's canon separate, and review finished packages instead of managing every asset by hand.",
    signal: "3-5 productions",
  },
  {
    persona: "Educator",
    statement:
      "Turn course concepts into episodic lessons with recurring characters, stable visual language, and reusable distribution assets.",
    signal: "Narrative courses",
  },
  {
    persona: "Brand team",
    statement:
      "Build serialized campaign worlds, generate channel-specific cuts, and feed performance signals back into the next episode.",
    signal: "Campaign engine",
  },
];

interface ProofProps {
  readonly className?: string;
}

export default function Proof({ className = "" }: ProofProps) {
  return (
    <section id="usecases" className={`relative py-24 md:py-32 ${className}`}>
      <div className="mx-auto max-w-7xl px-6 md:px-12">
        <div className="mb-16 grid gap-8 lg:grid-cols-[0.85fr_1fr] lg:items-end">
          <div>
            <p className="mb-3 inline-flex items-center rounded-full border border-brand-magenta/30 bg-brand-magenta/10 px-4 py-1.5 text-xs font-semibold uppercase text-brand-magenta-light">
              Use cases
            </p>
            <h2 className="mt-4 text-4xl font-bold text-foreground md:text-5xl">
              Built for teams with more ideas than production capacity.
            </h2>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[
              ["18+", "Agents"],
              ["1536", "Embedding dims"],
              ["100%", "Publish path"],
            ].map(([value, label]) => (
              <div key={label} className="rounded-lg border border-border/60 bg-brand-card p-4">
                <p className="text-2xl font-bold text-brand-warm">{value}</p>
                <p className="mt-1 text-xs uppercase text-muted-foreground">{label}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {personas.map((item) => (
            <div
              key={item.persona}
              className="relative overflow-hidden rounded-lg border border-border/60 bg-brand-card p-7 transition-all hover:border-brand-cyan/35 hover:shadow-xl hover:shadow-brand-cyan/10"
            >
              <div className="mb-6 flex items-center justify-between gap-4">
                <p className="text-sm font-bold uppercase text-foreground">{item.persona}</p>
                <span className="rounded-full border border-brand-cyan/30 bg-brand-cyan/10 px-3 py-1 text-xs font-semibold text-brand-cyan">
                  {item.signal}
                </span>
              </div>
              <p className="text-base leading-relaxed text-muted-foreground">{item.statement}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
