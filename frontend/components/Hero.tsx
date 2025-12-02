type HeroProps = {
  title: string;
  tagline: string;
  description: string;
};

export function Hero({ title, tagline, description }: HeroProps) {
  return (
    <section className="glass-card px-8 py-10 shadow-floating">
      <p className="text-sm uppercase tracking-[0.3em] text-[var(--enhanced-muted)]">
        {tagline}
      </p>
      <h1 className="mt-4 text-4xl font-semibold text-[var(--enhanced-text)]">
        {title}
      </h1>
      <p className="mt-4 max-w-3xl text-lg text-[var(--enhanced-muted)]">
        {description}
      </p>
    </section>
  );
}

