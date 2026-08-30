import re

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Update type ChartMode
text = re.sub(r'type ChartMode =([^;]+);', r'type ChartMode =\1\n  | "original"\n  | "table";', text, count=1)

# Update CHART_MODES array
text = re.sub(r'(const CHART_MODES: ChartMode\[\] = \[[^\]]+)(\];)', r'\1\n  "original",\n\2', text, count=1)

# Add render logic to renderChart
new_render_logic = '''
      if (chartMode === "original" || chartMode === "table") {
        const src = selectedChart?.source?.original_image_base64
          ? `data:image/png;base64,${selectedChart.source.original_image_base64}`
          : selectedChart?.source?.original_image_path
          ? `http://127.0.0.1:5000/api/v1/static/${selectedChart.source.original_image_path}`
          : null;

        if (src) {
          return (
            <div className="flex h-full w-full items-center justify-center p-4">
              <img src={src} className="max-h-full max-w-full object-contain rounded-lg shadow-sm" alt="Original extracted element" />
            </div>
          );
        } else {
          return (
            <div className="flex h-full items-center justify-center text-white/50">
              No original preview available
            </div>
          );
        }
      }
'''

render_start = r'(const renderChart =\s*\(\) => \{\s*if \(\s*!selectedChart \|\|[\s\S]*?return \([\s\S]*?\);\s*\})'
match = re.search(render_start, text)
if match:
    block = match.group(1)
    text = text.replace(block, block + '\n' + new_render_logic)
    with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Successfully patched DemoWorkspace.tsx')
else:
    print('Failed to find renderChart start block')
