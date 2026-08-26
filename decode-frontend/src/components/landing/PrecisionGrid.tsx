export function PrecisionGrid() {
  const cells = [
    {
      num: "01",
      title: "Detect",
      subtitle: "Smart Vision",
      metric: "REGIONS FOUND: 6 / 6",
      icon: (
        <svg viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.6" />
          <path d="M2 12H6M18 12H22M12 2V6M12 18V22" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      )
    },
    {
      num: "02",
      title: "Extract",
      subtitle: "Intelligent OCR",
      metric: "FIELD VARIANCE: 1.2%",
      icon: (
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M4 7V5C4 3.9 4.9 3 6 3H18C19.1 3 20 3.9 20 5V7M9 21H15M12 3V21" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      )
    },
    {
      num: "03",
      title: "Structure",
      subtitle: "Organized Data",
      metric: "SCHEMA MATCH: 98%",
      icon: (
        <svg viewBox="0 0 24 24" fill="none">
          <rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.6" />
          <rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.6" />
          <rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.6" />
          <rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.6" />
        </svg>
      )
    },
    {
      num: "04",
      title: "Verify",
      subtitle: "Trusted Accuracy",
      metric: "FINAL RISK: LOW",
      icon: (
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 2L20 6V12C20 17 16.5 20.7 12 22C7.5 20.7 4 17 4 12V6L12 2Z" stroke="currentColor" strokeWidth="1.6" />
        </svg>
      )
    }
  ];

  return (
    <section id="precision" className="min-h-[100svh] flex flex-col justify-center py-24 lg:py-32">
      <div className="mx-auto w-full max-w-[1800px] px-6 sm:px-8 md:px-16">
        <div className="reveal mx-auto mb-20 lg:mb-28 max-w-[800px] text-center">
          <div className="flex items-center justify-center gap-3 font-mono text-[12px] lg:text-[13px] font-medium uppercase tracking-[0.16em] text-[var(--color-seal-blue)] before:inline-block before:h-px before:w-[22px] before:bg-[var(--color-seal-blue)]">
            INSPECTION STANDARD
          </div>
          <h2 className="mt-6 font-[family-name:var(--font-display)] text-[clamp(2.5rem,5vw,4rem)] font-medium leading-[1.1] tracking-[-0.01em]">
            Precision at<br />Every Stage.
          </h2>
          <p className="mt-6 text-[clamp(1.1rem,1.5vw,1.35rem)] text-[var(--color-graphite-soft)] max-w-[50ch] mx-auto leading-relaxed">
            Intelligent detection. Accurate extraction. Trusted results — verified at each checkpoint, not assumed at the end.
          </p>
        </div>

        <div className="reveal grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 lg:gap-8">
          {cells.map((cell, idx) => (
            <div 
              key={idx} 
              className="flex flex-col justify-between min-h-[320px] lg:min-h-[380px] bg-white p-8 lg:p-10 rounded-xl border border-[var(--color-paper-line)] shadow-[0_4px_24px_rgba(20,20,10,0.04)]"
            >
              <div>
                <div className="flex items-center justify-between mb-8">
                  <div className="h-[36px] w-[36px] text-[var(--color-seal-blue)]">
                    {cell.icon}
                  </div>
                  <div className="font-mono text-[13px] font-bold tracking-[0.08em] text-[var(--color-brass)]">{cell.num}</div>
                </div>
                <div className="text-[22px] font-bold text-[var(--color-graphite)]">{cell.title}</div>
                <div className="mt-2 text-[15px] text-[var(--color-graphite-soft)]">{cell.subtitle}</div>
              </div>
              
              <div className="mt-12 border-t-2 border-dashed border-[var(--color-paper-line)] pt-5 font-mono text-[13px] font-semibold text-[var(--color-seal-blue)] uppercase tracking-wide">
                {cell.metric}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
