import fitz

doc = fitz.open('static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf')
p = doc[0]
drawings = p.get_drawings()
# Filter filled rects in the chart area (excluding legend squares)
bars = []
for d in drawings:
    rect = d['rect']
    fill = d.get('fill')
    if fill and rect.height > 20 and rect.width > 15 and rect.width < 50:
        bars.append({'rect': rect, 'fill': fill, 'x': rect.x0, 'y': rect.y0, 'h': rect.height})

bars.sort(key=lambda b: b['x'])
print(f"Total vector bars found: {len(bars)}")
for b in bars:
    print(f"  Bar at x={b['x']:.1f}, h={b['h']:.1f}, fill={b['fill']}")
