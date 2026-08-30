import os

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

export_png_svg_funcs = """

  const exportPNG = async () => {
    if (!selectedChart) return;
    const url = `http://127.0.0.1:5000/api/v1/exports/${encodeURIComponent(selectedChart.id)}/png`;
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `decode-chart-${selectedChart.id}.png`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  };

  const exportSVG = async () => {
    if (!selectedChart) return;
    const url = `http://127.0.0.1:5000/api/v1/exports/${encodeURIComponent(selectedChart.id)}/svg`;
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `decode-chart-${selectedChart.id}.svg`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  };
"""

button_string = """                <button
                  onClick={
                    exportCSV
                  }
                  className="flex items-center gap-1.5 rounded-lg border border-white/[0.07] px-3 py-2 text-[11px] text-white/45 hover:text-white"
                >
                  <Download
                    size={13}
                  />
                  Export CSV
                </button>"""

export_buttons_ui = """                <button
                  onClick={
                    exportPNG
                  }
                  className="flex items-center gap-1.5 rounded-lg border border-white/[0.07] px-3 py-2 text-[11px] text-white/45 hover:text-white"
                >
                  <Download
                    size={13}
                  />
                  Export PNG
                </button>
                <button
                  onClick={
                    exportSVG
                  }
                  className="flex items-center gap-1.5 rounded-lg border border-white/[0.07] px-3 py-2 text-[11px] text-white/45 hover:text-white"
                >
                  <Download
                    size={13}
                  />
                  Export SVG
                </button>"""

import re
# Insert the functions right before `const copyConfig =`
text = re.sub(r'(const copyConfig =\s*\(\) => \{)', export_png_svg_funcs + r'\1', text)

# Insert the buttons right after the Export CSV button
text = text.replace(button_string, button_string + '\n\n' + export_buttons_ui)

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print('Export PNG and SVG added!')
