export function HowItWorks() {
  return (
    <section id="how-it-works" className="min-h-[100svh] flex flex-col justify-center py-24 lg:py-32">
      <div className="mx-auto w-full max-w-[1800px] px-6 sm:px-8 md:px-16">
        <div className="reveal mx-auto mb-20 lg:mb-28 max-w-[800px] text-center">
          <div className="flex items-center justify-center gap-3 font-mono text-[12px] lg:text-[13px] font-medium uppercase tracking-[0.16em] text-[var(--color-seal-blue)] before:inline-block before:h-px before:w-[22px] before:bg-[var(--color-seal-blue)]">
            HOW VERIFICATION WORKS
          </div>
          <h2 className="mt-6 font-[family-name:var(--font-display)] text-[clamp(2.5rem,5vw,4rem)] font-medium leading-[1.1] tracking-[-0.01em]">
            From Locked Figure to<br />Certified Record.
          </h2>
          <p className="mt-6 text-[clamp(1.1rem,1.5vw,1.35rem)] text-[var(--color-graphite-soft)] max-w-[50ch] mx-auto leading-relaxed">
            Every chart is read, understood, and re-issued as structured data — nothing is guessed, everything is checked.
          </p>
        </div>

        <div className="reveal flex flex-col lg:flex-row items-center justify-center gap-16 lg:gap-24">
          {/* Card 1 */}
          <div className="flex-1 min-w-0 rounded-xl border border-[var(--color-paper-line)] bg-white p-[clamp(1.5rem,3vw,3rem)] shadow-[0_4px_24px_rgba(20,20,10,0.06)] w-full max-w-[600px]">
            <div className="mb-8 flex items-center gap-4">
              <div className="bg-[var(--color-paper)] p-3 rounded-lg border border-[var(--color-paper-line)]">
                <svg className="h-6 w-6 text-[var(--color-seal-blue)]" viewBox="0 0 24 24" fill="none">
                  <path d="M6 3H14L19 8V21H6V3Z" stroke="currentColor" strokeWidth="1.6" />
                </svg>
              </div>
              <div>
                <div className="text-[18px] font-semibold text-[var(--color-graphite)]">Research Figure</div>
                <div className="font-mono text-[12px] text-[var(--color-graphite-soft)] uppercase mt-1">SCANNED FROM SOURCE PDF</div>
              </div>
            </div>
            <div className="flex h-[220px] items-end gap-4 px-2 pt-4 border-b-2 border-dashed border-[var(--color-paper-line)] pb-2">
              <div className="flex-1 rounded-t-md bg-[#C9C4B4]" style={{ height: "60%" }} />
              <div className="flex-1 rounded-t-md bg-[#C9C4B4]" style={{ height: "40%" }} />
              <div className="flex-1 rounded-t-md bg-[#C9C4B4]" style={{ height: "85%" }} />
            </div>
          </div>

          {/* Engine */}
          <div className="flex shrink-0 flex-col items-center gap-5 my-8 lg:my-0">
            <div className="relative flex h-32 w-32 items-center justify-center rounded-full bg-[var(--color-ink)] shadow-[0_0_0_1px_rgba(216,190,142,0.35),0_20px_40px_-18px_rgba(11,30,51,0.5)] z-10">
              <svg className="h-[48px] w-[48px] text-[var(--color-brass-light)]" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5" />
                <path d="M8 12.5L10.5 15L16 9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
              <div className="animate-engineScan absolute left-[8%] right-[8%] top-[18%] h-[2px] bg-gradient-to-r from-transparent via-[var(--color-brass-light)] to-transparent" />
            </div>
            <div className="text-center font-mono text-[13px] font-semibold uppercase tracking-[0.1em] text-[var(--color-seal-blue)]">
              Verification<br />Engine
            </div>
          </div>

          {/* Card 2 */}
          <div className="flex-1 min-w-0 rounded-xl border border-[var(--color-paper-line)] bg-white p-[clamp(1.5rem,3vw,3rem)] shadow-[0_4px_24px_rgba(20,20,10,0.06)] w-full max-w-[600px]">
            <div className="mb-8 flex items-center gap-4">
              <div className="bg-[var(--color-paper)] p-3 rounded-lg border border-[var(--color-paper-line)]">
                <svg className="h-6 w-6 text-[var(--color-seal-blue)]" viewBox="0 0 24 24" fill="none">
                  <path d="M4 19V5M4 19H20M8 15V19M12 11V19M16 8V19" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                </svg>
              </div>
              <div>
                <div className="text-[18px] font-semibold text-[var(--color-graphite)]">Certified Record</div>
                <div className="font-mono text-[12px] text-[var(--color-graphite-soft)] uppercase mt-1">STRUCTURED &amp; EDITABLE</div>
              </div>
            </div>
            <div className="flex h-[220px] items-end gap-4 px-2 pt-4 border-b-2 border-solid border-[var(--color-graphite)] pb-2">
              <div className="flex-1 rounded-t-md bg-[var(--color-seal-blue)]" style={{ height: "60%" }} />
              <div className="flex-1 rounded-t-md bg-[#3C8FBF]" style={{ height: "40%" }} />
              <div className="flex-1 rounded-t-md bg-[var(--color-verified-green)]" style={{ height: "85%" }} />
            </div>
            <div className="mt-8 flex items-center justify-between border-t border-[var(--color-paper-line)] pt-6">
              <div className="flex items-center gap-3 font-mono text-[14px] font-bold text-[var(--color-verified-green)] uppercase tracking-wide">
                <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
                  <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
                  <path d="M8 12.5L10.5 15L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
                HIGH CONFIDENCE
              </div>
              <div className="text-right flex items-center gap-3">
                <div className="font-mono text-[11px] font-medium tracking-[0.1em] text-[var(--color-graphite-soft)] text-right leading-tight">CONF.<br />SCORE</div>
                <div className="font-mono text-[36px] font-bold text-[var(--color-verified-green)] leading-none">92</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
