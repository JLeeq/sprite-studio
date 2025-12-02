type HybridIframeProps = {
  title: string;
};

export function HybridIframe({ title }: HybridIframeProps) {
  const gradioUrl =
    process.env.NEXT_PUBLIC_GRADIO_URL ?? "http://127.0.0.1:7860";

  return (
    <section className="glass-card p-6 flex flex-col gap-4">
      <div>
        <p className="text-sm uppercase tracking-wider text-[var(--enhanced-muted)]">
          Live Studio
        </p>
        <h2 className="text-2xl font-semibold text-[var(--enhanced-text)]">
          {title}
        </h2>
        <p className="text-sm text-[var(--enhanced-muted)]">
          Heavy interactions still run inside Gradio Blocks. This embed keeps the
          experience seamless while we incrementally port features.
        </p>
      </div>
      <div className="relative w-full overflow-hidden rounded-2xl border border-[var(--enhanced-border)] shadow-floating">
        <iframe
          src={gradioUrl}
          className="h-[720px] w-full border-0"
          loading="lazy"
          title="Gradio Studio"
        />
        <div className="absolute left-4 bottom-4 bg-white/90 backdrop-blur px-3 py-1 rounded-full text-xs font-medium text-[var(--enhanced-muted)]">
          Connected to {gradioUrl}
        </div>
      </div>
    </section>
  );
}

