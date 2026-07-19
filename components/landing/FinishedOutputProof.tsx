"use client";

import Image from "next/image";
import { useRef } from "react";

const publishedProjects = [
  {
    title: "Neon Harbor: Pilot",
    description:
      "A serialized cyber-noir episode package with trailer, shorts, thumbnail, and launch metadata.",
    youtubeUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    thumbnail: "/images/landing/finished_output.png",
    format: "Episode",
    badges: ["Pilot", "Trailer", "Shorts"],
  },
  {
    title: "Lagos 2095: Case File",
    description:
      "A continuity-checked detective concept generated from a single premise and production brief.",
    youtubeUrl: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
    thumbnail: "/images/landing/publishing.png",
    format: "Franchise proof",
    badges: ["World bible", "Episode cut", "SEO"],
  },
  {
    title: "Orbit Classroom",
    description:
      "An educational micro-series with recurring characters, lesson arcs, and channel-ready clips.",
    youtubeUrl: "https://www.youtube.com/watch?v=9bZkp7q19f0",
    thumbnail: "/images/landing/production.png",
    format: "Course series",
    badges: ["Lessons", "Voice", "Captions"],
  },
  {
    title: "Launch Week Stories",
    description:
      "A brand campaign package with episodic cuts, social shorts, thumbnails, and publish records.",
    youtubeUrl: "https://www.youtube.com/watch?v=3JZ_D3ELwOQ",
    thumbnail: "/images/landing/hero-control-room.png",
    format: "Campaign",
    badges: ["Brand", "Social", "Analytics"],
  },
];

interface FinishedOutputProofProps {
  readonly className?: string;
}

export default function FinishedOutputProof({ className = "" }: FinishedOutputProofProps) {
  const carouselRef = useRef<HTMLDivElement>(null);

  const scrollByCard = (direction: "previous" | "next") => {
    const carousel = carouselRef.current;

    if (!carousel) {
      return;
    }

    const cardWidth = carousel.querySelector("article")?.clientWidth ?? 360;
    carousel.scrollBy({
      left: direction === "next" ? cardWidth + 24 : -(cardWidth + 24),
      behavior: "smooth",
    });
  };

  return (
    <section id="FinishedOutputProof" className={`relative overflow-hidden py-24 md:py-32 ${className}`}>
      <div className="absolute inset-0">
        <Image
          src="/images/landing/finished_output.png"
          alt=""
          fill
          className="object-cover opacity-20"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-brand-dark/85 via-brand-dark/92 to-brand-dark" />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl px-6 md:px-12">
        <div className="mb-10 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="mb-3 inline-flex items-center rounded-full border border-brand-warm/30 bg-brand-warm/10 px-4 py-1.5 text-xs font-semibold uppercase text-brand-warm">
              Finished output proof
            </p>
            <h2 className="text-4xl font-bold text-foreground md:text-5xl">
              Public projects that show the platform output.
            </h2>
            <p className="mt-5 text-lg leading-relaxed text-muted-foreground">
              Use this carousel for published YouTube episodes, trailers, shorts, and campaign
              packages produced through Showrunner.
            </p>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              className="grid h-11 w-11 place-items-center rounded-md border border-border bg-brand-card text-foreground transition-colors hover:border-brand-warm hover:text-brand-warm"
              onClick={() => scrollByCard("previous")}
              aria-label="Show previous project"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
              </svg>
            </button>
            <button
              type="button"
              className="grid h-11 w-11 place-items-center rounded-md border border-border bg-brand-card text-foreground transition-colors hover:border-brand-warm hover:text-brand-warm"
              onClick={() => scrollByCard("next")}
              aria-label="Show next project"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
              </svg>
            </button>
          </div>
        </div>

        <div
          ref={carouselRef}
          className="flex snap-x snap-mandatory gap-6 overflow-x-auto pb-4 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          aria-label="Published public project carousel"
        >
          {publishedProjects.map((project) => (
            <article
              key={project.title}
              className="min-w-[82%] snap-start overflow-hidden rounded-lg border border-border/70 bg-brand-card/90 shadow-2xl shadow-brand-dark/50 backdrop-blur-xl sm:min-w-[430px] lg:min-w-[500px]"
            >
              <a href={project.youtubeUrl} target="_blank" rel="noreferrer" className="group block">
                <div className="relative aspect-video overflow-hidden">
                  <Image
                    src={project.thumbnail}
                    alt=""
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                    sizes="(min-width: 1024px) 500px, 82vw"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-brand-dark via-brand-dark/20 to-transparent" />
                  <div className="absolute left-4 top-4 rounded-full border border-brand-cyan/30 bg-brand-cyan/15 px-3 py-1 text-xs font-semibold text-brand-cyan-light backdrop-blur-md">
                    {project.format}
                  </div>
                  <div className="absolute bottom-4 left-4 grid h-12 w-12 place-items-center rounded-full bg-brand-warm text-brand-ink shadow-lg shadow-brand-warm/20">
                    <svg className="h-5 w-5 translate-x-0.5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                      <path d="M6.5 4.8v10.4L15 10 6.5 4.8Z" />
                    </svg>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-2xl font-bold text-foreground">{project.title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                    {project.description}
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    {project.badges.map((badge) => (
                      <span
                        key={badge}
                        className="rounded-full border border-border/70 bg-brand-surface px-3 py-1 text-xs font-medium text-muted-foreground"
                      >
                        {badge}
                      </span>
                    ))}
                  </div>
                </div>
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
