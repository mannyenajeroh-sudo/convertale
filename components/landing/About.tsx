import Image from "next/image";

const architecture = [
  { label: "Reasoning", value: "Qwen" },
  { label: "Memory", value: "Neo4j" },
  { label: "Cloud", value: "Alibaba" },
  { label: "Connectors", value: "FastMCP" },
];

interface AboutProps {
  readonly className?: string;
}

export default function About({ className = "" }: AboutProps) {
  return (
    <section id="about" className={`relative overflow-hidden py-24 md:py-32 ${className}`}>
      <div className="absolute inset-0">
        <Image
          src="/images/landing/neo4j_graph.png"
          alt=""
          fill
          className="object-cover opacity-22"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-brand-dark/85 via-brand-dark/92 to-brand-dark" />
      </div>

      <div className="relative z-10 mx-auto grid max-w-7xl gap-12 px-6 md:px-12 lg:grid-cols-[0.9fr_1fr] lg:items-center">
        <div>
          <p className="mb-3 inline-flex items-center rounded-full border border-brand-cyan/30 bg-brand-cyan/10 px-4 py-1.5 text-xs font-semibold uppercase text-brand-cyan">
            Architecture
          </p>
          <h2 className="mt-4 text-4xl font-bold text-foreground md:text-5xl">
            Persistent memory for AI-native franchises.
          </h2>
          <div className="mt-8 space-y-5 text-lg leading-relaxed text-muted-foreground">
            <p>
              Convertale treats every campaign as a living production. Characters, locations, plot
              threads, facts, and world rules are stored as graph memory and grounded with Qwen
              embeddings so every new scene can check the canon before it ships.
            </p>
            <p>
              Agents operate through clear service boundaries: brand brief intake, writers room, storyboard,
              visual critic, video rendering, and Cliffhanger lead capture all leave auditable job records.
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-border/70 bg-brand-card/80 p-6 backdrop-blur-xl">
          <div className="mb-6 border-b border-border/60 pb-4">
            <p className="text-xs font-semibold uppercase text-muted-foreground">System stack</p>
            <p className="mt-2 text-2xl font-bold text-foreground">Production memory plane</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {architecture.map((stat) => (
              <div key={stat.label} className="rounded-md border border-border/60 bg-brand-dark/55 p-4">
                <p className="text-xs uppercase text-muted-foreground">{stat.label}</p>
                <p className="mt-2 text-2xl font-bold text-brand-warm">{stat.value}</p>
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-md border border-brand-cyan/25 bg-brand-cyan/10 p-4">
            <p className="text-sm leading-relaxed text-brand-cyan-light">
              Agents never call external platforms directly. Credentials stay behind the
              MCP registry while jobs remain observable inside Convertale.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
