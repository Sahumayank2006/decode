import re

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Find where exportCSV ends.
match = re.search(r'(const exportCSV =[\s\S]*?URL\.revokeObjectURL\(url\);\s*\};)', text)
if match:
    export_csv_block = match.group(1)
    
    new_exports = '''
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
'''
    text = text.replace(export_csv_block, export_csv_block + '\n' + new_exports)

    # Now we need to add the buttons in the UI.
    ui_buttons_match = re.search(r'(<button\s*onClick=\{\s*exportCSV\s*\}[^>]*>[\s\S]*?</button>)', text)
    if ui_buttons_match:
        export_csv_button = ui_buttons_match.group(1)
        
        new_buttons = '''
                <button
                  onClick={exportPNG}
                  className="flex items-center gap-1.5 rounded-lg border border-white/[0.07] px-3 py-2 text-[11px] text-white/45 hover:text-white"
                >
                  <Download size={13} />
                  Export PNG
                </button>
                <button
                  onClick={exportSVG}
                  className="flex items-center gap-1.5 rounded-lg border border-white/[0.07] px-3 py-2 text-[11px] text-white/45 hover:text-white"
                >
                  <Download size={13} />
                  Export SVG
                </button>
'''
        text = text.replace(export_csv_button, export_csv_button + '\n' + new_buttons)
        with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'w', encoding='utf-8') as f:
            f.write(text)
        print('Export buttons added successfully!')
    else:
        print('Could not find exportCSV button in UI!')
else:
    print('Could not find exportCSV function!')
