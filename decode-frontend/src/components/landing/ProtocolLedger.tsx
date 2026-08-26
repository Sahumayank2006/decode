export function ProtocolLedger() {
  const articles = [
    { num: "I.", name: "INGEST", desc: "Document received, paginated, and rendered for analysis." },
    { num: "II.", name: "DETECT", desc: "Every chart, table, and diagram located as its own region." },
    { num: "III.", name: "EXTRACT", desc: "Values, axes, legends, and labels recovered with confidence scoring." },
    { num: "IV.", name: "RECONSTRUCT", desc: "Rebuilt as an editable, restylable, interactive chart." },
    { num: "V.", name: "COMPLY", desc: "Similarity, color, and layout risk assessed against the source." },
    { num: "VI.", name: "EXPORT", desc: "Certified record released as SVG, PNG, or structured data." },
  ];

  return (
    <section id="protocol" className="bg-[var(--color-ink)] text-[var(--color-paper)] min-h-[100svh] flex flex-col justify-center py-24 lg:py-32">
      <div className="mx-auto w-full max-w-[1800px] px-6 sm:px-8 md:px-16">
        <div className="reveal mx-auto mb-20 lg:mb-28 max-w-[800px] text-center">
          <div className="flex items-center justify-center gap-3 font-mono text-[12px] lg:text-[13px] font-medium uppercase tracking-[0.16em] text-[var(--color-brass-light)] before:inline-block before:h-px before:w-[22px] before:bg-[var(--color-brass-light)]">
            THE PROTOCOL
          </div>
          <h2 className="mt-6 font-[family-name:var(--font-display)] text-[clamp(2.5rem,5vw,4rem)] font-medium leading-[1.1] tracking-[-0.01em] text-[var(--color-paper)]">
            Six Articles.<br />One Chain of Custody.
          </h2>
          <p className="mt-6 text-[clamp(1.1rem,1.5vw,1.35rem)] text-[rgba(247,244,236,0.6)] max-w-[50ch] mx-auto leading-relaxed">
            Every document passes through the same recorded sequence — nothing is skipped, nothing is unaccounted for.
          </p>
        </div>

        <div className="reveal mx-auto w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12 lg:gap-16 border-t border-[rgba(216,190,142,0.28)] pt-16">
          {articles.map((article, idx) => (
            <div 
              key={idx} 
              className="flex flex-col gap-6 rounded-xl border border-[rgba(216,190,142,0.16)] p-8 transition-colors duration-300 hover:bg-[rgba(216,190,142,0.04)]"
            >
              <div className="flex items-start justify-between">
                <div className="font-[family-name:var(--font-display)] text-[36px] lg:text-[42px] italic text-[var(--color-brass-light)] leading-none">
                  {article.num}
                </div>
                <div className="shrink-0 rounded-full border border-[rgba(47,111,78,0.5)] px-3 py-1.5 font-mono text-[10px] lg:text-[11px] font-bold tracking-[0.1em] text-[var(--color-verified-green)] whitespace-nowrap bg-[rgba(47,111,78,0.1)]">
                  RECORDED
                </div>
              </div>
              <div className="flex-1 mt-4">
                <div className="font-mono text-[22px] font-semibold tracking-[0.05em] text-[var(--color-paper)]">{article.name}</div>
                <div className="mt-4 text-[15px] leading-[1.6] text-[rgba(247,244,236,0.6)]">{article.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
