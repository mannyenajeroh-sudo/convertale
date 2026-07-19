const tiers = [
  {
    name: "Backlot",
    price: "Free",
    description: "For testing and learning",
    features: ["Limited projects", "Lower render minutes", "Community support"],
    cta: "Start Free",
    highlighted: false,
  },
  {
    name: "Creator",
    price: "$39/mo",
    description: "For independent creators",
    features: ["Unlimited projects", "Render minute quota", "Priority support"],
    cta: "Subscribe",
    highlighted: true,
  },
  {
    name: "Studio",
    price: "$149/mo",
    description: "For teams and professionals",
    features: ["Multiple concurrent productions", "Higher quotas", "Team seats"],
    cta: "Subscribe",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For large organizations",
    features: ["Custom quotas", "Dedicated support", "White-label options"],
    cta: "Contact Sales",
    highlighted: false,
  },
];

export default function Pricing() {
  return (
    <section id="pricing" className="relative py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-6 md:px-12">
        <div className="mb-16 max-w-3xl">
          <p className="mb-3 text-center">
            <span className="inline-flex items-center rounded-full border border-brand-warm/30 bg-brand-warm/10 px-4 py-1.5 text-xs font-semibold uppercase text-brand-warm">
              Pricing
            </span>
          </p>
          <h2 className="mt-4 text-center text-4xl font-bold tracking-tight text-foreground md:text-5xl">
            Plans for every stage
            <br />
            <span className="text-muted-foreground">of production</span>
          </h2>
          <p className="mt-6 text-center text-lg text-muted-foreground">
            Start free, scale as your franchise grows.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className={`group relative flex flex-col overflow-hidden rounded-lg border p-8 transition-all ${
                tier.highlighted
                  ? "border-brand-warm/45 bg-gradient-to-br from-brand-card to-brand-surface/50 shadow-xl shadow-brand-warm/10"
                  : "border-border/50 bg-brand-card hover:border-brand-cyan/30"
              }`}
            >
              {tier.highlighted && (
                <div className="absolute inset-0 bg-gradient-to-br from-brand-warm/5 to-transparent" />
              )}
              <div className="relative flex flex-1 flex-col">
                <p className="text-sm font-bold uppercase tracking-wider text-foreground">
                  {tier.name}
                </p>
                <p className="mt-3 text-4xl font-bold text-foreground">{tier.price}</p>
                <p className="mt-2 text-sm text-muted-foreground">{tier.description}</p>

                <ul className="mt-8 flex-1 space-y-4">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm text-muted-foreground">
                      <svg
                      className="mt-0.5 h-5 w-5 flex-shrink-0 text-brand-green"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={2}
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>

                <a
                  href="#access"
                  className={`mt-8 inline-flex items-center justify-center rounded-md px-6 py-3 text-sm font-semibold transition-all ${
                    tier.highlighted
                      ? "bg-brand-warm text-brand-ink hover:bg-brand-warm-light hover:shadow-lg hover:shadow-brand-warm/20"
                      : "border border-border text-foreground hover:border-brand-cyan hover:text-brand-cyan"
                  }`}
                >
                  {tier.cta}
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
