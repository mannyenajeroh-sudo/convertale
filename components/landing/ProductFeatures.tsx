import Image from "next/image";

const features = [
  {
    title: "Creative foundation",
    description:
      "Executive Producer, Show Bible, World, Character, and Story agents turn a raw idea into a consistent franchise foundation.",
    metric: "01",
    image: "/images/landing/plot.png",
  },
  {
    title: "Production orchestration",
    description:
      "Storyboard, cinematography, prompt engineering, video generation, TTS, score, and assembly run as one coordinated pipeline.",
    metric: "18+",
    image: "/images/landing/production.png",
  },
  {
    title: "Distribution package",
    description:
      "Episodes ship with trailers, shorts, thumbnails, SEO metadata, publish records, and analytics feedback into show memory.",
    metric: "06",
    image: "/images/landing/publishing.png",
  },
];

interface ProductFeaturesProps {
  readonly className?: string;
}

export default function ProductFeatures({ className = "" }: ProductFeaturesProps) {
  return (
    <section id="product" className={`relative py-24 md:py-32 ${className}`}>
      <div className="mx-auto max-w-7xl px-6 md:px-12">
        <div className="mb-16 grid gap-8 lg:grid-cols-[0.9fr_1fr] lg:items-end">
          <div>
            <p className="mb-3 inline-flex items-center rounded-full border border-brand-cyan/30 bg-brand-cyan/10 px-4 py-1.5 text-xs font-semibold uppercase text-brand-cyan">
              Product
            </p>
            <h2 className="mt-4 text-4xl font-bold text-foreground md:text-5xl">
              A production operating system, not a clip generator.
            </h2>
          </div>
          <p className="text-lg leading-relaxed text-muted-foreground">
            The product surface is built around the real work: locking story memory, directing
            generated shots, checking continuity, assembling finished episodes, and publishing
            distribution assets from one controlled workflow.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group relative overflow-hidden rounded-lg border border-border/60 bg-brand-card transition-all hover:border-brand-warm/40 hover:shadow-xl hover:shadow-brand-warm/10"
            >
              <div className="relative aspect-[16/10] overflow-hidden">
                <Image
                  src={feature.image}
                  alt=""
                  fill
                  className="object-cover transition-transform duration-500 group-hover:scale-105"
                  sizes="(min-width: 1024px) 33vw, 100vw"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-brand-dark via-brand-dark/30 to-transparent" />
                <div className="absolute bottom-4 left-4 rounded-md border border-brand-warm/35 bg-brand-dark/70 px-3 py-2 backdrop-blur-md">
                  <p className="text-2xl font-bold text-brand-warm">{feature.metric}</p>
                </div>
              </div>
              <div className="p-6">
                <h3 className="mb-3 text-xl font-bold text-foreground">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
