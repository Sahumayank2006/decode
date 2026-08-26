export function ComplySection() {
  return (
    <section id="comply" className="border-y border-[var(--color-paper-line)] bg-gradient-to-b from-[var(--color-paper)] to-[var(--color-paper-dim)] min-h-[100svh] flex flex-col justify-center py-24 lg:py-32 overflow-hidden">
      <div className="mx-auto w-full max-w-[1800px] px-6 sm:px-8 md:px-16 flex flex-col items-center gap-16 lg:gap-32 text-center lg:flex-row lg:text-left">
        {/* Left Content */}
        <div className="reveal flex-1 w-full max-w-[600px] lg:max-w-none">
          <div className="flex items-center justify-center lg:justify-start gap-3 font-mono text-[12px] lg:text-[13px] font-medium uppercase tracking-[0.16em] text-[var(--color-seal-blue)] before:inline-block before:h-px before:w-[22px] before:bg-[var(--color-seal-blue)]">
            RESPONSIBLE · VERIFIED · TRUSTED
          </div>
          <h2 className="mt-6 font-[family-name:var(--font-display)] text-[clamp(3.5rem,6vw,5.5rem)] font-medium leading-[1.05] tracking-[-0.02em]">
            Comply.
          </h2>
          <p className="mx-auto lg:mx-0 mt-8 max-w-[50ch] text-[clamp(1.1rem,1.5vw,1.35rem)] text-[var(--color-graphite-soft)] leading-relaxed">
            Every reconstruction is evaluated for responsible academic reuse before it ever leaves the protocol.
          </p>

          <div className="mt-12 flex flex-col sm:flex-row flex-wrap justify-center lg:justify-start gap-8 lg:gap-12">
            <div className="flex items-center">
              <div className="bg-[rgba(47,111,78,0.1)] p-2 rounded-full mr-4">
                <svg className="h-[20px] w-[20px] text-[var(--color-verified-green)]" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
                </svg>
              </div>
              <div>
                <div className="text-[16px] font-semibold leading-tight text-[var(--color-graphite)]">Similarity</div>
                <div className="font-mono text-[12px] font-medium text-[var(--color-graphite-soft)] uppercase mt-1">CHECKED</div>
              </div>
            </div>
            <div className="flex items-center">
              <div className="bg-[rgba(47,111,78,0.1)] p-2 rounded-full mr-4">
                <svg className="h-[20px] w-[20px] text-[var(--color-verified-green)]" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
                </svg>
              </div>
              <div>
                <div className="text-[16px] font-semibold leading-tight text-[var(--color-graphite)]">Integrity</div>
                <div className="font-mono text-[12px] font-medium text-[var(--color-graphite-soft)] uppercase mt-1">VERIFIED</div>
              </div>
            </div>
            <div className="flex items-center">
              <div className="bg-[rgba(47,111,78,0.1)] p-2 rounded-full mr-4">
                <svg className="h-[20px] w-[20px] text-[var(--color-verified-green)]" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L20 6V12C20 17 16.5 20.7 12 22C7.5 20.7 4 17 4 12V6L12 2Z" stroke="currentColor" strokeWidth="2" />
                </svg>
              </div>
              <div>
                <div className="text-[16px] font-semibold leading-tight text-[var(--color-graphite)]">Risk</div>
                <div className="font-mono text-[12px] font-medium text-[var(--color-graphite-soft)] uppercase mt-1">MINIMIZED</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Seal Visual */}
        <div className="reveal flex-[0_0_auto] w-full max-w-[400px] lg:max-w-[450px]">
          <div className="relative mx-auto w-[clamp(240px,35vw,380px)] aspect-square">
            <svg className="h-full w-full -rotate-90" viewBox="0 0 260 260">
              <circle cx="130" cy="130" r="120" fill="none" stroke="var(--color-paper-line)" strokeWidth="4" />
              <circle 
                className="animate-ringFill"
                cx="130" cy="130" r="120" 
                fill="none" stroke="var(--color-verified-green)" strokeWidth="4" strokeLinecap="round" 
                strokeDasharray="754" strokeDashoffset="754" 
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className="font-mono text-[clamp(60px,8vw,80px)] font-semibold text-[var(--color-ink)] leading-none">92</div>
              <div className="mt-2 font-mono text-[clamp(12px,1.5vw,14px)] font-bold tracking-[0.15em] text-[var(--color-verified-green)] uppercase">
                SAFE TO USE
              </div>
              <svg className="mt-4 h-6 w-6 text-[var(--color-verified-green)]" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L20 6V12C20 17 16.5 20.7 12 22C7.5 20.7 4 17 4 12V6L12 2Z" stroke="currentColor" strokeWidth="2" />
              </svg>
            </div>
          </div>
          
          <div className="mt-12 text-left font-mono text-[12px] lg:text-[13px] text-[var(--color-graphite-soft)]">
            <div className="mx-auto flex w-full max-w-[340px] justify-between gap-8 border-b-2 border-dashed border-[var(--color-paper-line)] py-3 uppercase">
              <span>STRUCTURAL SIMILARITY</span>
              <span className="font-semibold text-[var(--color-verified-green)]">98%</span>
            </div>
            <div className="mx-auto flex w-full max-w-[340px] justify-between gap-8 border-b-2 border-dashed border-[var(--color-paper-line)] py-3 uppercase">
              <span>CHROMATIC OVERLAP</span>
              <span className="font-semibold text-[var(--color-verified-green)]">95%</span>
            </div>
            <div className="mx-auto flex w-full max-w-[340px] justify-between gap-8 border-b-2 border-dashed border-[var(--color-paper-line)] py-3 uppercase">
              <span>LAYOUT RISK</span>
              <span className="font-semibold text-[var(--color-verified-green)]">LOW</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
